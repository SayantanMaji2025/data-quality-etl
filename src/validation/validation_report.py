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

ERROR_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\errors\business_rules"
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

    values = pd.to_numeric(
        df[column_name],
        errors="coerce"
    )

    invalid_mask = (
        df[column_name].notna()
        & (values < min_value)
    )

    return invalid_mask


def validate_range(df, column_name, rule_value):

    min_value, max_value = map(
        float,
        rule_value.split("|")
    )

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

    condition_value, target_column = (
        rule_value.split("|")
    )

    condition_mask = (
        df[condition_column].astype(str)
        == condition_value
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

    reference_values = set(
        reference_df[reference_column].dropna()
    )

    invalid_mask = (
        df[column_name].notna()
        & ~df[column_name].isin(reference_values)
    )

    return invalid_mask


def main():

    manifest = pd.read_csv(
        MANIFEST_PATH
    )

    business_rules = pd.read_csv(
        BUSINESS_RULES_PATH
    )

    results = []

    # Cache loaded datasets so that reference tables
    # do not need to be read repeatedly.
    dataframes = {}

    for _, manifest_row in manifest.iterrows():

        source_name = manifest_row["source_name"]
        file_name = manifest_row["file_pattern"]

        file_path = DATASET_PATH / file_name

        if not file_path.exists():
            continue

        dataframes[source_name] = pd.read_csv(
            file_path
        )

    for source_name, df in dataframes.items():

        print(f"\n{source_name}")
        print("-" * 80)

        source_rules = business_rules[
            business_rules["source_name"]
            == source_name
        ]

        for _, rule in source_rules.iterrows():

            rule_id = rule["rule_id"]
            rule_type = rule["rule_type"]
            column_name = rule["column_name"]

            secondary_column = rule[
                "secondary_column"
            ]

            reference_source = rule[
                "reference_source"
            ]

            reference_column = rule[
                "reference_column"
            ]

            rule_value = rule["rule_value"]
            severity = rule["severity"]

            total_records = len(df)

            # -------------------------------------------------
            # Validate configured columns
            # -------------------------------------------------

            required_columns = [column_name]

            if (
                rule_type == "date_order"
                and pd.notna(secondary_column)
                and secondary_column != ""
            ):
                required_columns.append(
                    secondary_column
                )

            missing_columns = [
                column
                for column in required_columns
                if column not in df.columns
            ]

            if missing_columns:

                results.append({
                    "rule_id": rule_id,
                    "source_name": source_name,
                    "column_name": column_name,
                    "rule_type": rule_type,
                    "severity": severity,
                    "total_records": total_records,
                    "invalid_records": "COLUMN_NOT_FOUND",
                    "status": "FAIL"
                })

                print(
                    f"{rule_id:<10}"
                    f"Type: {rule_type:<25}"
                    f"Status: COLUMN NOT FOUND"
                )

                continue

            # -------------------------------------------------
            # Execute validation rule
            # -------------------------------------------------

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

                invalid_mask = validate_date_order(
                    df,
                    column_name,
                    secondary_column
                )

            elif rule_type == "conditional_not_null":

                invalid_mask = validate_conditional_not_null(
                    df,
                    column_name,
                    rule_value
                )

            elif rule_type == "referential_integrity":

                if reference_source not in dataframes:

                    results.append({
                        "rule_id": rule_id,
                        "source_name": source_name,
                        "column_name": column_name,
                        "rule_type": rule_type,
                        "severity": severity,
                        "total_records": total_records,
                        "invalid_records": "REFERENCE_NOT_FOUND",
                        "status": "FAIL"
                    })

                    print(
                        f"{rule_id:<10}"
                        f"Type: {rule_type:<25}"
                        f"Status: REFERENCE NOT FOUND"
                    )

                    continue

                reference_df = dataframes[
                    reference_source
                ]

                if reference_column not in reference_df.columns:

                    results.append({
                        "rule_id": rule_id,
                        "source_name": source_name,
                        "column_name": column_name,
                        "rule_type": rule_type,
                        "severity": severity,
                        "total_records": total_records,
                        "invalid_records": "REFERENCE_COLUMN_NOT_FOUND",
                        "status": "FAIL"
                    })

                    print(
                        f"{rule_id:<10}"
                        f"Type: {rule_type:<25}"
                        f"Status: REFERENCE COLUMN NOT FOUND"
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

            # -------------------------------------------------
            # Calculate result
            # -------------------------------------------------

            invalid_count = int(
                invalid_mask.sum()
            )

            status = (
                "FAIL"
                if invalid_count > 0
                else "PASS"
            )

            # -------------------------------------------------
            # Extract failed records
            # -------------------------------------------------

            if invalid_count > 0:

                ERROR_PATH.mkdir(
                    parents=True,
                    exist_ok=True
                )

                error_file = (
                    ERROR_PATH
                    / f"{rule_id}.csv"
                )

                df.loc[invalid_mask].to_csv(
                    error_file,
                    index=False
                )

                print(
                    f"Error records written: {error_file}"
                )

            results.append({
                "rule_id": rule_id,
                "source_name": source_name,
                "column_name": column_name,
                "rule_type": rule_type,
                "severity": severity,
                "total_records": total_records,
                "invalid_records": invalid_count,
                "status": status
            })

            print(
                f"{rule_id:<10}"
                f"Type: {rule_type:<25}"
                f"Invalid: {invalid_count:<8}"
                f"Status: {status}"
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
        output_path / "business_rule_validation.csv",
        index=False
    )

    print(
        "\nBusiness rule validation report created."
    )




if __name__ == "__main__":
    main()