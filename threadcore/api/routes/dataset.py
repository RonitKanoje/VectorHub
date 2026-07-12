import os
from fastapi import APIRouter, Depends, HTTPException, Header, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json
from threadcore.infrastructure.db.session import get_db
from threadcore.services.analyst.dataset_service import process_and_save_dataset
from threadcore.services.rag.thread_service import (
    get_user_thread,
    save_or_update_thread,
)

router = APIRouter()


class ProcessDatasetRequest(BaseModel):
    media: str
    thread_id: str
    path: str
    language: str | None = None
    document_name: str | None = None


import os
import traceback
from fastapi import Depends, Header, HTTPException

@router.post("/process_dataset")
async def process_dataset(
    request: ProcessDatasetRequest,
    x_user_id: str = Header(None),
    db: Session = Depends(get_db),
):
    
    if not x_user_id:
        print("ERROR: Missing X-User-Id header")
        raise HTTPException(
            status_code=401,
            detail="X-User-Id header missing"
        )


    if os.path.exists(request.path):
        print(f"File size     : {os.path.getsize(request.path)} bytes")
        print(f"Extension     : {os.path.splitext(request.path)[1]}")
    else:
        raise HTTPException(
            status_code=400,
            detail="File path does not exist"
        )

    print("Checking thread...")

    thread = get_user_thread(
        db,
        request.thread_id,
        x_user_id,
    )


    if thread is None:
        print("Creating new analyst thread...")
        save_or_update_thread(
            db,
            request.thread_id,
            "New Analyst Chat",
            x_user_id,
            mode="analyst",
        )

    print("Calling process_and_save_dataset()...")

    try:
        dataset, df, report_json = process_and_save_dataset(
            db=db,
            file_path=request.path,
            thread_id=request.thread_id,
            user_id=x_user_id,
            document_name=request.document_name,
        )

        print("Dataset preprocessing completed successfully.")
        print(f"Rows          : {len(df)}")
        print(f"Columns       : {len(df.columns)}")
        print("========== PROCESS DATASET SUCCESS ==========\n")

    except Exception as e:
        print("\n========== PROCESS DATASET FAILED ==========")
        print("Exception Type :", type(e).__name__)
        print("Exception      :", str(e))
        traceback.print_exc()
        print("===========================================\n")

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
