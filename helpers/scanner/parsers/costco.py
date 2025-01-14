import cv2
from pytesseract import image_to_string
from ..image_helpers import grayscale, thicken_font, add_border, dilate
from .general import GeneralParser


class CostcoParser(GeneralParser):
    """A parser specifically for Costco receipts"""
    def __init__(self):
        super().__init__()
        self.regex = r"(?:(?P<extra>[A-Z]) +)?(?:(?P<serial>\d{1,}) +)(?P<name>(?=.*[a-zA-Z]{3,}).+) +(?P<price>\$?\d+\.\d{2})"

    @staticmethod
    def ocr_receipt(receipt) -> str:
        dilated = dilate(receipt, horizontal_param=300)

        # Finding contours using the dialated image
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

        ocr_data = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)

            # MANIPULATING THE BOUNDING BOX SUBSECTION
            cropped = receipt[y:y+h, x:x+w]  # cropping the original image according to the bounding box
            cropped = add_border(cropped, [100, 100, 50, 50])   # adding borders to improve accuracy
            c_gray = grayscale(cropped)
            _, thresholded = cv2.threshold(c_gray, 127, 230, cv2.THRESH_BINARY)
            thresholded = thicken_font(thresholded, 3, 3)

            # Apply OCR on the cropped image
            # For Costco, accuracy of ocr is improved by using this custom config
            custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=" 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.%/$-:''"'
            text = image_to_string(thresholded, config=custom_config)

            ocr_data.append([x,y,text])

        return GeneralParser.sort_by_coordinates(ocr_data)
