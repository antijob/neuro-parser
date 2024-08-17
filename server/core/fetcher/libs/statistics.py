class CoroutineStatistics:
    def __init__(self, source: str, article_numbers: int):
        self.source: str = source
        self.len: int = article_numbers
        self._fetch: int = 0
        self._bad_code: int = 0
        self._exception: int = 0
        self.codes: dict[int, int] = {}

    def exception(self):
        self._exception += 1

    def fetch(self):
        self._fetch += 1

    def bad_code(self, code: int):
        self._bad_code += 1
        if code in self.codes:
            self.codes[code] += 1
        else:
            self.codes[code] = 1

    def __str__(self):
        codes_str = ""
        if len(self.codes) > 0:
            codes_str = "\nBad codes info: "
            for code, count in self.codes.items():
                codes_str += f'"{code}": {count}, '
        return (
            f"Coroutine finished. Source: {self.source}\n"
            f"Task articles: {self.len}. Fetched: {self._fetch}. Bad Codes: {self._bad_code}. Exceptions: {self._exception}"
            f"{codes_str}"
        )
