import pandas as pd
from pathlib import Path


DATASET_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\dataset"
)

OUTPUT_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\data\processed"
)

PRODUCT_FILE = "olist_products_dataset.csv"
TRANSLATION_FILE = "product_category_name_translation.csv"


def main():

    product_path = DATASET_PATH / PRODUCT_FILE
    translation_path = DATASET_PATH / TRANSLATION_FILE

    print("\nProduct ETL")
    print("-" * 80)

    # ---------------------------------------------------------
    # Extract
    # ---------------------------------------------------------

    if not product_path.exists():
        print(f"Product source not found: {product_path}")
        return

    if not translation_path.exists():
        print(f"Translation source not found: {translation_path}")
        return

    products = pd.read_csv(product_path)
    translation = pd.read_csv(translation_path)

    print(f"Product records: {len(products)}")
    print(f"Translation records: {len(translation)}")

    # ---------------------------------------------------------
    # Transform - standardize strings
    # ---------------------------------------------------------

    products["product_id"] = (
        products["product_id"]
        .astype("string")
        .str.strip()
    )

    products["product_category_name"] = (
        products["product_category_name"]
        .astype("string")
        .str.strip()
    )

    translation["product_category_name"] = (
        translation["product_category_name"]
        .astype("string")
        .str.strip()
    )

    translation["product_category_name_english"] = (
        translation["product_category_name_english"]
        .astype("string")
        .str.strip()
    )

    # ---------------------------------------------------------
    # Transform - numeric columns
    # ---------------------------------------------------------

    numeric_columns = [
        "product_name_lenght",
        "product_description_lenght",
        "product_photos_qty",
        "product_weight_g",
        "product_length_cm",
        "product_height_cm",
        "product_width_cm"
    ]

    for column in numeric_columns:

        products[column] = pd.to_numeric(
            products[column],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # Transform - category translation
    # ---------------------------------------------------------

    products = products.merge(
        translation[
            [
                "product_category_name",
                "product_category_name_english"
            ]
        ],
        on="product_category_name",
        how="left"
    )

    # ---------------------------------------------------------
    # Deduplication
    # ---------------------------------------------------------

    before_dedup = len(products)

    products = products.drop_duplicates(
        subset=["product_id"]
    )

    duplicates_removed = (
        before_dedup - len(products)
    )

    # ---------------------------------------------------------
    # Load
    # ---------------------------------------------------------

    OUTPUT_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        OUTPUT_PATH / "dim_product.csv"
    )

    products.to_csv(
        output_path,
        index=False
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    translated_count = (
        products["product_category_name_english"]
        .notna()
        .sum()
    )

    untranslated_count = (
        products["product_category_name_english"]
        .isna()
        .sum()
    )

    print(
        f"Records after transformation: {len(products)}"
    )

    print(
        f"Duplicates removed: {duplicates_removed}"
    )

    print(
        f"Translated categories: {translated_count}"
    )

    print(
        f"Untranslated categories: {untranslated_count}"
    )

    print(f"Output: {output_path}")

    print("\nProduct ETL completed.")


if __name__ == "__main__":
    main()