# *_*coding:utf-8 *_*
import time
from info.configs import *
from fastapi import FastAPI
from info.utils.logger import MyLogger
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(title="AI_Test_Servers")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

logger = MyLogger()


@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"start request {request.method} {request.url.path}")
    start = time.time()

    response = await call_next(request)

    cost = time.time() - start
    logger.info(f"end request {request.method} {request.url.path} {cost:.3f}s")
    return response


from info.modules import register_router

register_router(app)
