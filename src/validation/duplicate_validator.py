import pandas as pd
from pathlib import Path


DATASET_PATH = Path(r"C:\Users\sayan\OneDrive\Documents\dataset")

MANIFEST_PATH = Path(r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\file_manifest.csv")

DUPLICATE_CONFIG_PATH = Path(r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\duplicate_config.csv")


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

        df = pd.read_csv(file_path)

        config = duplicate_config[
            duplicate_config["source_name"] == source_name
        ]

        if config.empty:

            print("No duplicate rule configured")
            continue

        duplicate_key = config.iloc[0]["duplicate_key"]

        key_columns = duplicate_key.split("|")

        missing_columns = [
            column
            for column in key_columns
            if column not in df.columns
        ]

        if missing_columns:

            print(
                f"Key columns not found: {missing_columns}"
            )

            results.append({
                "source_name": source_name,
                "file_name": file_name,
                "duplicate_key": duplicate_key,
                "total_records": len(df),
                "duplicate_records": None,
                "duplicate_groups": None,
                "duplicate_valid": False
            })

            continue

        duplicate_mask = df.duplicated(
            subset=key_columns,
            keep=False
        )

        duplicate_records = duplicate_mask.sum()

        duplicate_groups = (
            df.loc[duplicate_mask, key_columns]
            .drop_duplicates()
            .shape[0]
        )

        duplicate_valid = duplicate_records == 0

        results.append({
            "source_name": source_name,
            "file_name": file_name,
            "duplicate_key": duplicate_key,
            "total_records": len(df),
            "duplicate_records": duplicate_records,
            "duplicate_groups": duplicate_groups,
            "duplicate_valid": duplicate_valid
        })

        print(
            f"Duplicate Key: {duplicate_key}"
        )

        print(
            f"Total Records: {len(df)}"
        )

        print(
            f"Duplicate Records: {duplicate_records}"
        )

        print(
            f"Duplicate Groups: {duplicate_groups}"
        )

        print(
            f"Status: {'VALID' if duplicate_valid else 'INVALID'}"
        )

    output = pd.DataFrame(results)

    output_path = Path("metadata")
    output_path.mkdir(exist_ok=True)

    output.to_csv(
        output_path / "duplicate_validation.csv",
        index=False
    )

    print("\nDuplicate validation report created.")


if __name__ == "__main__":
    main()