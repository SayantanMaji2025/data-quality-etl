import hashlib
import pandas as pd
from pathlib import Path


DATASET_PATH = Path(r"C:\Users\sayan\OneDrive\Documents\dataset")
MANIFEST_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\file_manifest.csv"
)


def calculate_schema_hash(columns):
    schema = "|".join(columns)
    return hashlib.sha256(schema.encode("utf-8")).hexdigest()


def main():
    manifest = pd.read_csv(MANIFEST_PATH)

    results = []

    for _, row in manifest.iterrows():

        file_path = DATASET_PATH / row["file_pattern"]

        file_arrival = file_path.exists()

        actual_hash = None
        schema_status = False
        file_size = 0

        if file_arrival:

            df = pd.read_csv(file_path, nrows=0)

            actual_columns = list(df.columns)
            expected_columns = row["expected_schema"].split("|")

            actual_hash = calculate_schema_hash(actual_columns)
            expected_hash = calculate_schema_hash(expected_columns)

            schema_status = actual_hash == expected_hash

            file_size = file_path.stat().st_size


        results.append({
            "source_name": row["source_name"],
            "file_name": row["file_pattern"],
            "schema_hash": actual_hash,
            "schema_valid": schema_status,
            "file_size": file_size,
            "file_arrival": file_arrival
        })

        if not file_arrival:
            schema_display = "NA"
        elif schema_status:
            schema_display = "VALID"
        else:
            schema_display = "INVALID"

        print(
            f"{row['source_name']:<30}"
            f"\tFile Arrival: {file_arrival:<7} "
            f"\tSchema: {schema_display:<7} "
            f"\tFile size: {file_size}"
        )

    output = pd.DataFrame(results)

    output_path = Path("metadata")
    output_path.mkdir(exist_ok=True)

    output.to_csv(
        output_path / "schema_validation.csv",
        index=False
    )

    print("\nSchema validation report created.")


if __name__ == "__main__":
    main()