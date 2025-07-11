from pydantic import BaseModel
from datetime import timedelta
from fastapi_jwt_auth import AuthJWT
from app.config import settings  # use your config

class AuthSettings(BaseModel):
    authjwt_secret_key: str = settings.authjwt_secret_key
    authjwt_access_token_expires: timedelta = timedelta(hours=1)  # ⏰ Set to 1 hour

@AuthJWT.load_config
def get_config():
    return AuthSettings()
