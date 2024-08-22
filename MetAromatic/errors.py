from logging import getLogger


class SearchError(Exception):
    log = getLogger("met-aromatic")

    def __init__(self, message: str) -> None:
        self.log.error(message)
        super().__init__(message)
