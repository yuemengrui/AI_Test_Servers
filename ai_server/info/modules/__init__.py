# *_*coding:utf-8 *_*
from fastapi import FastAPI
from . import table
from . import pdf


def register_router(app: FastAPI):
    app.include_router(router=table.router, prefix="", tags=["Table OCR"])
    app.include_router(router=pdf.router, prefix="", tags=["PDF OCR"])
