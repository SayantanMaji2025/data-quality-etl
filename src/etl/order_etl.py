import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

OUTPUT_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\processed"
)

ORDER_FILE = "olist_orders_dataset.csv"


def main():

    input_path = DATASET_PATH / ORDER_FILE

    print("\nOrder ETL")
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

    datetime_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date"
    ]

    for column in datetime_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    # Date dimension
    df["purchase_date"] = (
        df["order_purchase_timestamp"].dt.date
    )

    df["purchase_year"] = (
        df["order_purchase_timestamp"].dt.year
    )

    df["purchase_month"] = (
        df["order_purchase_timestamp"].dt.month
    )

    # Delivery duration
    df["delivery_days"] = (
        df["order_delivered_customer_date"]
        - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    # Delivery delay against estimated date
    df["delivery_delay_days"] = (
        df["order_delivered_customer_date"]
        - df["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    # Round derived measures
    df["delivery_days"] = (
        df["delivery_days"].round(2)
    )

    df["delivery_delay_days"] = (
        df["delivery_delay_days"].round(2)
    )

    # ---------------------------------------------------------
    # Deduplication
    # ---------------------------------------------------------

    before_dedup = len(df)

    df = df.drop_duplicates(
        subset=["order_id"]
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
        OUTPUT_PATH / "fact_order.csv"
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

    print(
        f"Orders with delivery date: "
        f"{df['order_delivered_customer_date'].notna().sum()}"
    )

    print(
        f"Orders with calculated delivery days: "
        f"{df['delivery_days'].notna().sum()}"
    )

    print(f"Output: {output_path}")

    print("\nOrder ETL completed.")


if __name__ == "__main__":
    main()