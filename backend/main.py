from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from schemas.responses import ApiResponse
from utils.exceptions import AppException
import logging
from config.logging_config import setup_logging
from config.database import async_engine
from routers import user, report, admin as admin_router
from routers.report import skills_router
from routers import artifact as artifact_router
from models import Base
from fastapi.staticfiles import StaticFiles

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 导入路由

app.include_router(user.router)
app.include_router(report.router)
app.include_router(skills_router)
app.include_router(artifact_router.router)
app.include_router(admin_router.router)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="images"), name="static")


# 注册全局异常处理
@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse(
            status_code=exc.status_code, message=exc.message, data=exc.data
        ).model_dump(),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    msg = (
        f"参数校验错误: {exc.errors()[0].get('msg')}"
        if exc.errors()
        else "参数校验失败"
    )
    return JSONResponse(
        status_code=422,
        content=ApiResponse(
            status_code=422, message=msg, data=exc.errors()
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def global_exception_handler(_request: Request, exc: Exception):
    logger.error(f"系统未捕获错误: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ApiResponse(
            status_code=500, message="服务器内部错误", data=None
        ).model_dump(),
    )


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI Backend!"}


@app.get("/health", response_model=ApiResponse)
async def check_health() -> ApiResponse:
    return ApiResponse(status_code=200, message="Healthy", data=None)
