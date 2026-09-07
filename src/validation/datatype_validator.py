import pandas as pd
from pathlib import Path


DATASET_PATH = Path(r"C:\Users\sayan\OneDrive\Documents\dataset")

MANIFEST_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\file_manifest.csv"
)

SCHEMA_CONFIG_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\schema_config.csv"
)


def validate_column_dtype(series, expected_dtype):

    # Nulls are handled separately in the Null Validation layer
    non_null_values = series.dropna()

    if expected_dtype == "string":
        return True, 0

    if expected_dtype == "integer":

        converted = pd.to_numeric(
            non_null_values,
            errors="coerce"
        )

        invalid_mask = converted.isna() | (converted % 1 != 0)

        invalid_count = invalid_mask.sum()

        return invalid_count == 0, invalid_count

    if expected_dtype == "float":

        converted = pd.to_numeric(
            non_null_values,
            errors="coerce"
        )

        invalid_count = converted.isna().sum()

        return invalid_count == 0, invalid_count

    if expected_dtype == "datetime":

        converted = pd.to_datetime(
            non_null_values,
            errors="coerce"
        )

        invalid_count = converted.isna().sum()

        return invalid_count == 0, invalid_count

    return False, len(non_null_values)


def main():

    manifest = pd.read_csv(MANIFEST_PATH)

    schema_config = pd.read_csv(SCHEMA_CONFIG_PATH)

    results = []

    for _, manifest_row in manifest.iterrows():

        source_name = manifest_row["source_name"]
        file_name = manifest_row["file_pattern"]

        file_path = DATASET_PATH / file_name

        print(f"\n{source_name}")
        print("-" * 80)
        schema_config = pd.read_csv(SCHEMA_CONFIG_PATH)

        if not file_path.exists():

            print("File not found")

            continue

        df = pd.read_csv(file_path)

        source_schema = schema_config[
            schema_config["source_name"] == source_name
        ]

        for _, schema_row in source_schema.iterrows():

            column_name = schema_row["column_name"]
            expected_dtype = schema_row["expected_dtype"]

            if column_name not in df.columns:

                results.append({
                    "source_name": source_name,
                    "file_name": file_name,
                    "column_name": column_name,
                    "expected_dtype": expected_dtype,
                    "datatype_valid": False,
                    "invalid_count": "COLUMN_NOT_FOUND"
                })

                print(
                    f"{column_name:<35}"
                    f"Expected: {expected_dtype:<10}"
                    f"Status: COLUMN NOT FOUND"
                )

                continue

            valid, invalid_count = validate_column_dtype(
                df[column_name],
                expected_dtype
            )

            results.append({
                "source_name": source_name,
                "file_name": file_name,
                "column_name": column_name,
                "expected_dtype": expected_dtype,
                "datatype_valid": valid,
                "invalid_count": invalid_count
            })

            print(
                f"{column_name:<35}"
                f"Expected: {expected_dtype:<10}"
                f"Status: {'VALID' if valid else 'INVALID':<8}"
                f"Invalid: {invalid_count}"
            )

    output = pd.DataFrame(results)

    output_path = Path("metadata")
    output_path.mkdir(exist_ok=True)

    output.to_csv(
        output_path / "datatype_validation.csv",
        index=False
    )

    print("\nDatatype validation report created.")


if __name__ == "__main__":
    main()