import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

MANIFEST_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\file_manifest.csv"
)

ERROR_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\errors\null"
)


def main():

    manifest = pd.read_csv(MANIFEST_PATH)

    results = []

    for _, row in manifest.iterrows():

        source_name = row["source_name"]
        file_name = row["file_pattern"]

        file_path = DATASET_PATH / file_name

        print(f"\n{source_name}")
        print("-" * 80)

        if not file_path.exists():

            print("File not found")
            continue

        df = pd.read_csv(file_path)

        total_records = len(df)

        for column_name in df.columns:

            null_mask = df[column_name].isna()

            null_count = null_mask.sum()

            null_percentage = (
                (null_count / total_records) * 100
                if total_records > 0
                else 0
            )

            # -------------------------------------------------
            # Extract records containing null values
            # -------------------------------------------------

            if null_count > 0:

                ERROR_PATH.mkdir(
                    parents=True,
                    exist_ok=True
                )

                error_file = (
                    ERROR_PATH
                    / f"{source_name}_{column_name}.csv"
                )

                df.loc[null_mask].to_csv(
                    error_file,
                    index=False
                )

                print(
                    f"Null records written: {error_file}"
                )

            results.append({
                "source_name": source_name,
                "file_name": file_name,
                "column_name": column_name,
                "total_records": total_records,
                "null_count": null_count,
                "null_percentage": round(null_percentage, 2)
            })

            print(
                f"{column_name:<35}"
                f"Nulls: {null_count:<8}"
                f"Null %: {null_percentage:.2f}%"
            )

    output = pd.DataFrame(results)

    output_path = Path("metadata")
    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    output.to_csv(
        output_path / "null_validation.csv",
        index=False
    )

    print("\nNull validation report created.")


if __name__ == "__main__":
    main()