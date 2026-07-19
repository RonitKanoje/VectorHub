from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy.orm import Session
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from threadcore.core.config import settings
from threadcore.services.rag.thread_service import (
    get_user_thread as get_thread_for_user,
)

security = HTTPBearer(auto_error=True)


class CurrentUser(BaseModel):
    user_id: str
    service: str


def get_chatbot(request: Request):
    # Reusing the same chatbot instance for all requests, as it is stateless and thread-safe
    return request.app.state.chatbot


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:


    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.internal_api_secret,
            algorithms=["HS256"],
        )

        if not isinstance(payload, dict):
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = payload.get("user_id")
        service = payload.get("service")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        if service != "express":
            raise HTTPException(status_code=401, detail="Invalid token")

        return CurrentUser(
            user_id=user_id,
            service=service,
        )

    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    except InvalidTokenError as e:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise



def ensure_thread_access(db: Session, thread_id: str, user_id: str):
   
    thread = get_thread_for_user(db, thread_id, user_id)

    if thread is None:
        raise HTTPException(status_code=404, detail="invalid_thread_id")

    return thread