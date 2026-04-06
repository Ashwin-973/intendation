

import uvicorn
import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from typing import AsyncIterator

'''# path bootstrap (so `data.py` at server root is importable)
_server_root = Path(__file__).resolve().parents[1]
if str(_server_root) not in sys.path:
    sys.path.insert(0, str(_server_root))'''

from src.api import router
from src.logger import setup_logging,get_logger
from src.middleware import (
    ExceptionMiddleware,
    pydantic_validation_exception_handler,
    shelby_exception_handler,
    generic_exception_handler
)
from src.exceptions import ShelbyBaseException
from src.schemas import HealthResponse,ComponentHealth

'''BOOT LOGGING'''
setup_logging("DEBUG")
logger=get_logger(__name__)

APP_VERSION="1.1.0"

'''LIFESPAN'''
@asynccontextmanager
async def cars_lifespan(app:FastAPI)->AsyncIterator[None]:
    logger.info("[MAIN] starting Shelby API server")

    logger.info("[MAIN] revving car engine...")
    app.state.engine_loaded=True
    app.state.app_version=APP_VERSION

    logger.info("[MAIN] car engine can melt balls of steel")

    yield None

    logger.info("[MAIN] closing the shelby garage")
    app.state.engine_loaded=False
    del app.state.app_version

    logger.info("[MAIN] 7000+ RPM . goodbye")


'''APPLICATION'''

def create_app()->FastAPI:
    application=FastAPI(
        title="Shelby American",
        description="A gritty, passionate, and fast-paced California workshop",
        version=APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=cars_lifespan
    )

    #middleware
    application.add_middleware(ExceptionMiddleware) #! Note: Starlette middleware runs outermost-first (LIFO registration order)

    #exception handlers
    application.add_exception_handler(RequestValidationError,pydantic_validation_exception_handler) #*exception handlers are called only if middleware fails to catch an exception or re-raises an exception
    application.add_exception_handler(ShelbyBaseException,shelby_exception_handler)
    application.add_exception_handler(Exception,generic_exception_handler)

    #routers
    application.include_router(router)

    return application




app=create_app()


'''HEALTH ENDPOINTS'''

@app.get("/",tags=["meta"],description="root endpoint")
def welcome()->dict:
    return {
        "message": "Welcome to Shelby American . Get Ready to dive into the world of fast,sexy and exotic cars . Buckle Up!!",
        "docs": "/docs",
        "health": "/health",
        "version": app.state.app_version,
    }


@app.get("/health",response_model=HealthResponse)
def health_check()->HealthResponse:

    from data import CAR_DB

    db_ok=True if CAR_DB is not None and isinstance(CAR_DB,list) else False
    engine_ok=getattr(app.state,"engine_loaded",False)

    components={
        "database":ComponentHealth(
            status="ok" if db_ok else "down",
            message=f"{len(CAR_DB)} cars loaded" if db_ok else "CAR_DB is None"
        ),
        "engine":ComponentHealth(
            status="ok" if engine_ok else "down",
            message="engine ready" if engine_ok else "engine still revving"
        )
    }

    overall="ok" if(c.status=="ok" for c in components) else "degraded"

    return HealthResponse(
        status=overall,
        version=app.state.app_version,
        components=components
    )
    

'''RUNNER'''

if __name__=="__main__":
    uvicorn.run(
        app="src.main:app",
        reload=True,
        log_level="warning"
    )