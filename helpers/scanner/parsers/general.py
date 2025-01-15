import cv2
from re import finditer, MULTILINE
from pytesseract import image_to_string
from ..image_helpers import grayscale, thicken_font, add_border


class GeneralParser:
    def __init__(self):
        self.regex = r"^(?!.*\b\d{12}\b.*x \d+\b)(?:(?P<serial>\d*)\s+)?(?P<name>[^\d+\n]+?)\s+(?P<price>\$?\d+\.\d{2})"

    @staticmethod
    def ocr_receipt(receipt) -> str:
        gray = grayscale(receipt)

        # thicken font horizontally to ensure that rows/lines are extracted from the receipt
        gray = thicken_font(gray, 1, 100)

        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Applying dilation on the threshold image to get rough outline of bounding boxes
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2000, 1))
        dilation = cv2.dilate(thresh, kernel, iterations=1)
        contours, _ = cv2.findContours(dilation, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)

        ocr_data=[]
        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)

            # CROPPED MANIPULATION
            cropped = receipt[y:y+h, x:x+w]  # cropping the original image according to the bounding box
            cropped = add_border(cropped, [100, 100, 50, 50])   # adding borders to improve accuracy
            c_gray = grayscale(cropped)

            _, thresholded = cv2.threshold(c_gray, 30, 255, cv2.THRESH_TOZERO)

            thresholded = thicken_font(thresholded, 2, 2)
            cv2.imwrite(f"temp/bboxes/bbox{i}.jpg", thresholded)

            # Apply OCR on the cropped image
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=" 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.\'$-/&:"'
            text = image_to_string(thresholded, config=custom_config)
            ocr_data.append([x,y,text])

        return GeneralParser.sort_by_coordinates(ocr_data)


    @staticmethod
    def extract_date(receipt_ocr: str) -> tuple[str, str, str]:
        """
        Given the result of ocr on a receipt, extract the date in a list containing the
        month, day, year on the receipt in that order

        Args:
            receipt_ocr: the full result of performing OCR on the receipt

        Returns:
            A tuple consisting of the (month, day, year) found on the receipt. If no date could
            be found or one of the components of the date is missing, then an empty string is put in its place
        """
        date_regex = r"(?P<month>(0[1-9]|1[0-2]))[\/-](?P<day>(0[1-9]|[12][0-9]|3[01]))[\/-](?P<year>(\d{2}){1,2})"
        match = next(finditer(date_regex, receipt_ocr), None)
        if match is None:
            return ("", "", "")

        month, day, year = match.group("month").strip(), match.group("day").strip(), match.group("year").strip()
        if month == "" or day == "" or year == "":
            return ("", "", "")

        return (month, day, year)

    @staticmethod
    def sort_by_coordinates(ocr_data: list[list]) -> str:
        """
        Given a list of ocr data, return the ocr'd text sorted with respect to their coordinates

        Args:
            ocr_data: a list of lists containing the x, y, and text that was ocr'd from the contour

        Returns: a single string of sorted ocr'd text
        """
        sorted_list = sorted(ocr_data, key=lambda x: x[1])
        receipt_ocr = ""
        for _, _, text in sorted_list:
            receipt_ocr += text
        return receipt_ocr

    def group_ocr_result(self, receipt_ocr: str) -> list[list]:
        """
        Given unprocessed OCR result, clean it up by getting the items and their price

        Args:
            receipt_ocr: unprocessed result of OCRing a receipt

        Returns:
            A list containing 2 lists, items and their associated prices
        """
        matches = finditer(self.regex, receipt_ocr, MULTILINE)
        items = []            # the name of the items from the receipt
        prices = []           # the price of each item
        forbidden = ["TOTAL", "TAX", "PRICE"]

        for match in matches:
            # We only care about the name and price of the item
            name = match.group("name")
            price = match.group("price")
            if name != "" and price != "" and not any(word in name for word in forbidden):
                items.append(name.strip())
                prices.append(price.strip())
        return [items, prices]
