import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

OUTPUT_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\processed"
)

SELLER_FILE = "olist_sellers_dataset.csv"


def main():

    input_path = DATASET_PATH / SELLER_FILE

    print("\nSeller ETL")
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

    df["seller_id"] = (
        df["seller_id"]
        .astype("string")
        .str.strip()
    )

    df["seller_zip_code_prefix"] = pd.to_numeric(
        df["seller_zip_code_prefix"],
        errors="coerce"
    ).astype("Int64")

    df["seller_city"] = (
        df["seller_city"]
        .astype("string")
        .str.strip()
    )

    df["seller_state"] = (
        df["seller_state"]
        .astype("string")
        .str.strip()
        .str.upper()
    )

    # ---------------------------------------------------------
    # Deduplication
    # ---------------------------------------------------------

    before_dedup = len(df)

    df = df.drop_duplicates(
        subset=["seller_id"]
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
        OUTPUT_PATH / "dim_seller.csv"
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
        f"States represented: {df['seller_state'].nunique()}"
    )

    print(f"Output: {output_path}")

    print("\nSeller ETL completed.")


if __name__ == "__main__":
    main()