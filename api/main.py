from fastapi import FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from database.query import query_get, query_put, query_update
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from user import Auth, UserAuthRequestModel, UserAuthResponseModel, UserRequestModel, UserResponseModel, register_user, signin_user, update_user, get_all_users

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:4000",
    "http://localhost:19006"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()
auth_handler = Auth()

########## Auth APIs ##########

@app.post('/v1/signup', response_model=UserResponseModel)
def signup_api(user_details: UserRequestModel):
    """
    This sign-up API allow you to register your account.
    """
    user = register_user(user_details)
    return JSONResponse(status_code=200, content=jsonable_encoder(user))

@app.post('/v1/signin', response_model=UserAuthResponseModel)
def signin_api(user_details: UserAuthRequestModel):
    """
    This sign-in API allow you to obtain your access token.
    """
    user = signin_user(user_details.email, user_details.password)
    access_token = auth_handler.encode_token(user['email'])
    refresh_token = auth_handler.encode_refresh_token(user['email'])
    return JSONResponse(status_code=200, content={'token': {'access_token': access_token, 'refresh_token': refresh_token}, 'user': user})

@app.get('/v1/refresh-token')
def refresh_token_api(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    This refresh-token API allow you to obtain new access token.
    """
    refresh_token = credentials.credentials
    new_token = auth_handler.refresh_token(refresh_token)
    return {'access_token': new_token}


########## Users APIs ##########

@app.get("/v1/users", response_model=list[UserResponseModel])
def get_all_users_api(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    This user update API allow you to update user data.
    """
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        user = get_all_users()
        return JSONResponse(status_code=200, content=jsonable_encoder(user))
    return JSONResponse(status_code=401, content={'error': 'Faild to authorize'})

@app.post("/v1/user/update", response_model=UserResponseModel)
def update_user_api(user_details: UserRequestModel, credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    This user update API allow you to update user data.
    """
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        user = update_user(user_details)
        return JSONResponse(status_code=200, content=jsonable_encoder(user))
    return JSONResponse(status_code=401, content={'error': 'Faild to authorize'})


########## Test APIs ##########

@app.get('/secret')
def secret_data_api(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    This secret API is just for testing. Need access token to access this API.
    """
    token = credentials.credentials
    if(auth_handler.decode_token(token)):
        return 'Top Secret data only authorized users can access this info'

@app.get('/not-secret')
def not_secret_data_api():
    """
    This not-secret API is just for testing.
    """
    return 'Not secret data'
