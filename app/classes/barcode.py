# app/classes/barcode.py

from enum import Enum

class BarcodeType(Enum):
    Unknown = 0
    EAN13 = 1
    EAN8  = 2
    UPCA  = 3
    UPCE  = 4

class BarCode:
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

    def getWidth(self, barcode_type):
        """
        Computes the width (in pixels) of the barcode drawing based on the barcode type and current scale.
        """
        PADDING = 5 * self.scale
        if barcode_type in (BarcodeType.EAN13, BarcodeType.UPCA):
            # start guard (3) + left digits (6*7) + middle guard (5) + right digits (6*7) + end guard (3)
            width = 2 * PADDING + (3 + 42 + 5 + 42 + 3) * self.scale
        elif barcode_type in (BarcodeType.EAN8, BarcodeType.UPCE):
            # simplified for 8-digit codes
            width = 2 * PADDING + (3 + 28 + 3) * self.scale
        else:
            width = 0
        return width

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

        # Implement drawing for EAN-13 only.
        if barcode_type == BarcodeType.EAN13:
            if len(code) != 13:
                print("EAN-13 barcode must have 13 digits.")
                return False

            width = self.getWidth(barcode_type)
            # Draw the background rectangle.
            self.tela.fillRect(x, y, width, height, self.background_color)

            PADDING = 5 * self.scale
            current_x = x + PADDING

            # Build the barcode pattern: start guard, left side, middle guard, right side, end guard.
            full_pattern = "101"
            first_digit = int(code[0])
            pattern_scheme = self.EAN13_PATTERN[first_digit]
            left_digits = code[1:7]
            for i, digit_char in enumerate(left_digits):
                digit = int(digit_char)
                if pattern_scheme[i] == 'L':
                    full_pattern += self.EAN_L[digit]
                else:
                    full_pattern += self.EAN_G[digit]
            full_pattern += "01010"
            right_digits = code[7:13]
            for digit_char in right_digits:
                digit = int(digit_char)
                full_pattern += self.EAN_R[digit]
            full_pattern += "101"

            # Debug: Print the built pattern.

            # Draw the barcode bars.
            for bit in full_pattern:
                if bit == '1':
                    self.tela.fillRect(current_x, y, self.scale, height, self.bar_color)
                current_x += self.scale

            # (Optional: Implement drawing digits if self.show_digits is True.)
            return True
        else:
            print("Barcode type not implemented.")
            return False
