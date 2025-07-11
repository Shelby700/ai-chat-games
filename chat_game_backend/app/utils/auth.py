from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from app.config import settings

class AuthSettings(BaseModel):
    authjwt_secret_key: str = settings.JWT_SECRET_KEY

@AuthJWT.load_config
def get_config():
    return AuthSettings()
