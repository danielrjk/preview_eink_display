# app/classes/barcode.py

from enum import Enum

class BarcodeType(Enum):
    Unknown = 0
    EAN13 = 1
    EAN8  = 2
    UPCA  = 3
    UPCE  = 4

class BarCode:
    # Built-in 5x7 digit bitmaps matching Adafruit_GFX default font (glcdfont.c)
    DIGIT_BITMAPS = {
        0: [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,1,1],
            [1,0,1,0,1],
            [1,1,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0],
        ],
        1: [
            [0,0,1,0,0],
            [0,1,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,0,1,0,0],
            [0,1,1,1,0],
        ],
        2: [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [0,0,0,0,1],
            [0,1,1,1,0],
            [1,0,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,1],
        ],
        3: [
            [1,1,1,1,1],
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,1,1,0],
            [0,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0],
        ],
        4: [
            [0,0,0,1,0],
            [0,0,1,1,0],
            [0,1,0,1,0],
            [1,0,0,1,0],
            [1,1,1,1,1],
            [0,0,0,1,0],
            [0,0,0,1,0],
        ],
        5: [
            [1,1,1,1,1],
            [1,0,0,0,0],
            [1,1,1,1,0],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0],
        ],
        6: [
            [0,0,1,1,1],
            [0,1,0,0,0],
            [1,0,0,0,0],
            [1,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0],
        ],
        7: [
            [1,1,1,1,1],
            [0,0,0,0,1],
            [0,0,0,0,1],
            [0,0,0,1,0],
            [0,0,1,0,0],
            [0,1,0,0,0],
            [1,0,0,0,0],
        ],
        8: [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,0],
        ],
        9: [
            [0,1,1,1,0],
            [1,0,0,0,1],
            [1,0,0,0,1],
            [0,1,1,1,1],
            [0,0,0,0,1],
            [0,0,0,1,0],
            [1,1,1,0,0],
        ],
    }

    DIGIT_PADDING_TOP = 3

    # Encoding patterns for EAN-13
    EAN_L = [
        "0001101", "0011001", "0010011", "0111101", "0100011",
        "0110001", "0101111", "0111011", "0110111", "0001011"
    ]
    EAN_G = [
        "0100111", "0110011", "0011011", "0100001", "0011101",
        "0111001", "0000101", "0010001", "0001001", "0010111"
    ]
    EAN_R = [
        "1110010", "1100110", "1101100", "1000010", "1011100",
        "1001110", "1010000", "1000100", "1001000", "1110100"
    ]
    EAN13_PATTERN = [
        "LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
        "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"
    ]
    UPCE_ZERO_PATTERN = [
        "GGGLLL", "GGLGLL", "GGLLGL", "GGLLLG", "GLGGLL",
        "GLLGGL", "GLLLGG", "GLGLGL", "GLGLLG", "GLLGLG"
    ]
    UPCE_ONE_PATTERN = [
        "LLLGGG", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
        "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"
    ]

    def __init__(self, tela, scale=1, show_digits=True, background_color=0,
                 bar_color=1, pad_with_leading_zeros=True):
        """
        :param tela: An instance of your Tela class.
        :param scale: Scale factor for barcode elements.
        :param show_digits: Whether to display the numerical digits.
        :param background_color: Color used to clear the drawing area.
        :param bar_color: Color used for the barcode bars.
        :param pad_with_leading_zeros: Automatically pad the code with leading zeros.
        """
        self.tela = tela
        self.scale = scale
        self.show_digits = show_digits
        self.background_color = background_color
        self.bar_color = bar_color
        self.pad_with_leading_zeros = pad_with_leading_zeros

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

    def setShowDigits(self, show_digits):
        self.show_digits = show_digits
        return self

    def getShowDigits(self):
        return self.show_digits

    def setColors(self, background, bars):
        """Set the background and bar colors."""
        self.background_color = background
        self.bar_color = bars
        return self

    def setBackgroundColor(self, background):
        self.background_color = background
        return self

    def getBackgroundColor(self):
        return self.background_color

    def setBarColor(self, bars):
        self.bar_color = bars
        return self

    def getBarColor(self):
        return self.bar_color

    def setPadWithLeadingZeros(self, pad):
        self.pad_with_leading_zeros = pad
        return self

    def getPadWithLeadingZeros(self):
        return self.pad_with_leading_zeros

    # --- Helper & Validation Methods ---

    @staticmethod
    def uint64ToStr(number):
        return str(number)

    @staticmethod
    def getNumberOfDigits(barcode_type):
        if barcode_type == BarcodeType.EAN13:
            return 13
        elif barcode_type == BarcodeType.EAN8:
            return 8
        elif barcode_type == BarcodeType.UPCA:
            return 12
        elif barcode_type == BarcodeType.UPCE:
            return 8
        return 0

    @staticmethod
    def padWithLeadingZerosFunc(barcode, barcode_type):
        required = BarCode.getNumberOfDigits(barcode_type)
        if len(barcode) >= required:
            return barcode
        return barcode.zfill(required)

    @staticmethod
    def validateChecksum(barcode, barcode_type):
        if len(barcode) < 2:
            return False
        # For EAN13, multiply digits at odd positions (index 1,3,5,...) by 3.
        multiplier_index = 1 if barcode_type == BarcodeType.EAN13 else 0
        s = 0
        for i in range(len(barcode) - 1):
            digit = int(barcode[i])
            if i % 2 == multiplier_index:
                s += 3 * digit
            else:
                s += digit
        checksum = (10 - (s % 10)) % 10
        return checksum == int(barcode[-1])

    @staticmethod
    def detectType(barcode, pad_with_leading_zeros=True):
        if not all(ch.isdigit() for ch in barcode):
            return BarcodeType.Unknown
        length = len(barcode)
        if length == 13:
            possible = BarcodeType.EAN13
        elif length == 12:
            possible = BarcodeType.UPCA
        elif length == 8:
            possible = BarcodeType.UPCE if barcode[0] in ['0', '1'] else BarcodeType.EAN8
        elif pad_with_leading_zeros:
            if length <= 8:
                barcode = barcode.zfill(8)
                possible = BarcodeType.EAN8
            else:
                barcode = barcode.zfill(13)
                possible = BarcodeType.EAN13
        else:
            return BarcodeType.Unknown
        return possible if BarCode.validateChecksum(barcode, possible) else BarcodeType.Unknown

    @staticmethod
    def isValid(barcode, barcode_type=BarcodeType.Unknown, pad_with_leading_zeros=True):
        if isinstance(barcode, int):
            barcode = BarCode.uint64ToStr(barcode)
        if barcode_type == BarcodeType.Unknown:
            detected = BarCode.detectType(barcode, pad_with_leading_zeros)
            return detected != BarcodeType.Unknown
        else:
            if pad_with_leading_zeros:
                barcode = BarCode.padWithLeadingZerosFunc(barcode, barcode_type)
            detected = BarCode.detectType(barcode, False)
            if barcode_type == detected:
                return True
            if barcode_type == BarcodeType.EAN8 and detected == BarcodeType.UPCE:
                return True
            return False

    # --- Drawing Methods ---

    def _get_digit_width(self):
        if not self.show_digits:
            return 0
        return 5 * self.scale

    def _get_digit_height(self):
        if not self.show_digits:
            return 0
        return 7 * self.scale

    def _draw_digit(self, digit_char, x, y):
        """
        Renders a single digit at (x, y) using the built-in 3x5 bitmap, scaled by self.scale.
        """
        if not self.show_digits:
            return
        digit = int(digit_char)
        bitmap = self.DIGIT_BITMAPS[digit]
        for row_idx, row in enumerate(bitmap):
            for col_idx, pixel in enumerate(row):
                if pixel:
                    self.tela.fillRect(
                        x + col_idx * self.scale,
                        y + row_idx * self.scale,
                        self.scale, self.scale,
                        self.bar_color
                    )

    def _draw_pattern(self, pattern, x, y, bar_height):
        """
        Draws a binary pattern string as bars at (x, y) with the given height.
        """
        for i, bit in enumerate(pattern):
            if bit == '1':
                self.tela.fillRect(x + i * self.scale, y, self.scale, bar_height, self.bar_color)

    def getWidth(self, barcode_type):
        """
        Computes the width (in pixels) of the barcode drawing based on the barcode type and current scale.
        """
        digit_width = self._get_digit_width()
        padding = 2 * 5 * self.scale

        if barcode_type == BarcodeType.EAN8:
            guard_length = (3 + 5 + 3) * self.scale
            bar_length = 7 * 8 * self.scale
        elif barcode_type == BarcodeType.EAN13:
            guard_length = (3 + 5 + 3) * self.scale
            bar_length = 7 * 12 * self.scale
            if self.show_digits:
                padding += digit_width + self.scale
        elif barcode_type == BarcodeType.UPCA:
            guard_length = (3 + 5 + 3) * self.scale
            bar_length = 7 * 12 * self.scale
            if self.show_digits:
                padding += 2 * (digit_width + self.scale)
        elif barcode_type == BarcodeType.UPCE:
            guard_length = (3 + 0 + 6) * self.scale
            bar_length = 7 * 6 * self.scale
            if self.show_digits:
                padding += 2 * (digit_width + self.scale)
        else:
            return 0

        return padding + guard_length + bar_length

    def draw(self, code, x, y, height, barcode_type=BarcodeType.Unknown):
        """
        Draws the barcode on the Tela.
        :param code: Barcode as a string or integer.
        :param x: X-coordinate of the drawing area.
        :param y: Y-coordinate.
        :param height: Total height in pixels.
        :param barcode_type: The expected BarcodeType. If Unknown, type will be auto-detected.
        :return: True if the barcode was drawn successfully, else False.
        """
        if isinstance(code, int):
            code = self.uint64ToStr(code)
        if barcode_type == BarcodeType.Unknown:
            barcode_type = self.detectType(code, self.pad_with_leading_zeros)
            if barcode_type == BarcodeType.Unknown:
                print("Barcode type detection failed.")
                return False
        if self.pad_with_leading_zeros:
            code = self.padWithLeadingZerosFunc(code, barcode_type)
        if not self.isValid(code, barcode_type, False):
            print("Barcode validation failed.")
            return False

        width = self.getWidth(barcode_type)
        if width == 0:
            return False

        # Draw the background rectangle
        self.tela.fillRect(x, y, width, height, self.background_color)

        PADDING = 5 * self.scale
        digit_height = self._get_digit_height()
        digit_width = self._get_digit_width()

        # Calculate bar heights (mirroring BarcodeGFX layout)
        bar_y = y + PADDING
        number_y = y + height - PADDING - digit_height
        bar_height = number_y - bar_y - self.DIGIT_PADDING_TOP * self.scale
        long_bar_height = bar_height + self.DIGIT_PADDING_TOP * self.scale + digit_height // 2
        if not self.show_digits:
            bar_height += self.DIGIT_PADDING_TOP * self.scale
            long_bar_height = bar_height

        current_x = x + PADDING
        first_digit = int(code[0])

        # Determine index ranges for left/right side digit loops
        if barcode_type == BarcodeType.EAN13:
            index1, index2, index3 = 1, 7, 13
        elif barcode_type == BarcodeType.EAN8:
            index1, index2, index3 = 0, 4, 8
        elif barcode_type == BarcodeType.UPCA:
            index1, index2, index3 = 1, 6, 11
        elif barcode_type == BarcodeType.UPCE:
            index1, index2, index3 = 1, 7, 7

        # Draw first digit outside the bars (all types except EAN-8)
        if barcode_type != BarcodeType.EAN8 and self.show_digits:
            self._draw_digit(code[0], current_x, number_y)
            current_x += digit_width + self.scale

        # Start guard
        self._draw_pattern("101", current_x, bar_y, long_bar_height)
        current_x += 3 * self.scale

        # UPC-A: first digit after start guard uses long bars
        if barcode_type == BarcodeType.UPCA:
            self._draw_pattern(self.EAN_L[first_digit], current_x, bar_y, long_bar_height)
            current_x += 7 * self.scale

        # Draw left side
        for i in range(index1, index2):
            digit = int(code[i])
            if barcode_type == BarcodeType.EAN13:
                pattern_scheme = self.EAN13_PATTERN[first_digit]
                if pattern_scheme[i - 1] == 'G':
                    pattern = self.EAN_G[digit]
                else:
                    pattern = self.EAN_L[digit]
            elif barcode_type == BarcodeType.UPCE:
                last_digit = int(code[7])
                if first_digit == 0:
                    pattern_scheme = self.UPCE_ZERO_PATTERN[last_digit]
                else:
                    pattern_scheme = self.UPCE_ONE_PATTERN[last_digit]
                if pattern_scheme[i - 1] == 'G':
                    pattern = self.EAN_G[digit]
                else:
                    pattern = self.EAN_L[digit]
            else:
                pattern = self.EAN_L[digit]

            self._draw_pattern(pattern, current_x, bar_y, bar_height)
            digit_x = current_x + int(7 * self.scale * 0.5) - digit_width // 2
            self._draw_digit(code[i], digit_x, number_y)
            current_x += 7 * self.scale

        # Middle guard (not for UPC-E)
        if barcode_type != BarcodeType.UPCE:
            self._draw_pattern("01010", current_x, bar_y, long_bar_height)
            current_x += 5 * self.scale

        # Draw right side
        for i in range(index2, index3):
            digit = int(code[i])
            self._draw_pattern(self.EAN_R[digit], current_x, bar_y, bar_height)
            digit_x = current_x + int(7 * self.scale * 0.5) - digit_width // 2
            self._draw_digit(code[i], digit_x, number_y)
            current_x += 7 * self.scale

        # UPC-A: last digit before end guard uses long bars
        if barcode_type == BarcodeType.UPCA:
            last_digit = int(code[11])
            self._draw_pattern(self.EAN_R[last_digit], current_x, bar_y, long_bar_height)
            current_x += 7 * self.scale

        # End guard
        if barcode_type == BarcodeType.UPCE:
            self._draw_pattern("010101", current_x, bar_y, long_bar_height)
            current_x += 6 * self.scale
        else:
            self._draw_pattern("101", current_x, bar_y, long_bar_height)
            current_x += 3 * self.scale

        # Draw last digit outside (UPC-A and UPC-E only)
        if barcode_type in (BarcodeType.UPCA, BarcodeType.UPCE) and self.show_digits:
            self._draw_digit(code[index3], current_x + self.scale, number_y)

        return True
