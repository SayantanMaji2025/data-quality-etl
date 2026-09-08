import pandas as pd
from pathlib import Path


METADATA_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\src\validation\metadata"
)

OUTPUT_PATH = METADATA_PATH / "validation_report.csv"


def build_report():

    reports = []

    # =========================================================
    # 1. Schema Validation
    # =========================================================

    df = pd.read_csv(METADATA_PATH / "schema_validation.csv")

    schema_report = pd.DataFrame({
        "source_name": df["source_name"],
        "validation_type": "schema_validation",
        "rule_id": "",
        "column_name": "",
        "total_records": "",
        "invalid_records": "",
        "invalid_percentage": "",
        "severity": "FAIL",
        "status": df["schema_valid"].map({
            True: "PASS",
            False: "FAIL"
        })
    })

    reports.append(schema_report)

    # =========================================================
    # 2. Datatype Validation
    # =========================================================

    df = pd.read_csv(METADATA_PATH / "datatype_validation.csv")

    datatype_report = pd.DataFrame({
        "source_name": df["source_name"],
        "validation_type": "datatype_validation",
        "rule_id": "",
        "column_name": df["column_name"],
        "total_records": "",
        "invalid_records": df["invalid_count"],
        "invalid_percentage": "",
        "severity": "FAIL",
        "status": df["datatype_valid"].map({
            True: "PASS",
            False: "FAIL"
        })
    })

    reports.append(datatype_report)

    # =========================================================
    # 3. Null Validation
    # =========================================================

    df = pd.read_csv(METADATA_PATH / "null_validation.csv")

    null_report = pd.DataFrame({
        "source_name": df["source_name"],
        "validation_type": "null_validation",
        "rule_id": "",
        "column_name": df["column_name"],
        "total_records": df["total_records"],
        "invalid_records": df["null_count"],
        "invalid_percentage": df["null_percentage"].round(2),
        "severity": "",
        "status": ""
    })

    reports.append(null_report)

    # =========================================================
    # 4. Duplicate Validation
    # =========================================================

    df = pd.read_csv(METADATA_PATH / "duplicate_validation.csv")

    duplicate_report = pd.DataFrame({
        "source_name": df["source_name"],
        "validation_type": "duplicate_validation",
        "rule_id": "",
        "column_name": df["duplicate_key"],
        "total_records": df["total_records"],
        "invalid_records": df["duplicate_records"],
        "invalid_percentage": (
            df["duplicate_records"] /
            df["total_records"] * 100
        ).round(2),
        "severity": "FAIL",
        "status": df["duplicate_valid"].map({
            True: "PASS",
            False: "FAIL"
        })
    })

    reports.append(duplicate_report)

    # =========================================================
    # 5. Business Rule Validation
    # =========================================================

    df = pd.read_csv(
        METADATA_PATH / "business_rule_validation.csv"
    )

    business_report = pd.DataFrame({
        "source_name": df["source_name"],
        "validation_type": "business_rule_validation",
        "rule_id": df["rule_id"],
        "column_name": df["column_name"],
        "total_records": df["total_records"],
        "invalid_records": df["invalid_records"],
        "invalid_percentage": (
            df["invalid_records"] /
            df["total_records"] * 100
        ).round(2),
        "severity": df["severity"],
        "status": df["status"]
    })

    reports.append(business_report)

    # =========================================================
    # Combine Reports
    # =========================================================

    validation_report = pd.concat(
        reports,
        ignore_index=True
    )

    validation_report.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nValidation report created.")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Total validation checks: {len(validation_report)}")


if __name__ == "__main__":
    build_report()