import sys
import time
from pathlib import Path
from datetime import datetime

from run_logger import log_pipeline_run


# Allow imports from src/validation
sys.path.append(
    str(Path(__file__).resolve().parents[1] / "validation")
)

from run_validation import main as run_validation_pipeline

from customer_etl import main as run_customer_etl
from order_etl import main as run_order_etl
from order_item_etl import main as run_order_item_etl
from payment_etl import main as run_payment_etl
from review_etl import main as run_review_etl
from product_etl import main as run_product_etl
from seller_etl import main as run_seller_etl


ETL_STEPS = [
    ("dim_customer", run_customer_etl),
    ("fact_order", run_order_etl),
    ("fact_order_item", run_order_item_etl),
    ("fact_payment", run_payment_etl),
    ("fact_review", run_review_etl),
    ("dim_product", run_product_etl),
    ("dim_seller", run_seller_etl),
]


def main():

    print("\n" + "=" * 80)
    print("DATA QUALITY ETL PIPELINE")
    print("=" * 80)

    pipeline_start_datetime = datetime.now()
    pipeline_start = time.time()

    completed_steps = 0
    failed_steps = 0

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    print("\n" + "-" * 80)
    print("Starting: Data Validation")
    print("-" * 80)

    validation_passed = run_validation_pipeline()

    if not validation_passed:

        end_time = datetime.now()

        log_pipeline_run(
            start_time=pipeline_start_datetime,
            end_time=end_time,
            validation_status="FAIL",
            etl_steps=len(ETL_STEPS),
            completed_steps=0,
            failed_steps=0,
            status="VALIDATION_FAILED"
        )

        print("\nETL pipeline stopped because validation failed.")

        return False

    print("\nData validation passed. Starting ETL.")

    # ---------------------------------------------------------
    # ETL
    # ---------------------------------------------------------

    for step_name, etl_function in ETL_STEPS:

        print("\n" + "-" * 80)
        print(f"Starting: {step_name}")
        print("-" * 80)

        step_start = time.time()

        try:

            etl_function()

            completed_steps += 1

        except Exception as error:

            elapsed = time.time() - step_start

            failed_steps += 1

            print(
                f"\nFAILED: {step_name}"
                f"\nError: {error}"
                f"\nExecution time: {elapsed:.2f} seconds"
            )

            print("\nETL pipeline stopped.")

            end_time = datetime.now()

            log_pipeline_run(
                start_time=pipeline_start_datetime,
                end_time=end_time,
                validation_status="PASS",
                etl_steps=len(ETL_STEPS),
                completed_steps=completed_steps,
                failed_steps=failed_steps,
                status="ETL_FAILED"
            )

            return False

        elapsed = time.time() - step_start

        print(
            f"\nCompleted: {step_name}"
            f"\nExecution time: {elapsed:.2f} seconds"
        )

    # ---------------------------------------------------------
    # Pipeline Summary
    # ---------------------------------------------------------

    pipeline_elapsed = time.time() - pipeline_start

    print("\n" + "=" * 80)
    print("PIPELINE SUMMARY")
    print("=" * 80)
    print(f"Validation:     {'PASS' if validation_passed else 'FAIL'}")
    print(f"ETL Steps:      {len(ETL_STEPS)}")
    print(f"Completed:      {completed_steps}")
    print(f"Failed:         {failed_steps}")
    print("Status:         SUCCESS")
    print(f"Total time:     {pipeline_elapsed:.2f} seconds")
    print("=" * 80)

    # ---------------------------------------------------------
    # Run Logging
    # ---------------------------------------------------------

    end_time = datetime.now()

    log_pipeline_run(
        start_time=pipeline_start_datetime,
        end_time=end_time,
        validation_status="PASS",
        etl_steps=len(ETL_STEPS),
        completed_steps=completed_steps,
        failed_steps=failed_steps,
        status="SUCCESS"
    )

    return True


if __name__ == "__main__":

    success = main()

    if not success:
        raise SystemExit(1)