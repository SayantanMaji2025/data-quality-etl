import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

OUTPUT_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\processed"
)

REVIEW_FILE = "olist_order_reviews_dataset.csv"


def main():

    input_path = DATASET_PATH / REVIEW_FILE

    print("\nReview ETL")
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
        "review_creation_date",
        "review_answer_timestamp"
    ]

    for column in datetime_columns:

        df[column] = pd.to_datetime(
            df[column],
            errors="coerce"
        )

    df["review_score"] = pd.to_numeric(
        df["review_score"],
        errors="coerce"
    ).astype("Int64")

    string_columns = [
        "review_id",
        "order_id",
        "review_comment_title",
        "review_comment_message"
    ]

    for column in string_columns:

        df[column] = (
            df[column]
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
            "review_id"
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
        OUTPUT_PATH / "fact_review.csv"
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
        f"Average review score: "
        f"{df['review_score'].mean():.2f}"
    )

    print(f"Output: {output_path}")

    print("\nReview ETL completed.")


if __name__ == "__main__":
    main()