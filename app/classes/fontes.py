import os
import re
import numpy as np
from bdfparser import Font

class Fontes:
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
        self.font_mode = 0
        #self.size = int(re.sub(r"\D", "", font_name))

        # Build path to your BDF font
        base_dir = os.path.dirname(os.path.abspath(__file__))  
        caminho_font = os.path.join(
            base_dir, 
            "..",  # go up one level to /classes
            "src", 
            "olikraus_u8g2_master_tools-font_bdf", 
            f"{font_name}.bdf"
        )
        try:
            font = Font(caminho_font)
        except:
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

    def setCursor(self, x, y):
        self.cursor = (x, y)

    def print(self, text):
        font = self.font
        pixels = self.tela.pixels
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
        self.tela.pixels = pixels

    def drawGlyph(self, x, y, encoding):
        font = self.font
        pixels = self.tela.pixels
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
        self.tela.pixels = pixels
