from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    account: str
    password: str

    model_config = {
        "json_schema_extra": {
            "example": {"account": "test@gmail.com", "password": "test1234"},
        }
    }


class Token(BaseModel):
    access_token: str


class User(BaseModel):
    id: int
    account: str
    password: str
    is_disabled: bool
    role: str
