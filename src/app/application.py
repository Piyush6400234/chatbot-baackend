from fastapi import FastAPI, Request
import toml
# from pydantic import BaseModel
import traceback
from typing import Optional
from src.app.api.router import api_router
from starlette.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from .lifetime import register_shutdown_event, register_startup_event
from fastapi.middleware.cors import CORSMiddleware

# class ExceptionResponseModel(BaseModel):
#     success: bool = False
#     exception_type: str
#     message: str
#     stack: Optional[str]


# class APIException(Exception):
#     def __init__(self, message: str):
#         self.message = message.lower()

# def get_app() -> FastAPI:

#     """

#     Get FastAPI application.

#     This is the main constructor of an application.

#     :return: application.
#     """
#     configure_logging()

#     file_path = "pyproject.toml"
    

#     with open(file_path, "r") as toml_file:
#         data = toml.loads(toml_file.read())

app = FastAPI(
    title="DropBox",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# register_startup_event(app)
# register_shutdown_event(app)




# app.add_middleware(ExceptionHandlerMiddleware)

# Main router for the API.

app.include_router(
    router=api_router,
    prefix="/api",
    # responses={
    # 400: {
    #     "model": ExceptionResponseModel,
    #     "description": "Bad Request",
    # },
    # 500: {
    #     "model": ExceptionResponseModel,
    #     "description": "Internal Server Error",
    #     },
    # },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or use "*" if you're testing
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Origin, X-Requested-With, Content-Type, Accept"],
)