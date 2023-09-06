# *_*coding:utf-8 *_*
# @Author : YueMengRui
from pydantic import BaseModel, Field, AnyUrl
from typing import Dict, Literal


class BaseResponse(BaseModel):
    errcode: int
    errmsg: str
    data: dict = {}


class TableRequest(BaseModel):
    # image: str = Field(default=None, repr=False, description="图片base64编码，(不包含base64头)")
    file_url: AnyUrl = Field(description="文件URL")
    file_type: Literal["PDF", "IMAGE"] = Field(description="文件类型")
    table_seg_configs: Dict = Field(default=dict(), description="表格分割超参数")
