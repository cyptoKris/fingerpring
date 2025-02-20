class AirDropException(Exception):
    def __init__(self, name: str, *args: object) -> None:
        super().__init__(*args)
        self.name: str = name

    def __repr__(self):
        return f"{self.__class__}"

    def __str__(self):
        return self.__repr__()


class WalletInfoException(AirDropException):
    def __init__(self, info: str):
        super().__init__("WalletInfo")
        self.info = info

    def __repr__(self):
        return f"{self.info}"
