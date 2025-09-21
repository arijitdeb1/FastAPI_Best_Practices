import asyncio
import os
from fastapi import FastAPI, HTTPException, Request
from pydantic_settings import BaseSettings
from functools import lru_cache
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import aioredis
import logging
from fastapi.logger import logger as fastapi_logger
from fastapi.responses import JSONResponse
from logging.handlers import RotatingFileHandler


class Settings(BaseSettings):
    app_name: str = "MyFastAPI App"
    admin_email: str
    database_url: str
    secret_key: str
    allowed_hosts: list = ["*"]
    debug: bool = False

    class Config:
        env_file = ".env"


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(),
        RotatingFileHandler("app.log", maxBytes=10*1024*1024, backupCount=5)
    ]
)


#settings = Settings()
app = FastAPI()

## RATE Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

## In Memory Cache
@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend())

## Redis Cache
'''
@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
'''    

## CORS setting
origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://yourdomain.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@lru_cache()
def get_settings():
    return Settings()

## if DEBUG is enabled, allow all hosts
@app.middleware("http")
async def validate_host(request, call_next):
    settings = get_settings()
    logger = logging.getLogger("fastapi")
    logger.info(f"Incoming request: {request.method} {request.url}")
    host = request.headers.get("host", "").split(":")[0]
    if settings.debug or host in settings.allowed_hosts:
        return await call_next(request)
    raise HTTPException(status_code=400, detail="Invalid host")

## Health Check
@app.get("/health")
async def health_check():
    # Perform checks (e.g., database connection, external services)
    all_systems_operational = True
    if all_systems_operational:
        return JSONResponse(content={"status": "healthy"}, status_code=200)
    else:
        return JSONResponse(content={"status": "unhealthy"}, status_code=503)
    
## RATE Limiter
@app.get("/")
@limiter.limit("1/minute")
async def root(request: Request):
    fastapi_logger.info("Root endpoint called")
    return {"message": "Hello World"}


@app.get("/info")
async def info():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "database_url": settings.database_url[:10] + "..."  # Truncate for security
    }

@app.get("/blocker")
async def blocking_endpoint():
    print("Blocking operation started...")
    #time.sleep(5)  # This blocks the entire event loop for 5 seconds
    await asyncio.sleep(10) # Correct way to pause an asynchronous function without blocking the event loop
    print("Blocking operation finished.")
    return {"message": "The event loop was blocked!"}

## In Memory Cache
@app.get("/cached-data")
@cache(expire=60)
async def get_cached_data():
    # Simulating a slow operation
    await asyncio.sleep(2)
    print("Slow operation finished.")
    return {"data": "This response is cached for 60 seconds"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
