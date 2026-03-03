from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    password: str = Field(min_length=8, max_length=72)
    repeat_password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    login: str
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    id: int
    login: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int