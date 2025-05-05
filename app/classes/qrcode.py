from qrcodegen import QrCode

class QRCode:
    def __init__(self, tela, scale=1):
        """
        :param tela: An instance of your Tela class.
        :param scale: Scale factor for barcode elements.
        """
        self.tela = tela
        self.scale = scale

    # --- Setter and Getter Methods for Method Chaining ---

    def setScale(self, scale):
        if scale == 0:
            scale = 1
        elif scale > 20:
            scale = 20
        self.scale = scale
        return self

    def getScale(self):
        return self.scale

    # --- Drawing Methods ---


    def draw(self, code, x, y):
      """
      Draws the barcode on the Tela.
      :param code: Barcode as a string or integer.
      :param x: X-coordinate of the drawing area.
      :param y: Y-coordinate.
      """
      qr = QrCode.encode_text(code, QrCode.Ecc.LOW)
      size = qr.get_size()
      base_matrix = [[1 if qr.get_module(x, y) else 0 for x in range(size)] for y in range(size)]
      scale = self.getScale()
      matrix = []

      margin=3

      padded_size = size + 2*margin
      padded_matrix = [[0 for _ in range(padded_size)] for _ in range(padded_size)]

      for y_padding in range(size):
         for x_padding in range(size):
            padded_matrix[y_padding+margin][x_padding+margin] = base_matrix[y_padding][x_padding]

      for row in padded_matrix:
        matrix_row_block = [[cell]*scale for cell in row]
        for _ in range(scale):
           scaled_row = [item for group in matrix_row_block for item in group]
           matrix.append(scaled_row)

      for matrix_x, row in enumerate(matrix):
         for matrix_y, cell in enumerate(row):
            self.tela.fillRect(x+matrix_x,y+matrix_y,1,1,cell)
      
      return True
            
