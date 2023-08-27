import os

import zipfile
import tarfile

from django.core.exceptions import ValidationError


class UnsupportedFileFormatError(Exception):
    pass

def unpack_file(file_path, extract_path):
    if file_path.endswith(".zip"):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_path)
    elif file_path.endswith(".tar.gz"):
        with tarfile.open(file_path, "r:gz") as tar:
            tar.extractall(extract_path)
    elif file_path.endswith(".tar"):
        with tarfile.open(file_path, "r:") as tar:
            tar.extractall(extract_path)
    else:
        raise UnsupportedFileFormatError("Неподдерживаемое разрешение файла: " + file_path)


def extract_filename_without_extension(file_path):
    base_filename = os.path.basename(file_path)
    filename, extensions = os.path.splitext(base_filename)

    while extensions:
        filename, extensions = os.path.splitext(filename)

    return filename


def validate_file_extension(value):
    if value.name.endswith('.zip') or \
       value.name.endswith('.tar') or \
       value.name.endswith('.tar.gz'):
       return

    raise ValidationError('Неподдерживаемое разрешение файла: ' + value.name)
