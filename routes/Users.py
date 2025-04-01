from fastapi import (
    Depends,
    HTTPException,
    status,
    APIRouter,
    Request,
    UploadFile,
    File,
    Form,
)
import jwt
from utils.nlp import getSummary, getPdfSummary
from models.model import TokenData, User
from typing import Annotated
from utils.auth import get_user
import os
from dotenv import load_dotenv
from test import process_file_and_text
from scrape import search_indian_kanoon

load_dotenv(".env")

users_root = APIRouter()


# Extract the token from the Authorization header
def get_token_from_header(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header[len("Bearer ") :]
    return token


# Dependency to retrieve the current user
async def get_current_user(
    token: Annotated[str, Depends(get_token_from_header)]
) -> User:
    print("Received token:", token)  # Debug statement
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")]
        )
        print("Decoded payload:", payload)  # Debug statement
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except Exception as e:
        print("Decoding error:", str(e))  # Debug statement
        raise credentials_exception

    user = get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


# Dependency to ensure the current user is active
async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# Get the current user details
@users_root.get("/users/me", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]
) -> User:
    return current_user


# Route for uploading only files (file is required)
@users_root.post("/fileUpload")
async def upload_file_route(
    file: Annotated[UploadFile, File(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    files_content = await file.read()
    result = getPdfSummary(files_content, file.filename)
    
    return result


# Route for submitting only text and getting summary (description is required)
@users_root.post("/text")
async def submit_text_route(
    description: Annotated[str, Form(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = getSummary(description)
    return result


# Route for submitting both file and text (both are required)
@users_root.post("/file_and_text")
async def upload_file_and_text_route(
    file: Annotated[UploadFile, File(...)],  # File is required
    description: Annotated[str, Form(...)],  # Text is required
    current_user: Annotated[User, Depends(get_current_user)],  # User authentication
):
    files_content = await file.read()
    result = process_file_and_text(files_content, file.filename, description)
    return result


@users_root.post("/cases")
async def submit_case_route(
    caseDetails: Annotated[str, Form(...)],
    current_user: Annotated[User, Depends(get_current_user)],
):
    result = search_indian_kanoon(caseDetails)
    return result
