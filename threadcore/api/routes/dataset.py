import logging
import os

from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy.orm import Session
from threadcore.infrastructure.db.session import get_db
from threadcore.services.analyst.dataset_service import process_and_save_dataset
from threadcore.services.rag.thread_service import (
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
    x_user_id: str = Header(None),
    db: Session = Depends(get_db),
):
    
    if not x_user_id:
        logger.error("Missing X-User-Id header")
        raise HTTPException(
            status_code=401,
            detail="X-User-Id header missing"
        )


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
        x_user_id,
    )


    if thread is None:
        logger.info("Creating new analyst thread")
        save_or_update_thread(
            db,
            request.thread_id,
            "New Analyst Chat",
            x_user_id,
            mode="analyst",
        )

    logger.info("Dataset preprocessing started")

    try:
        dataset, df, report_json = process_and_save_dataset(
            db=db,
            file_path=request.path,
            thread_id=request.thread_id,
            user_id=x_user_id,
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
