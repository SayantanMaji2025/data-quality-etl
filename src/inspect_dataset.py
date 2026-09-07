import pandas as pd
from pathlib import Path

DATASET_PATH = Path(r"C:\Users\sayan\OneDrive\Documents\dataset")


def inspect_file(file_path):
    df = pd.read_csv(file_path, nrows=5)

    print("\n" + "=" * 70)
    print(f"FILE: {file_path.name}")
    print("=" * 70)

    print("\nColumns:")
    for column in df.columns:
        print(f"  - {column}")

    print("\nSample data:")
    print(df.to_string(index=False))


def main():
    csv_files = sorted(DATASET_PATH.glob("*.csv"))

    print(f"Found {len(csv_files)} CSV files.")

    for file_path in csv_files:
        inspect_file(file_path)


if __name__ == "__main__":
    main()