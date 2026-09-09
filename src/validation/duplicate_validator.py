import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

MANIFEST_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\file_manifest.csv"
)

DUPLICATE_CONFIG_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\duplicate_config.csv"
)

ERROR_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\errors\duplicate"
)


def main():

    manifest = pd.read_csv(MANIFEST_PATH)
    duplicate_config = pd.read_csv(DUPLICATE_CONFIG_PATH)

    results = []

    for _, manifest_row in manifest.iterrows():

        source_name = manifest_row["source_name"]
        file_name = manifest_row["file_pattern"]

        file_path = DATASET_PATH / file_name

        print(f"\n{source_name}")
        print("-" * 80)

        if not file_path.exists():

            print("File not found")
            continue

        # -----------------------------------------------------
        # Find duplicate configuration for this source
        # -----------------------------------------------------

        source_config = duplicate_config[
            duplicate_config["source_name"] == source_name
        ]

        # No duplicate rule configured for this source
        if source_config.empty:
            continue

        df = pd.read_csv(file_path)

        total_records = len(df)

        for _, config_row in source_config.iterrows():

            duplicate_key = config_row["duplicate_key"]

            duplicate_columns = duplicate_key.split("|")

            # -------------------------------------------------
            # Validate configured columns exist
            # -------------------------------------------------

            missing_columns = [
                column
                for column in duplicate_columns
                if column not in df.columns
            ]

            if missing_columns:

                print(
                    f"{duplicate_key:<35}"
                    f"Status: COLUMN NOT FOUND"
                )

                results.append({
                    "source_name": source_name,
                    "file_name": file_name,
                    "duplicate_key": duplicate_key,
                    "total_records": total_records,
                    "duplicate_records": "COLUMN_NOT_FOUND",
                    "duplicate_groups": "COLUMN_NOT_FOUND",
                    "duplicate_valid": False
                })

                continue

            # -------------------------------------------------
            # Find all records belonging to duplicate groups
            # -------------------------------------------------

            duplicate_mask = df.duplicated(
                subset=duplicate_columns,
                keep=False
            )

            duplicate_records = duplicate_mask.sum()

            duplicate_groups = (
                df.loc[duplicate_mask, duplicate_columns]
                .drop_duplicates()
                .shape[0]
            )

            duplicate_valid = duplicate_records == 0

            # -------------------------------------------------
            # Extract duplicate records
            # -------------------------------------------------

            if duplicate_records > 0:

                ERROR_PATH.mkdir(
                    parents=True,
                    exist_ok=True
                )

                error_file = (
                    ERROR_PATH
                    / f"{source_name}_{duplicate_key.replace('|', '_')}.csv"
                )

                df.loc[duplicate_mask].to_csv(
                    error_file,
                    index=False
                )

                print(
                    f"Duplicate records written: {error_file}"
                )

            results.append({
                "source_name": source_name,
                "file_name": file_name,
                "duplicate_key": duplicate_key,
                "total_records": total_records,
                "duplicate_records": duplicate_records,
                "duplicate_groups": duplicate_groups,
                "duplicate_valid": duplicate_valid
            })

            print(
                f"{duplicate_key:<35}"
                f"Duplicate Records: {duplicate_records:<8}"
                f"Duplicate Groups: {duplicate_groups:<8}"
                f"Status: {'VALID' if duplicate_valid else 'INVALID'}"
            )

    # ---------------------------------------------------------
    # Write validation report
    # ---------------------------------------------------------

    output = pd.DataFrame(results)

    output_path = Path("metadata")
    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        output_path / "duplicate_validation.csv",
        index=False
    )

    print("\nDuplicate validation report created.")


if __name__ == "__main__":
    main()