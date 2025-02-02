import cv2
from pytesseract import image_to_string
from ..image_helpers import grayscale, thicken_font
from .general import GeneralParser



class TargetParser(GeneralParser):
    """A parser specifically for Target receipts"""
    def __init__(self):
        super().__init__()
        self.regex = r"(?P<serial>\d{4,})\s+(?P<name>.+?)\s+((?P<extra>[a-zA-Z]{1,2})\s+)?(?:\$)?(?P<price>\d+\.\d{1,2})"

    @staticmethod
    def ocr_receipt(receipt) -> str:
        _, receipt_gray = cv2.threshold(grayscale(receipt), 127, 255, cv2.THRESH_BINARY)
        thickened = thicken_font(receipt_gray, 2, 2)
        receipt_ocr = image_to_string(thickened)
        return receipt_ocr
