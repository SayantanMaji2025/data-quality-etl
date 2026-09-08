import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

MANIFEST_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\file_manifest.csv"
)

BUSINESS_RULES_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\config\business_rules.csv"
)


def validate_allowed_values(df, column_name, rule_value):

    allowed_values = rule_value.split("|")

    invalid_mask = (
        df[column_name].notna()
        & ~df[column_name].isin(allowed_values)
    )

    return invalid_mask


def validate_min_value(df, column_name, rule_value):

    min_value = float(rule_value)

    invalid_mask = (
        df[column_name].notna()
        & (pd.to_numeric(df[column_name], errors="coerce") < min_value)
    )

    return invalid_mask


def validate_range(df, column_name, rule_value):

    min_value, max_value = map(float, rule_value.split("|"))

    values = pd.to_numeric(
        df[column_name],
        errors="coerce"
    )

    invalid_mask = (
        df[column_name].notna()
        & (
            (values < min_value)
            | (values > max_value)
        )
    )

    return invalid_mask


def validate_date_order(
    df,
    column_name,
    secondary_column
):

    first_date = pd.to_datetime(
        df[column_name],
        errors="coerce"
    )

    second_date = pd.to_datetime(
        df[secondary_column],
        errors="coerce"
    )

    # Only compare records where both dates exist
    comparison_mask = (
        first_date.notna()
        & second_date.notna()
    )

    invalid_mask = (
        comparison_mask
        & (first_date > second_date)
    )

    return invalid_mask

def validate_conditional_not_null(
    df,
    condition_column,
    rule_value
):
    """
    Validate that a target column is not null
    when a condition is satisfied.

    rule_value format:
    condition_value|target_column
    """

    condition_value, target_column = rule_value.split("|")

    condition_mask = (
        df[condition_column].astype(str) == condition_value
    )

    invalid_mask = (
        condition_mask
        & df[target_column].isna()
    )

    return invalid_mask
def validate_referential_integrity(
    df,
    column_name,
    reference_df,
    reference_column
):
    """
    Check whether every non-null value in the source column
    exists in the reference column.
    """

    reference_values = set(
        reference_df[reference_column].dropna()
    )

    invalid_mask = (
        df[column_name].notna()
        & ~df[column_name].isin(reference_values)
    )

    return invalid_mask
def main():

    manifest = pd.read_csv(MANIFEST_PATH)

    business_rules = pd.read_csv(
        BUSINESS_RULES_PATH
    )

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

        source_rules = business_rules[
            business_rules["source_name"] == source_name
        ]

        for _, rule in source_rules.iterrows():

            rule_id = rule["rule_id"]
            rule_type = rule["rule_type"]
            column_name = rule["column_name"]
            secondary_column = rule["secondary_column"]
            rule_value = rule["rule_value"]
            severity = rule["severity"]

            if column_name not in df.columns:

                print(
                    f"{rule_id:<10}"
                    f"Column not found: {column_name}"
                )

                continue

            if rule_type == "allowed_values":

                invalid_mask = validate_allowed_values(
                    df,
                    column_name,
                    rule_value
                )

            elif rule_type == "min_value":

                invalid_mask = validate_min_value(
                    df,
                    column_name,
                    rule_value
                )

            elif rule_type == "range":

                invalid_mask = validate_range(
                    df,
                    column_name,
                    rule_value
                )

            elif rule_type == "date_order":

                if secondary_column not in df.columns:

                    print(
                        f"{rule_id:<10}"
                        f"Column not found: {secondary_column}"
                    )

                    continue

                invalid_mask = validate_date_order(
                    df,
                    column_name,
                    secondary_column
                )
            elif rule_type == "conditional_not_null":

                condition_column = column_name

                condition_value, target_column = rule_value.split("|")

                if target_column not in df.columns:
                    print(
                        f"{rule_id:<10}"
                        f"Column not found: {target_column}"
                    )

                    continue

                invalid_mask = validate_conditional_not_null(
                    df,
                    condition_column,
                    rule_value
                )
            elif rule_type == "referential_integrity":

                reference_source = rule["reference_source"]
                reference_column = rule["reference_column"]

                reference_manifest = manifest[
                    manifest["source_name"] == reference_source
                    ]

                if reference_manifest.empty:
                    print(
                        f"{rule_id:<10}"
                        f"Reference source not found: {reference_source}"
                    )
                    continue

                reference_file = reference_manifest.iloc[0]["file_pattern"]

                reference_path = DATASET_PATH / reference_file

                if not reference_path.exists():
                    print(
                        f"{rule_id:<10}"
                        f"Reference file not found: {reference_file}"
                    )
                    continue

                reference_df = pd.read_csv(reference_path)

                if reference_column not in reference_df.columns:
                    print(
                        f"{rule_id:<10}"
                        f"Reference column not found: {reference_column}"
                    )
                    continue

                invalid_mask = validate_referential_integrity(
                    df,
                    column_name,
                    reference_df,
                    reference_column
                )
            else:
                print(
                    f"{rule_id:<10}"
                    f"Unsupported rule type: {rule_type}"
                )

                continue

            invalid_count = invalid_mask.sum()

            status = (
                "PASS"
                if invalid_count == 0
                else severity
            )

            results.append({
                "rule_id": rule_id,
                "source_name": source_name,
                "column_name": column_name,
                "rule_type": rule_type,
                "severity": severity,
                "total_records": len(df),
                "invalid_records": invalid_count,
                "status": status
            })

            print(
                f"{rule_id:<10}"
                f"Type: {rule_type:<30}"
                f"Invalid: {invalid_count:<8}"
                f"Status: {status}"
            )

    output = pd.DataFrame(results)

    output_path = Path("metadata")
    output_path.mkdir(exist_ok=True)

    output.to_csv(
        output_path / "business_rule_validation.csv",
        index=False
    )

    print("\nBusiness rule validation report created.")


if __name__ == "__main__":
    main()