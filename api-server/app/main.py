"""
main file for exosphere apis
"""
import os
from beanie import init_beanie
from fastapi import FastAPI
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from pymongo import AsyncMongoClient
from fastapi.security import OAuth2PasswordBearer

# injecting singletons
from .singletons.logs_manager import LogsManager

# injecting middlewares
from .middlewares.unhandled_exceptions_middleware import (
    UnhandledExceptionsMiddleware,
)
from .middlewares.request_id_middleware import RequestIdMiddleware

# injecting databases
from .user.models.user_database_model import User
from .project.models.project_database_model import Project
from .satellite.models.satellite_database_model import Satellite

# injecting routers
from .user.routes import router as user_router
from .auth.routes import router as auth_router
from .project.routes import router as project_router
from .satellite.routes import router as satellite_router
 
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # begaining of the server
    logger = LogsManager().get_logger()
    logger.info("server starting")

    # initializing beanie
    client = AsyncMongoClient(os.getenv("MONGO_URI"))
    # Get the database name from environment variables.
    # If not set, use "default" to avoid errors when accessing client[db_name]
    # os.getenv can return None, which is not valid for dictionary-style access
    db_name = os.getenv("MONGO_DATABASE_NAME", "default")
    db = client[db_name]
    await init_beanie(db, document_models=[User, Project, Satellite])
    logger.info("beanie dbs initialized")

    # main logic of the server
    yield

    # end of the server
    logger.info("server shutting down")


app = FastAPI(
    lifespan=lifespan,
    title="Exosphere API Server",
    description="Exosphere API Server",
    version="0.1.0",
    contact={
        "name": "Nivedit Jain (Founder exosphere.host)",
        "email": "nivedit@exosphere.host",
    },
    license_info={
        "name": "Elastic License 2.0 (ELv2)",
        "url": "https://github.com/exospherehost/exosphere-api-server/blob/main/LICENSE",
    },
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# this middleware should be the first one
app.add_middleware(RequestIdMiddleware)

app.add_middleware(UnhandledExceptionsMiddleware)


@app.get("/health")
def health() -> dict:
    return {"message": "OK"}

# injecting routers
app.include_router(user_router)
app.include_router(auth_router)
app.include_router(project_router)
app.include_router(satellite_router)
