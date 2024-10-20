import signal
import os
import toml
import markdown

from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from jwt import ExpiredSignatureError
from pydantic import ValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient

from src.config.settings import settings
from src.core.exceptions.token_exception import TokenException
from src.core.security.get_current_user import get_current_user
from src.models.token import TokenDecrypted
from src.services.router import router
from src.core.exceptions.client_exception import ClientException
from src.core.logger.log import Log, app_logger, AppLog

toml_path = Path(__file__).parent.parent / "pyproject.toml"
changelog_path = Path(__file__).parent.parent / "changelog.md"
config = None

print("TOML PATH : ")
print(toml_path)
if toml_path.exists() and toml_path.is_file():
    config = toml.load(toml_path)

app_version = "unknown"

if config:
    project = config.get("tool.poetry", None)
    app_version = "unknown" if not project else project.get("version", "unknown")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = AppLog(msg="App started", filename=__name__)
    app_logger.info(logger.model_dump())
    # Connect to db
    try:
        client = AsyncIOMotorClient(settings.MONGO_URI)
        app.state.db = client.get_database(settings.DB_NAME)
        ping_response = await app.state.db.command("ping")
        if int(ping_response["ok"]) != 1:
            raise Exception("Problem connecting to database cluster.")
        else:
            logger.update(AppLog(msg="Connected to database"))
            app_logger.info(logger.model_dump())
        yield
        logger.update(AppLog(extra="closing db connection !"))
        client.close()
    except Exception as ex:
        logger.update(AppLog(error=str(ex)))
        app_logger.error(logger.model_dump())
    finally:
        logger.update(AppLog(msg="App exiting...."))
        app_logger.info(logger.model_dump())
        os.kill(os.getpid(), signal.SIGTERM)


app = FastAPI(lifespan=lifespan)

origins = settings.get_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(i) for i in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    origin = request.headers.get("origin")
    if origin in origins:
        cors_origin = origin
    else:
        cors_origin = ""

    if getattr(request.state, "logger", None) is None:
        request.state.logger = Log(filename=__name__)
    request.state.logger.update(Log(error=str(exc), code=exc.status_code))
    app_logger.error(request.state.logger.model_dump(), exc_info=exc)
    response = JSONResponse(
        content={"detail": exc.detail, "trace_id": request.state.logger.trace_id},
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
    if getattr(request.state, "logger", None) is None:
        request.state.logger = Log(filename=__name__)
    if isinstance(exc, ClientException):
        request.state.logger.update(Log(error=str(exc), code=exc.status_code))
        app_logger.warning(request.state.logger.model_dump(), exc_info=exc)
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": request.state.logger.trace_id},
            status_code=exc.status_code,
        )
    elif isinstance(exc, ValidationError):
        request.state.logger.update(Log(error=str(exc), code=422))
        app_logger.warning(request.state.logger.model_dump(), exc_info=exc)
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": request.state.logger.trace_id},
            status_code=422,
        )
    elif isinstance(exc, ExpiredSignatureError):
        request.state.logger.update(Log(error=str(exc), code=403))
        app_logger.warning(request.state.logger.model_dump(), exc_info=exc)
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": request.state.logger.trace_id},
            status_code=403,
        )
    elif isinstance(exc, TokenException):
        request.state.logger.update(Log(error=str(exc), code=401))
        app_logger.warning(request.state.logger.model_dump(), exc_info=exc)
        response = JSONResponse(
            content={"detail": str(exc), "trace_id": request.state.logger.trace_id},
            status_code=401,
        )
    else:
        request.state.logger.update(Log(error=str(exc), code=500))
        app_logger.warning(request.state.logger.model_dump(), exc_info=exc)
        response = JSONResponse(
            content={
                "detail": "Internal server error",
                "trace_id": request.state.logger.trace_id,
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
    request.state.logger = Log(event="get changelog", user=user.sub)
    data = ""
    with open(changelog_path, "r") as f:
        data = f.read()
    return markdown.markdown(data)
