from generate_schema_hash import main as run_schema_validation
from datatype_validator import main as run_datatype_validation
from null_validator import main as run_null_validation
from duplicate_validator import main as run_duplicate_validation
from business_rule_validator import main as run_business_rule_validation
from validation_gateway import run_quality_gate


VALIDATION_STEPS = [
    ("Schema Validation", run_schema_validation),
    ("Datatype Validation", run_datatype_validation),
    ("Null Validation", run_null_validation),
    ("Duplicate Validation", run_duplicate_validation),
    ("Business Rule Validation", run_business_rule_validation),
]


def main():

    print("\n" + "=" * 80)
    print("DATA VALIDATION PIPELINE")
    print("=" * 80)

    for step_name, validation_function in VALIDATION_STEPS:

        print("\n" + "-" * 80)
        print(f"Starting: {step_name}")
        print("-" * 80)

        try:
            validation_function()

        except Exception as error:

            print(f"\nFAILED: {step_name}")
            print(f"Error: {error}")
            print("\nValidation pipeline stopped.")
            return False

        print(f"\nCompleted: {step_name}")

    # ---------------------------------------------------------
    # Quality Gate
    # ---------------------------------------------------------

    print("\n")
    quality_gate_passed = run_quality_gate()

    if not quality_gate_passed:

        print("\nValidation pipeline FAILED.")
        return False

    print("\nValidation pipeline PASSED.")
    return True


if __name__ == "__main__":

    success = main()

    if not success:
        raise SystemExit(1)