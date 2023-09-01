# *_*coding:utf-8 *_*
# @Author : YueMengRui
from pydantic import BaseModel, Field
from typing import Dict


class BaseResponse(BaseModel):
    errcode: int
    errmsg: str
    data: dict = {}


class TableRequest(BaseModel):
    image: str = Field(description="图片base64编码，(不包含base64头)")
    table_seg_configs: Dict = Field(default=dict(), description="表格分割超参数")
