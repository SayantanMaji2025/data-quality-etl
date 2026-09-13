import pandas as pd
from pathlib import Path


METADATA_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\metadata"
)

LOG_FILE = METADATA_PATH / "etl_step_runs.csv"


def log_etl_step(
    run_id,
    step_name,
    start_time,
    end_time,
    status,
    error_message=""
):

    METADATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    step_record = pd.DataFrame([{
        "run_id": run_id,
        "step_name": step_name,
        "start_time": start_time,
        "end_time": end_time,
        "duration_seconds": round(
            (end_time - start_time).total_seconds(),
            2
        ),
        "status": status,
        "error_message": error_message
    }])

    if LOG_FILE.exists():

        step_record.to_csv(
            LOG_FILE,
            mode="a",
            header=False,
            index=False
        )

    else:

        step_record.to_csv(
            LOG_FILE,
            index=False
        )

    print(
        f"ETL step logged: {step_name} → {status}"
    )