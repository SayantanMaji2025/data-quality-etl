import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

OUTPUT_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\processed"
)

CUSTOMER_FILE = "olist_customers_dataset.csv"


def main():

    input_path = DATASET_PATH / CUSTOMER_FILE

    print("\nCustomer ETL")
    print("-" * 80)

    # ---------------------------------------------------------
    # Extract
    # ---------------------------------------------------------

    if not input_path.exists():

        print(f"Source file not found: {input_path}")
        return

    df = pd.read_csv(input_path)

    print(f"Source records: {len(df)}")

    # ---------------------------------------------------------
    # Transform
    # ---------------------------------------------------------

    customer_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_zip_code_prefix",
        "customer_city",
        "customer_state"
    ]

    df = df[customer_columns].copy()

    # Standardize string columns
    string_columns = [
        "customer_id",
        "customer_unique_id",
        "customer_city",
        "customer_state"
    ]

    for column in string_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # Enforce numeric datatype
    df["customer_zip_code_prefix"] = pd.to_numeric(
        df["customer_zip_code_prefix"],
        errors="coerce"
    ).astype("Int64")

    # ---------------------------------------------------------
    # Remove duplicate customer IDs as a safety measure
    # ---------------------------------------------------------

    before_dedup = len(df)

    df = df.drop_duplicates(
        subset=["customer_id"]
    )

    duplicates_removed = (
        before_dedup - len(df)
    )

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    OUTPUT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_PATH / "dim_customer.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print(f"Records after transformation: {len(df)}")
    print(f"Duplicates removed: {duplicates_removed}")
    print(f"Output: {output_path}")

    print("\nCustomer ETL completed.")


if __name__ == "__main__":
    main()