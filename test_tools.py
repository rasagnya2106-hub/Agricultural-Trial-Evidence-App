from tools import (
    search_trials,
    compare_trials,
    find_evidence,
    get_trial_sources,
)


print("\n======================================")
print("TEST 1: SEARCH TRIALS")
print("======================================")

results = search_trials(
    crop="Wheat",
    product="Harvest Plus"
)

for result in results:

    print(
        result["trial_id"],
        result["country"],
        result["year"]
    )


print("\n======================================")
print("TEST 2: COMPARE TRIALS")
print("======================================")

results = compare_trials(
    ["T01", "T02"]
)

for result in results:

    print(
        result["trial_id"],
        result["country"],
        result["percentage_change"]
    )


print("\n======================================")
print("TEST 3: FIND EVIDENCE")
print("======================================")

results = find_evidence(
    crop="Potato",
    product="Root Boost"
)

for result in results:

    print(
        result["trial_id"],
        result["treatment_yield_kg_ha"],
        result["control_yield_kg_ha"],
        result["yield_difference_kg_ha"]
    )


print("\n======================================")
print("TEST 4: GET SOURCES")
print("======================================")

sources = get_trial_sources("T03")

for source in sources:

    print(
        source["source"],
        source["treatment_yield_kg_ha"],
        source["control_yield_kg_ha"]
    )


print("\n======================================")
print("ALL TOOL TESTS COMPLETE")
print("======================================")