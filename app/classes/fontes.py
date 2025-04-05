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

    def setFont(self, font_name):
        # Example: "u8g2_font_ncenB14_tr" => "ncenB14"
        if len(font_name.split("_")) != 4:
            raise Exception("Nome de Fonte incompleta")
        font_name = "_".join(font_name.split("_")[2:-1])
        self.size = int(re.sub(r"\D", "", font_name))

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

        # Adjust font bounding box
        max_width = 0
        max_height = 0
        for glyph_name, glyph in font.glyphs.items():
            bbx, bby = glyph[2], glyph[3]
            max_width = max(max_width, bbx)
            max_height = max(max_height, bby)
        font.headers['fbbx'] = max_width
        font.headers['fbby'] = max_height

        self.font = font

    def setCursor(self, x, y):
        self.cursor = (x, y)

    def print(self, text):
        font = self.font
        texto = font.draw(text, direction='lr')
        nparr = np.array(texto.todata(2))
        pixels = self.tela.pixels
        x, y = self.cursor
        # In your original code you swapped x,y => just replicate that logic
        x, y = y, x
        x -= self.size
        for i, linha in enumerate(nparr):
            for j, celula in enumerate(linha):
                if 0 <= x + i < len(pixels) and 0 <= y + j < len(pixels[0]):
                    # 'any' is basically an OR operation
                    pixels[x + i][y + j] = any([celula, pixels[x + i][y + j]])
        self.tela.pixels = pixels

    def drawGlyph(self, font_name, x, y, encoding):
        # Save the old font
        fonteAnterior = self.font
        self.setFont(font_name)
        font = self.font
        pixels = self.tela.pixels
        x, y = y, x
        str_icon = chr(encoding)
        texto = font.draw(str_icon, direction='lr')
        nparr = np.array(texto.todata(2))
        for i, linha in enumerate(nparr):
            for j, celula in enumerate(linha):
                if 0 <= x + i < len(pixels) and 0 <= y + j < len(pixels[0]):
                    pixels[x + i][y + j] = any([celula, pixels[x + i][y + j]])
        self.tela.pixels = pixels
        # Restore old font
        self.font = fonteAnterior
