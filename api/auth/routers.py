from fastapi import APIRouter
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from auth.provider import Auth
from user.controllers import (
    register_user,
    signin_user,
)
from auth.models import (
    UserAuthResponseModel,
    SignInRequestModel,
    SignUpRequestModel,
)

router = APIRouter()
OAuth2 = HTTPBearer()
auth_handler = Auth()


@router.post("/v1/signup", response_model=UserAuthResponseModel)
def signup_api(user_details: SignUpRequestModel):
    """
    This sign-up API allow you to register your account, and return access token.
    """
    user = register_user(user_details)
    access_token = auth_handler.encode_token(user_details.email)
    refresh_token = auth_handler.encode_refresh_token(user_details.email)
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {
                "token": {"access_token": access_token, "refresh_token": refresh_token},
                "user": user,
            }
        ),
    )


@router.post("/v1/signin", response_model=UserAuthResponseModel)
def signin_api(user_details: SignInRequestModel):
    """
    This sign-in API allow you to obtain your access token.
    """
    user = signin_user(user_details.email, user_details.password)
    access_token = auth_handler.encode_token(user["email"])
    refresh_token = auth_handler.encode_refresh_token(user["email"])
    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {
                "token": {"access_token": access_token, "refresh_token": refresh_token},
                "user": user,
            }
        ),
    )


@router.get("/v1/refresh-token")
def refresh_token_api(refresh_token: str):
    """
    This refresh-token API allow you to obtain new access token.
    """
    new_token = auth_handler.refresh_token(refresh_token)
    return jsonable_encoder({"access_token": new_token})