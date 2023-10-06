# -*- coding: utf-8 -*-

"""
Settings module
"""

from pathlib import Path

from decouple import config as c

# Build paths inside the project like this: BASE_DIR.joinpath('some')
# `pathlib` is better than writing:
# BASE_DIR = dirname(dirname(dirname(dirname(__file__))))
BASE_DIR = Path(__file__).parent.parent.parent.parent

