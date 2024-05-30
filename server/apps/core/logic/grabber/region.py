import os.path

from django.conf import settings

from server.apps.core.data.topo import TOPONYMS, COUNTRIES
from server.apps.core.logic.morphy import normalize_text

DATA_DIR = os.path.join(
    settings.BASE_DIR,
    "server",
    "apps",
    "core",
    "logic",
    "grabber",
    "classificator",
    "data",
)


def region_codes(text):
    text = text.strip()
    default_region = "ALL"
    if not text:
        return [default_region]

    normalized_text = tuple(normalize_text(text))
    if not normalized_text:
        return [default_region]
    toponyms_counters = {}
    for region_code, regional_toponyms in TOPONYMS.items():
        for toponym in regional_toponyms:
            if toponym in normalized_text:
                toponyms_counters[region_code] = (
                    toponyms_counters.get(region_code, 0) + 1
                )
    if not toponyms_counters:
        return [default_region]
    return sorted(toponyms_counters, key=lambda x: toponyms_counters[x], reverse=True)


def region_code(text):
    return region_codes(text)[0]
