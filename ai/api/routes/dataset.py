import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ai.api.dependencies import get_current_user, CurrentUser
from ai.infrastructure.db.session import get_db
from ai.services.analyst.dataset_service import process_and_save_dataset
from ai.services.rag.thread_service import (
    get_user_thread,
    save_or_update_thread,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class ProcessDatasetRequest(BaseModel):
    media: str
    thread_id: str
    path: str
    language: str | None = None
    document_name: str | None = None

@router.post("/process_dataset")
async def process_dataset(
    request: ProcessDatasetRequest,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):


    if os.path.exists(request.path):
        logger.debug(
            "Dataset upload details: file_size=%s extension=%s",
            os.path.getsize(request.path),
            os.path.splitext(request.path)[1],
        )
    else:
        raise HTTPException(
            status_code=400,
            detail="File path does not exist"
        )

    logger.debug("Checking analyst thread")

    thread = get_user_thread(
        db,
        request.thread_id,
        current_user.user_id,
    )


    if thread is None:
        logger.info("Creating new analyst thread")
        save_or_update_thread(
            db,
            request.thread_id,
            "New Analyst Chat",
            current_user.user_id,
            mode="analyst",
        )

    logger.info("Dataset preprocessing started")

    try:
        dataset, df, report_json = process_and_save_dataset(
            db=db,
            file_path=request.path,
            thread_id=request.thread_id,
            user_id=current_user.user_id,
            document_name=request.document_name,
        )

        logger.info(
            "Dataset preprocessing completed successfully: rows=%s columns=%s",
            len(df),
            len(df.columns),
        )

    except Exception as e:
        logger.exception("Dataset preprocessing failed")

        raise HTTPException(
            status_code=500,
            detail=f"Failed to preprocess dataset: {str(e)}"
        )

    return {
        "status": "success",
        "message": "Dataset preprocessed and stored",
        "rows": len(df),
        "cols": len(df.columns),
    }
