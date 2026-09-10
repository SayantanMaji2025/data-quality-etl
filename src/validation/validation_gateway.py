import pandas as pd
from pathlib import Path


METADATA_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\src\validation\metadata"
)


def check_schema():

    path = METADATA_PATH / "schema_validation.csv"

    df = pd.read_csv(path)

    return (
        df["file_arrival"].all()
        and df["schema_valid"].all()
    )


def check_datatype():

    path = METADATA_PATH / "datatype_validation.csv"

    df = pd.read_csv(path)

    invalid = pd.to_numeric(
        df["invalid_count"],
        errors="coerce"
    )

    return (
        df["datatype_valid"].all()
        and (invalid.fillna(0) == 0).all()
    )


def check_business_rules():

    path = METADATA_PATH / "business_rule_validation.csv"

    df = pd.read_csv(path)

    # Only FAIL severity blocks the pipeline.
    blocking_failures = df[
        (df["severity"] == "FAIL")
        & (df["status"] == "FAIL")
    ]

    return blocking_failures.empty


def run_quality_gate():

    print("\n" + "=" * 80)
    print("DATA QUALITY GATE")
    print("=" * 80)

    schema_passed = check_schema()
    datatype_passed = check_datatype()
    business_rules_passed = check_business_rules()

    checks = {
        "Schema Validation": schema_passed,
        "Datatype Validation": datatype_passed,
        "Business Rule Validation": business_rules_passed,
    }

    for check_name, passed in checks.items():

        status = "PASS" if passed else "FAIL"

        print(
            f"{check_name:<30} {status}"
        )

    quality_gate_passed = all(checks.values())

    print("-" * 80)

    if quality_gate_passed:
        print("QUALITY GATE: PASSED")
    else:
        print("QUALITY GATE: FAILED")

    return quality_gate_passed


if __name__ == "__main__":

    success = run_quality_gate()

    if not success:
        raise SystemExit(1)