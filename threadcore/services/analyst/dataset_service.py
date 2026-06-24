import os
from sqlalchemy.orm import Session
from threadcore.domains.analyst.repositories.dataset_repository import create_dataset
from threadcore.services.analyst.preprocess import run_preprocessing


def process_and_save_dataset(
    db: Session,
    file_path: str,
    thread_id: str,
    user_id: str,
):
    """Service to preprocess and save dataset metadata."""

    df, report_json = run_preprocessing(file_path)

    dataset = create_dataset(
        db=db,
        thread_id=thread_id,
        user_id=user_id,
        name=os.path.basename(file_path),
        file_path=file_path,
        file_type=file_path.split(".")[-1],
        row_count=str(len(df)),
        column_count=str(len(df.columns)),
        status="READY",
    )

    return dataset, df, report_json