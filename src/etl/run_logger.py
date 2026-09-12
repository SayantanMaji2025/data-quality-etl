import pandas as pd
from pathlib import Path
from datetime import datetime


METADATA_PATH = Path(
    r"C:\Users\sayan\OneDrive\Documents\data-quality-etl\metadata"
)

LOG_FILE = METADATA_PATH / "pipeline_runs.csv"


def log_pipeline_run(
    start_time,
    end_time,
    validation_status,
    etl_steps,
    completed_steps,
    failed_steps,
    status
):

    METADATA_PATH.mkdir(
        parents=True,
        exist_ok=True
    )

    run_record = pd.DataFrame([{
        "run_id": start_time.strftime("%Y%m%d%H%M%S"),
        "start_time": start_time,
        "end_time": end_time,
        "duration_seconds": round(
            (end_time - start_time).total_seconds(),
            2
        ),
        "validation_status": validation_status,
        "etl_steps": etl_steps,
        "completed_steps": completed_steps,
        "failed_steps": failed_steps,
        "status": status
    }])

    if LOG_FILE.exists():

        run_record.to_csv(
            LOG_FILE,
            mode="a",
            header=False,
            index=False
        )

    else:

        run_record.to_csv(
            LOG_FILE,
            index=False
        )

    print(f"Pipeline run logged: {LOG_FILE}")