import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

OUTPUT_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\processed"
)

ORDER_ITEM_FILE = "olist_order_items_dataset.csv"


def main():

    input_path = DATASET_PATH / ORDER_ITEM_FILE

    print("\nOrder Item ETL")
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

    df["shipping_limit_date"] = pd.to_datetime(
        df["shipping_limit_date"],
        errors="coerce"
    )

    numeric_columns = [
        "price",
        "freight_value"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # Total item cost
    df["item_total"] = (
        df["price"] + df["freight_value"]
    ).round(2)

    # ---------------------------------------------------------
    # Deduplication
    # ---------------------------------------------------------

    before_dedup = len(df)

    df = df.drop_duplicates(
        subset=["order_id", "order_item_id"]
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
        OUTPUT_PATH / "fact_order_item.csv"
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
        f"Total item value: "
        f"{df['item_total'].sum():.2f}"
    )

    print(f"Output: {output_path}")

    print("\nOrder Item ETL completed.")


if __name__ == "__main__":
    main()