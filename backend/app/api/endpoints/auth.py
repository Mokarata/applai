from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_user_service
from app.core import get_logger
from app.core.security import create_access_token
from app.db import get_db
from app.schemas.token import Token
from app.services.user_service import UserService

router = APIRouter()
logger = get_logger(__name__)


@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(get_user_service),
) -> Token:
    """OAuth2-compatible token login, get an access token for future requests."""
    user = user_service.authenticate_user(
        email=form_data.username, password=form_data.password
    )
    if not user:
        logger.warning(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"User {user.email} successfully authenticated.")
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token, token_type="bearer")
