from pydantic import BaseModel


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
