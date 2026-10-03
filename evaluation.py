from tools import (
    search_trials,
    compare_trials,
    find_evidence,
    get_trial_sources,
)


def check_search():
    results = search_trials(
        crop="Wheat",
        product="Harvest Plus"
    )

    expected = {"T01", "T02", "T05", "T06"}
    actual = {trial["trial_id"] for trial in results}

    passed = actual == expected

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        "Wheat + Harvest Plus search"
    )

    if not passed:
        print("Expected:", expected)
        print("Actual:", actual)

    return passed


def check_scientific_trials():
    results = search_trials(
        crop="Wheat",
        product="Harvest Plus",
        trial_type="Scientific"
    )

    expected = {"T01", "T06"}
    actual = {trial["trial_id"] for trial in results}

    passed = actual == expected

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        "Scientific wheat trial filter"
    )

    if not passed:
        print("Expected:", expected)
        print("Actual:", actual)

    return passed


def check_comparison():
    results = compare_trials(
        ["T01", "T02"]
    )

    values = {
        trial["trial_id"]: trial
        for trial in results
    }

    passed = (
        values["T01"]["absolute_change_kg_ha"] == 400
        and round(
            values["T01"]["percentage_change"], 2
        ) == 5.00
        and values["T02"]["absolute_change_kg_ha"] == 300
        and round(
            values["T02"]["percentage_change"], 2
        ) == 4.00
    )

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        "Trial comparison calculations"
    )

    return passed


def check_conflicting_sources():
    sources = get_trial_sources("T03")

    treatment_values = {
        source["treatment_yield_kg_ha"]
        for source in sources
    }

    passed = treatment_values == {
        42000.0,
        44000.0
    }

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        "T03 conflicting source values preserved"
    )

    return passed


def check_missing_value():
    results = search_trials(
        crop="Wheat",
        product="Harvest Plus",
        country="Germany",
        year=2025
    )

    passed = (
        len(results) == 1
        and results[0]["trial_id"] == "T05"
        and results[0]["control_yield_kg_ha"] is None
    )

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        "Missing control value handled correctly"
    )

    return passed


def check_no_rice_evidence():
    results = find_evidence(
        crop="Rice",
        product="Harvest Plus"
    )

    passed = len(results) == 0

    print(
        f"[{'PASS' if passed else 'FAIL'}] "
        "No unsupported rice evidence"
    )

    return passed


def run_evaluation():

    print("=" * 60)
    print("AGRICULTURAL TRIAL EVIDENCE APP")
    print("EVALUATION")
    print("=" * 60)

    checks = [
        check_search(),
        check_scientific_trials(),
        check_comparison(),
        check_conflicting_sources(),
        check_missing_value(),
        check_no_rice_evidence(),
    ]

    passed = sum(checks)
    total = len(checks)

    print()
    print("=" * 60)
    print(
        f"RESULT: {passed}/{total} checks passed"
    )
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    run_evaluation()