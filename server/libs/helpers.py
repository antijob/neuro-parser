from pathlib import Path

DATA_SUBFOLDER = "test_data"


def load_pytest_data(file_path):
    def _load(filename, file_path=file_path):
        filepath = Path(file_path).parent / DATA_SUBFOLDER / filename
        with open(filepath, "r", encoding="utf-8") as file:
            return file.read()

    return _load
