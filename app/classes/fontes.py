import os
import re
import numpy as np
from bdfparser import Font

class Fontes:
    # Where the bundled u8g2 BDF fonts live. Resolved once so that every
    # lookup can be checked against it.
    FONT_DIR = os.path.realpath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "src",
            "olikraus_u8g2_master_tools-font_bdf",
        )
    )

    @classmethod
    def _resolve_font_path(cls, font_name):
        """
        Map a font name to a path inside FONT_DIR, or refuse it.

        The name reaches here from submitted code, and it used to be
        interpolated straight into a path. setFont("u8g2_font_../../../x_t")
        therefore escaped the font directory and opened an arbitrary file. The
        contents were never returned, so this was blind, but it was still a
        read primitive pointed at the filesystem.

        Two checks rather than one: reject anything that looks like a path,
        then confirm the resolved location really is under FONT_DIR. The first
        gives a clear refusal, the second is what actually holds if some
        platform quirk slips past it.
        """
        if not font_name:
            raise Exception("Fonte não implementada")

        if (
            os.sep in font_name
            or (os.altsep and os.altsep in font_name)
            or '/' in font_name
            or '\\' in font_name
            or os.pardir in font_name
            or ':' in font_name          # Windows drive or stream separator
            or font_name.startswith('.')
        ):
            raise Exception("Fonte não implementada")

        caminho = os.path.realpath(
            os.path.join(cls.FONT_DIR, f"{font_name}.bdf")
        )
        if os.path.dirname(caminho) != cls.FONT_DIR:
            raise Exception("Fonte não implementada")

        return caminho

    def __init__(self, tela):
        self.font = None
        self.cursor = (0, 0)
        self.tela = tela
        self.size = 0
        self.font_mode = 0

    def setFontMode(self, mode):
        self.font_mode = int(mode)

    def setFont(self, font_name):
        # Example: "u8g2_font_ncenB14_tr" => "ncenB14"
        #if len(font_name.split("_")) != 4:
            #raise Exception("Nome de Fonte incompleta")
        font_name = "_".join(font_name.split("_")[2:-1])
        #self.size = int(re.sub(r"\D", "", font_name))

        caminho_font = self._resolve_font_path(font_name)
        try:
            font = Font(caminho_font)
        except Exception:
            raise Exception("Fonte não implementada")

        self.fbbxoff = font.headers['fbbxoff']

        # Adjust font bounding box
        max_width = 0
        max_height = 0
        for glyph_name, glyph in font.glyphs.items():
            bbx, bby = glyph[2], glyph[3]
            max_width = max(max_width, bbx)
            max_height = max(max_height, bby)
        font.headers['fbbx'] = max_width
        font.headers['fbby'] = max_height

        # Baseline offset from top of bitmap (after bounding box adjustment)
        self.baseline_offset = font.headers['fbby'] + font.headers['fbbyoff'] - 1
        self.size = font.headers["pointsize"]
        self.font = font
        self.font_mode = 0

    def setCursor(self, x, y):
        self.cursor = (x, y)

    def print(self, text):
        font = self.font
        pixels = self.tela._pixels
        x, y = self.cursor
        x, y = y, x
        x -= self.baseline_offset
        y += self.fbbxoff
        if self.font_mode == 1:
            texto = font.draw(text, direction='lr')
            nparr = np.array(texto.todata(2))
            for i, linha in enumerate(nparr):
                for j, celula in enumerate(linha):
                    if 0 <= x + i < len(pixels) and 0 <= y + j < len(pixels[0]):
                        pixels[x + i][y + j] = any([celula, pixels[x + i][y + j]])
        else:
            # Mode 0: draw a solid filled rectangle for each character's bounding box (bbx x bby)
            glyph_by_code = {g[1]: g for _, g in font.glyphs.items()}
            baseline_row = x + self.baseline_offset
            char_col = 0
            for char in text:
                g = glyph_by_code.get(ord(char))
                if g is None:
                    continue
                advance, bbx, bby, bbxoff, bbyoff = g[8], g[2], g[3], g[4], g[5]
                char_col += advance
                if char == ' ' or bbx == 0 or bby == 0:
                    continue
                col_start = y + (char_col - advance) + bbxoff - self.fbbxoff
                row_start = baseline_row - bbyoff - bby + 1
                for i in range(bby):
                    for j in range(col_start, col_start + bbx):
                        if 0 <= row_start + i < len(pixels) and 0 <= j < len(pixels[0]):
                            pixels[row_start + i][j] = 1
        self.tela._pixels = pixels

    def drawGlyph(self, x, y, encoding):
        font = self.font
        pixels = self.tela._pixels
        x, y = int(y), int(x)
        x -= self.baseline_offset
        y += self.fbbxoff
        if self.font_mode == 0:
            # Mode 0: draw a solid filled rectangle for the glyph's bounding box (bbx x bby)
            for enc, g in font.glyphs.items():
                if g[1] == encoding:
                    bbx, bby, bbxoff, bbyoff = g[2], g[3], g[4], g[5]
                    baseline_row = x + self.baseline_offset
                    col_start = y + bbxoff - self.fbbxoff
                    row_start = baseline_row - bbyoff - bby + 1
                    for i in range(bby):
                        for j in range(col_start, col_start + bbx):
                            if 0 <= row_start + i < len(pixels) and 0 <= j < len(pixels[0]):
                                pixels[row_start + i][j] = 1
                    break
        else:
            str_icon = chr(encoding)
            texto = font.draw(str_icon, direction='lr')
            nparr = np.array(texto.todata(2))
            for i, linha in enumerate(nparr):
                for j, celula in enumerate(linha):
                    if 0 <= x + i < len(pixels) and 0 <= y + j < len(pixels[0]):
                        pixels[x + i][y + j] = any([celula, pixels[x + i][y + j]])
        self.tela._pixels = pixels
