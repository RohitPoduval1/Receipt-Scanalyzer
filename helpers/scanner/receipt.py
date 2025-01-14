class Receipt:
    def __init__(self):
        self.file = None
        self.store: str = ""
        self.items: list[str] = []
        self.prices: list[float] = []
        self.date: str = ""
