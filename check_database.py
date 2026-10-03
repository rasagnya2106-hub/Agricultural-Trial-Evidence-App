from database import get_all_trials, get_sources


rows = get_all_trials()

print("\n======================================")
print("NORMALIZED TRIALS")
print("======================================")

for row in rows:

    trial_id = row[0]

    print("\n--------------------------------------")

    print(f"Trial ID: {trial_id}")
    print(f"Crop: {row[1]}")
    print(f"Product: {row[2]}")
    print(f"Country: {row[3]}")
    print(f"Year: {row[4]}")
    print(f"Type: {row[5]}")
    print(f"Treatment: {row[6]} kg/ha")
    print(f"Control: {row[7]} kg/ha")

    print("\nSources:")

    sources = get_sources(trial_id)

    for source in sources:

        print(
            f"  - {source[1]}"
        )

        print(
            f"    Treatment: "
            f"{source[3]} kg/ha"
        )

        print(
            f"    Control: "
            f"{source[4]} kg/ha"
        )

        if source[5]:

            print(
                f"    Notes: "
                f"{source[5]}"
            )


print("\n======================================")
print(
    f"Total normalized trials: {len(rows)}"
)
print("======================================")