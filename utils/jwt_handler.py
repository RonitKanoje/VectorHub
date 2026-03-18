from dotenv import load_dotenv
import os
from fastapi.security import OAuth2PasswordBearer
import jwt
import time
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database.postgres.userdb import get_db, UserDB

load_dotenv()

ALGORITHM = "HS256"
SECRET_KEY = os.getenv("SESSION_SECRET_KEY")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: int = 3600):
    to_encode = data.copy()
    to_encode.update({"exp": time.time() + expires_delta})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

# Auth Dependencies

def get_current_user(token: str = Depends(oauth2_scheme),db: Session = Depends(get_db)):
    try:
        payload = verify_token(token)
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise Exception("Invalid token: user_id missing")
        # Fetch user from DB
        user = db.query(UserDB).filter(UserDB.id == user_id).first()
        if user is None:
            raise Exception("User not found")
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

def get_current_active_user(current_user: UserDB = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

