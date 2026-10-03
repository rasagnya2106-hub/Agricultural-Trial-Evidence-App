COUNTRY_MAP = {
    "FR": "France",
    "DE": "Germany",
    "ES": "Spain",
}

PRODUCT_MAP = {
    "harvest plus": "Harvest Plus",
    "harvestplus": "Harvest Plus",
    "root boost": "Root Boost",
    "rootboost": "Root Boost",
}

CROP_MAP = {
    "wheat": "Wheat",
    "potato": "Potato",
    "potatoes": "Potato",
}


def normalize_product(value):
    if not value:
        return None

    key = value.strip().lower()
    return PRODUCT_MAP.get(key, value.strip())


def normalize_country(value):
    if not value:
        return None

    value = value.strip()

    return COUNTRY_MAP.get(value.upper(), value.title())


def normalize_crop(value):
    if not value:
        return None

    key = value.strip().lower()

    return CROP_MAP.get(key, value.title())


def convert_to_kg(value, unit):
    if value is None:
        return None

    if not unit:
        return float(value)

    unit = unit.lower().strip()

    if "t/ha" in unit:
        return float(value) * 1000

    return float(value)