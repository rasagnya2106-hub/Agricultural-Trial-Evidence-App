from ingestion import load_all_trials
from database import (
    create_tables,
    clear_database,
    insert_trial,
    insert_source,
)


def make_trial_key(trial):

    return (
        trial.trial_id,
        trial.crop,
        trial.product,
        trial.country,
        trial.year,
        trial.trial_type,
    )


def process_trials():

    trials = load_all_trials()

    print("\n======================================")
    print("DATA QUALITY PROCESSING")
    print("======================================")

    # --------------------------------------------------
    # Create database
    # --------------------------------------------------

    create_tables()
    clear_database()

    # --------------------------------------------------
    # Store EVERY original source
    # --------------------------------------------------

    print("\nStoring original source records...")

    for trial in trials:

        insert_source(trial)

    print(
        f"Original source records stored: {len(trials)}"
    )

    # --------------------------------------------------
    # Identify unique normalized trials
    # --------------------------------------------------

    seen = {}

    unique_trials = []

    for trial in trials:

        key = make_trial_key(trial)

        if key in seen:

            existing = seen[key]

            same_treatment = (
                existing.treatment_yield_kg_ha
                == trial.treatment_yield_kg_ha
            )

            same_control = (
                existing.control_yield_kg_ha
                == trial.control_yield_kg_ha
            )

            if same_treatment and same_control:

                print(
                    f"\nDUPLICATE FOUND: {trial.trial_id}"
                )

                print(
                    f"Source 1: {existing.source}"
                )

                print(
                    f"Source 2: {trial.source}"
                )

            else:

                print(
                    f"\nCONFLICT FOUND: {trial.trial_id}"
                )

                print(
                    f"Source 1: {existing.source}"
                )

                print(
                    f"Treatment: "
                    f"{existing.treatment_yield_kg_ha}"
                )

                print(
                    f"Source 2: {trial.source}"
                )

                print(
                    f"Treatment: "
                    f"{trial.treatment_yield_kg_ha}"
                )

                print(
                    "Both source records will be preserved."
                )

        else:

            seen[key] = trial
            unique_trials.append(trial)

    # --------------------------------------------------
    # Store canonical trials
    # --------------------------------------------------

    print("\n======================================")
    print("STORING NORMALIZED TRIALS")
    print("======================================")

    for trial in unique_trials:

        insert_trial(trial)

    print(
        f"\nUnique normalized trials: "
        f"{len(unique_trials)}"
    )

    print("\n======================================")
    print("PROCESSING COMPLETE")
    print("======================================")


if __name__ == "__main__":

    process_trials()