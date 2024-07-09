import time


class CoroutineStatistics:
    def __init__(self, source: str, article_numbers: int):
        self.source: str = source
        self.len: int = article_numbers
        self.fetches: int = 0
        self.success: int = 0
        self.bad_codes: int = 0
        self.exceptions: int = 0
        self.codes: Dict[int, int] = {}

        self.start_time: float = 0
        self.elapsed_time: float = 0
        self.fetch_time: float = 0
        self.postprocess_time: float = 0
        self.fetch_start_time: float = 0

    def start(self):
        self.start_time = time.time()

    def finish(self):
        end_time = time.time()
        self.elapsed_time = end_time - self.start_time

    def exception(self):
        self.exceptions += 1

    def postprocess(self, time: float):
        self.postprocess_time += time
        self.success += 1

    def fetch_start(self):
        self.fetch_start_time = time.time()

    def fetched(self):
        fetch_end_time = time.time()
        self.fetch_time += fetch_end_time - self.fetch_start_time
        self.fetches += 1

    def bad_code(self, code: int):
        self.bad_codes += 1
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
            f"Coroutine finished. Source: {self.source}: {self.len} articles by {self.elapsed_time:.2f}s.\n"
            f"Fetch time: {self.fetch_time:.2f}s, Parse time:{self.postprocess_time:.2f}s\n"
            f"Succeded: {self.success}, Fetched: {self.fetches}, Bad Codes: {self.bad_codes}, Exceptions: {self.exceptions}"
            f"{codes_str}"
        )
