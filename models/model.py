from pydantic import BaseModel


class Login(BaseModel):
    Email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    email: str


class TokenWithUserName(BaseModel):
    access_token: str
    token_type: str
    Name: str


class TokenData(BaseModel):
    email: str | None = None


class User(BaseModel):
    Name: str
    email: str | None = None
    disabled: bool | None = None


class signupUser(BaseModel):
    Name: str
    email: str | None = None
    hashed_password: str


class UserInDB(User):
    hashed_password: str
