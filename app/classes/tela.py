class Tela:
    def __init__(self, pixels):
        self.pixels = pixels

    # Public drawing methods
    def fillScreen(self, color):
        self._fill_screen(color)

    def drawLine(self, x1, y1, x2, y2, color):
        self._draw_line(x1, y1, x2, y2, color)

    def fillCircle(self, x, y, r, color):
        self._fill_circle(x, y, r, color)

    def drawCircle(self, x, y, r, color):
        self._draw_circle(x, y, r, color)

    def fillRect(self, x, y, width, height, color):
        self._fill_rect(x, y, width, height, color)

    def drawRect(self, x, y, width, height, color):
        self._draw_rect(x, y, width, height, color)

    def fillTriangle(self, x1, y1, x2, y2, x3, y3, color):
        self._fill_triangle(x1, y1, x2, y2, x3, y3, color)

    def drawTriangle(self, x1, y1, x2, y2, x3, y3, color):
        self._draw_triangle(x1, y1, x2, y2, x3, y3, color)

    # --- Private drawing utility methods ---
    def _fill_screen(self, color):
        self.pixels.fill(color)

    def _draw_line(self, x0, y0, x1, y1, color):
        pixels = self.pixels
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        ystep = 1 if y0 < y1 else -1
        while x0 <= x1:
            if steep:
                if 0 <= x0 < len(pixels) and 0 <= y0 < len(pixels[0]):
                    pixels[x0][y0] = color
            else:
                if 0 <= y0 < len(pixels) and 0 <= x0 < len(pixels[0]):
                    pixels[y0][x0] = color
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1

    def _draw_fast_vline(self, x, y, h, color):
        self._draw_line(x, y, x, y + h - 1, color)

    def _draw_fast_hline(self, x, y, w, color):
        self._draw_line(x, y, x + w - 1, y, color)

    def _fill_circle(self, x0, y0, r, color):
        self._draw_fast_vline(x0, y0 - r, 2 * r + 1, color)
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        px = x
        py = y
        delta = 1
        corners = 3
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            if x < (y + 1):
                if corners & 1:
                    self._draw_fast_vline(x0 + x, y0 - y, 2 * y + delta, color)
                if corners & 2:
                    self._draw_fast_vline(x0 - x, y0 - y, 2 * y + delta, color)
            if y != py:
                if corners & 1:
                    self._draw_fast_vline(x0 + py, y0 - px, 2 * px + delta, color)
                if corners & 2:
                    self._draw_fast_vline(x0 - py, y0 - px, 2 * px + delta, color)
                py = y
            px = x

    def _draw_circle(self, x0, y0, r, color):
        pixels = self.pixels
        f = 1 - r
        ddF_x = 1
        ddF_y = -2 * r
        x = 0
        y = r
        if (y0 + r) < len(pixels) and x0 < len(pixels[0]):
            pixels[y0 + r][x0] = color
        if (y0 - r) >= 0 and x0 < len(pixels[0]):
            pixels[y0 - r][x0] = color
        if y0 < len(pixels) and (x0 + r) < len(pixels[0]):
            pixels[y0][x0 + r] = color
        if y0 < len(pixels) and (x0 - r) >= 0:
            pixels[y0][x0 - r] = color
        while x < y:
            if f >= 0:
                y -= 1
                ddF_y += 2
                f += ddF_y
            x += 1
            ddF_x += 2
            f += ddF_x
            if (y0 + y) < len(pixels) and (x0 + x) < len(pixels[0]):
                pixels[y0 + y][x0 + x] = color
            if (y0 + y) < len(pixels) and (x0 - x) >= 0:
                pixels[y0 + y][x0 - x] = color
            if (y0 - y) >= 0 and (x0 + x) < len(pixels[0]):
                pixels[y0 - y][x0 + x] = color
            if (y0 - y) >= 0 and (x0 - x) >= 0:
                pixels[y0 - y][x0 - x] = color
            if (y0 + x) < len(pixels) and (x0 + y) < len(pixels[0]):
                pixels[y0 + x][x0 + y] = color
            if (y0 + x) < len(pixels) and (x0 - y) >= 0:
                pixels[y0 + x][x0 - y] = color
            if (y0 - x) >= 0 and (x0 + y) < len(pixels[0]):
                pixels[y0 - x][x0 + y] = color
            if (y0 - x) >= 0 and (x0 - y) >= 0:
                pixels[y0 - x][x0 - y] = color

    def _fill_rect(self, x, y, w, h, color):
        for i in range(x, x + w):
            self._draw_fast_vline(i, y, h, color)

    def _draw_rect(self, x, y, w, h, color):
        self._draw_fast_hline(x, y, w, color)
        self._draw_fast_hline(x, y + h - 1, w, color)
        self._draw_fast_vline(x, y, h, color)
        self._draw_fast_vline(x + w - 1, y, h, color)

    def _fill_triangle(self, x0, y0, x1, y1, x2, y2, color):
        # Sort vertices by y-coordinate ascending
        if y0 > y1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        if y0 > y1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        if y0 == y2:
            a = b = x0
            if x1 < a:
                a = x1
            elif x1 > b:
                b = x1
            if x2 < a:
                a = x2
            elif x2 > b:
                b = x2
            self._draw_fast_hline(a, y0, b - a + 1, color)
            return

        dx01 = x1 - x0
        dy01 = y1 - y0
        dx02 = x2 - x0
        dy02 = y2 - y0
        dx12 = x2 - x1
        dy12 = y2 - y1
        sa = 0
        sb = 0

        last = y1 if y1 == y2 else y1 - 1
        for y in range(y0, last + 1):
            a = x0 + sa // dy01
            b = x0 + sb // dy02
            sa += dx01
            sb += dx02
            if a > b:
                a, b = b, a
            self._draw_fast_hline(a, y, b - a + 1, color)

        sa = dx12 * (last - y1)
        sb = dx02 * (last - y0)
        for y in range(y1, y2 + 1):
            a = x1 + sa // dy12
            b = x0 + sb // dy02
            sa += dx12
            sb += dx02
            if a > b:
                a, b = b, a
            self._draw_fast_hline(a, y, b - a + 1, color)

    def _draw_triangle(self, x0, y0, x1, y1, x2, y2, color):
        self._draw_line(x0, y0, x1, y1, color)
        self._draw_line(x1, y1, x2, y2, color)
        self._draw_line(x2, y2, x0, y0, color)
