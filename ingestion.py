from pathlib import Path
import pandas as pd
import re

from models import Trial
from normalization import (
    normalize_product,
    normalize_country,
    normalize_crop,
    convert_to_kg,
)


# ---------------------------------------------------------
# PROJECT PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "sample-data"


# ---------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------

def clean_value(value):
    """
    Convert empty/NaN values into None.
    """
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def clean_number(value):
    """
    Convert a value into float when possible.
    """
    value = clean_value(value)

    if value is None:
        return None

    try:
        return float(value)
    except ValueError:
        return None


def normalize_trial_type(value):
    """
    Normalize trial type names.
    """
    value = clean_value(value)

    if not value:
        return None

    return value.strip().title()


# ---------------------------------------------------------
# CSV INGESTION
# ---------------------------------------------------------

def load_trials_a():
    """
    Read trials_a.csv and convert it into standard Trial records.
    """

    path = DATA_DIR / "trials_a.csv"

    df = pd.read_csv(path)

    records = []

    for _, row in df.iterrows():

        trial_id = clean_value(row.get("trial_id"))
        crop = normalize_crop(row.get("crop"))
        product = normalize_product(row.get("product"))
        country = normalize_country(row.get("country"))

        year = clean_number(row.get("year"))

        trial_type = normalize_trial_type(
            row.get("trial_type")
        )

        treatment = clean_number(
            row.get("treatment_yield")
        )

        control = clean_number(
            row.get("control_yield")
        )

        unit = clean_value(
            row.get("yield_unit")
        )

        treatment_kg = convert_to_kg(
            treatment,
            unit
        )

        control_kg = convert_to_kg(
            control,
            unit
        )

        record = Trial(
            trial_id=trial_id,
            crop=crop,
            product=product,
            country=country,
            year=int(year) if year is not None else None,
            trial_type=trial_type,
            treatment_yield_kg_ha=treatment_kg,
            control_yield_kg_ha=control_kg,
            source="trials_a.csv",
            source_type="csv",
        )

        records.append(record)

    return records


def load_trials_b():
    """
    Read trials_b.csv and convert it into standard Trial records.
    """

    path = DATA_DIR / "trials_b.csv"

    df = pd.read_csv(path)

    records = []

    for _, row in df.iterrows():

        trial_id = clean_value(
            row.get("Trial reference")
        )

        crop = normalize_crop(
            row.get("Crop name")
        )

        product = normalize_product(
            row.get("Product name")
        )

        country = normalize_country(
            row.get("Country code")
        )

        year = clean_number(
            row.get("Season year")
        )

        trial_type = normalize_trial_type(
            row.get("Trial category")
        )

        treatment = clean_number(
            row.get("Treated yield kg per ha")
        )

        control = clean_number(
            row.get("Untreated yield kg per ha")
        )

        record = Trial(
            trial_id=trial_id,
            crop=crop,
            product=product,
            country=country,
            year=int(year) if year is not None else None,
            trial_type=trial_type,
            treatment_yield_kg_ha=treatment,
            control_yield_kg_ha=control,
            source="trials_b.csv",
            source_type="csv",
        )

        records.append(record)

    return records


# ---------------------------------------------------------
# TEXT REPORT PARSER
# ---------------------------------------------------------

def parse_text_report(filename):
    """
    Read one of the supplied text reports and convert it
    into a standard Trial record.
    """

    path = DATA_DIR / filename

    text = path.read_text(
        encoding="utf-8"
    )

    trial_match = re.search(
        r"Trial\s+(T\d+)",
        text,
        re.IGNORECASE
    )

    crop_match = re.search(
        r"Crop:\s*([^\n.]+)",
        text,
        re.IGNORECASE
    )

    product_match = re.search(
        r"Product:\s*([^\n.]+)",
        text,
        re.IGNORECASE
    )

    country_match = re.search(
        r"(?:Location|Country):\s*([^\n.]+)",
        text,
        re.IGNORECASE
    )

    year_match = re.search(
        r"Year:\s*(\d{4})",
        text,
        re.IGNORECASE
    )

    type_match = re.search(
        r"Trial type:\s*([^\n.]+)",
        text,
        re.IGNORECASE
    )

    treatment_match = re.search(
        r"(?:Treated yield|Treatment yield):\s*([\d.]+)\s*(t/ha|kg/ha)",
        text,
        re.IGNORECASE
    )

    control_match = re.search(
        r"(?:Untreated yield|Control yield|Untreated control yield):\s*([\d.]+)\s*(t/ha|kg/ha)",
        text,
        re.IGNORECASE
    )

    notes_match = re.search(
        r"Notes\s*(.*)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    trial_id = (
        trial_match.group(1)
        if trial_match
        else None
    )

    crop = (
        normalize_crop(crop_match.group(1))
        if crop_match
        else None
    )

    product = (
        normalize_product(product_match.group(1))
        if product_match
        else None
    )

    country = (
        normalize_country(country_match.group(1))
        if country_match
        else None
    )

    year = (
        int(year_match.group(1))
        if year_match
        else None
    )

    trial_type = (
        normalize_trial_type(type_match.group(1))
        if type_match
        else None
    )

    treatment = None

    if treatment_match:
        treatment = convert_to_kg(
            float(treatment_match.group(1)),
            treatment_match.group(2)
        )

    control = None

    if control_match:
        control = convert_to_kg(
            float(control_match.group(1)),
            control_match.group(2)
        )

    notes = (
        notes_match.group(1).strip()
        if notes_match
        else None
    )

    return Trial(
        trial_id=trial_id,
        crop=crop,
        product=product,
        country=country,
        year=year,
        trial_type=trial_type,
        treatment_yield_kg_ha=treatment,
        control_yield_kg_ha=control,
        source=filename,
        source_type="report",
        notes=notes,
    )


# ---------------------------------------------------------
# LOAD ALL REPORTS
# ---------------------------------------------------------

def load_reports():

    report_files = [
        "T02_field_report.txt",
        "T03_summary.txt",
        "T04_scientific_report.txt",
        "T06_archive_note.txt",
    ]

    records = []

    for filename in report_files:

        record = parse_text_report(filename)

        records.append(record)

    return records


# ---------------------------------------------------------
# LOAD EVERYTHING
# ---------------------------------------------------------

def load_all_trials():

    records = []

    records.extend(load_trials_a())
    records.extend(load_trials_b())
    records.extend(load_reports())

    return records


# ---------------------------------------------------------
# TEST THE INGESTION
# ---------------------------------------------------------

if __name__ == "__main__":

    trials = load_all_trials()

    print("\n======================================")
    print("AGRICULTURAL TRIAL DATA")
    print("======================================")

    print(f"\nTotal records loaded: {len(trials)}\n")

    for trial in trials:

        print("--------------------------------------")

        print(f"Trial ID: {trial.trial_id}")
        print(f"Crop: {trial.crop}")
        print(f"Product: {trial.product}")
        print(f"Country: {trial.country}")
        print(f"Year: {trial.year}")
        print(f"Type: {trial.trial_type}")

        print(
            f"Treatment: "
            f"{trial.treatment_yield_kg_ha} kg/ha"
        )

        print(
            f"Control: "
            f"{trial.control_yield_kg_ha} kg/ha"
        )

        print(f"Source: {trial.source}")

        if trial.notes:
            print(f"Notes: {trial.notes}")

    print("\n======================================")
    print("INGESTION COMPLETE")
    print("======================================")