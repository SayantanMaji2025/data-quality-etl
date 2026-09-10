import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

OUTPUT_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\processed"
)

PAYMENT_FILE = "olist_order_payments_dataset.csv"


def main():

    input_path = DATASET_PATH / PAYMENT_FILE

    print("\nPayment ETL")
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

    df["payment_sequential"] = pd.to_numeric(
        df["payment_sequential"],
        errors="coerce"
    ).astype("Int64")

    df["payment_installments"] = pd.to_numeric(
        df["payment_installments"],
        errors="coerce"
    ).astype("Int64")

    df["payment_value"] = pd.to_numeric(
        df["payment_value"],
        errors="coerce"
    ).round(2)

    df["payment_type"] = (
        df["payment_type"]
        .astype("string")
        .str.strip()
    )

    # ---------------------------------------------------------
    # Deduplication
    # ---------------------------------------------------------

    before_dedup = len(df)

    df = df.drop_duplicates(
        subset=[
            "order_id",
            "payment_sequential"
        ]
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
        OUTPUT_PATH / "fact_payment.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    print(
        f"Records after transformation: {len(df)}"
    )

    print(
        f"Duplicates removed: {duplicates_removed}"
    )

    print(
        f"Total payment value: "
        f"{df['payment_value'].sum():.2f}"
    )

    print(f"Output: {output_path}")

    print("\nPayment ETL completed.")


if __name__ == "__main__":
    main()