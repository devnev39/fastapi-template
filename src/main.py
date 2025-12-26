import os
import signal

from contextlib import asynccontextmanager
from pathlib import Path

import markdown
import toml

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from jwt import ExpiredSignatureError
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.core.exceptions.client_exception import ClientException
from src.core.exceptions.token_exception import TokenException
from src.core.logger.context import error
from src.core.logger.context import request_id
from src.core.logger.log import logger
from src.core.middlewares.logger import LoggingASGIMiddleware
from src.core.security.get_current_user import get_current_user
from src.models.token import TokenDecrypted
from src.services.router import router

toml_path = Path(__file__).parent.parent / "pyproject.toml"
changelog_path = Path(__file__).parent.parent / "changelog.md"
config = None

print("TOML PATH : ")
print(toml_path)
if toml_path.exists() and toml_path.is_file():
    config = toml.load(toml_path)

app_version = "unknown"

if config:
    project = config.get("project", None)
    app_version = "unknown" if not project else project.get("version", "unknown")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to db
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        app.state.db = client.get_database(settings.DB_NAME)
        ping_response = await app.state.db.command("ping")
        if int(ping_response["ok"]) != 1:
            raise Exception("Problem connecting to database cluster.")
        yield
        client.close()
    except Exception as ex:
        logger.error("Error in starting application !", error=str(ex))
    finally:
        os.kill(os.getpid(), signal.SIGTERM)


app = FastAPI(lifespan=lifespan)

origins = settings.get_origins()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[str(i) for i in origins],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.add_middleware(LoggingASGIMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    origin = request.headers.get("origin")
    if origin in origins:
        cors_origin = origin
    else:
        cors_origin = ""

    response = JSONResponse(
        content={"detail": exc.detail, "trace_id": request_id.get()},
        status_code=exc.status_code,
    )
    response.headers.append("Access-Control-Allow-Origin", cors_origin)
    return response


@app.exception_handler(Exception)
async def client_server_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin")
    if origins[0] == "*":
        cors_origin = origins[0]
    elif origin in origins:
        cors_origin = origin
    else:
        cors_origin = ""

    response = None
    trace_id = request_id.get()
    if isinstance(exc, ClientException):
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": trace_id},
            status_code=exc.status_code,
        )
    elif isinstance(exc, ValidationError):
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": trace_id},
            status_code=422,
        )
    elif isinstance(exc, ExpiredSignatureError):
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": trace_id},
            status_code=403,
        )
    elif isinstance(exc, TokenException):
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": trace_id},
            status_code=401,
        )
    else:
        response = JSONResponse(
            content={
                "detail": "Internal server error",
                "trace_id": trace_id,
            },
            status_code=500,
        )

    response.headers.append("Access-Control-Allow-Origin", cors_origin)
    return response


app.include_router(router=router)


@app.get("/")
async def root():
    return {"message": "Application accepting request!"}


@app.get("/version")
async def version():
    return {"version": app_version}


@app.get("/changelog", response_class=HTMLResponse)
async def changelog(request: Request, user: TokenDecrypted = Depends(get_current_user)):
    data = ""
    with open(changelog_path, "r") as f:
        data = f.read()
    return markdown.markdown(data)
