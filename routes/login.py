# login.py
import os
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from utils.auth import authenticate_user, create_access_token
from models.model import Token, Login

load_dotenv(".env")

login_root = APIRouter()


@login_root.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", email=user.email)


@login_root.post("/signIn", response_model=Token)
async def frontend_login_for_access_token(form_data: Login):
    user = authenticate_user(form_data.Email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    )
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer", email=user.email)
