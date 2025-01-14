from .general import GeneralParser


class WalmartParser(GeneralParser):
    """A parser specifically for Walmart receipts"""
    def __init__(self):
        super().__init__()

        # required name, required serial number, optional capital letter, required price
        self.regex = r"(?P<name>[^\n]+?)\s+((?P<serial>\d+)\s+)(?:(?P<letter>[A-Z]?)\s+)?(?P<price>\d+\.\d{2})"
