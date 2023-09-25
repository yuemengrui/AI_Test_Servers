# *_*coding:utf-8 *_*
# @Author : YueMengRui
import os
import cv2
import fitz
import uuid
import shutil
import requests
import datetime
from fastapi import APIRouter
from info import logger
from info.configs.base_configs import TEMP
from .protocol import PDFRequest, BaseResponse
from fastapi.responses import JSONResponse
from info.utils.response_code import RET, error_map
from info.utils.ocr import get_ocr_general_res

router = APIRouter()


@router.api_route('/ai/ocr/pdf', methods=['POST'], response_model=BaseResponse, summary="PDF OCR")
def pdf_ocr(pdf_req: PDFRequest):
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

    file_path = os.path.join(TEMP, nowtime + uuid.uuid1().hex + '.pdf')

    try:
        file_data = requests.get(pdf_req.file_url).content
        with open(file_path, 'wb') as f:
            f.write(file_data)
    except Exception as e:
        logger.error({'EXCEPTION': e})
        return JSONResponse(BaseResponse(errcode=RET.FILEGETERR, errmsg=error_map[RET.FILEGETERR]).dict())

    image_path_list = []
    try:
        doc = fitz.open(file_path)
        pdf_pages = doc.page_count
    except Exception as e:
        logger.error({'EXCEPTION': e})
        return JSONResponse(
            BaseResponse(errcode=RET.DATAERR, errmsg=error_map[RET.DATAERR] + ': PDF转图片失败').dict())
    else:
        for i in range(pdf_pages):
            img_path = os.path.join(TEMP, str(nowtime) + uuid.uuid1().hex + '.jpg')
            try:
                page = doc[i]
                zoom_x = 2.0
                zoom_y = 2.0
                trans = fitz.Matrix(zoom_x, zoom_y)
                pm = page.get_pixmap(matrix=trans)
                pm.save(img_path)
            except Exception as e:
                logger.error({'EXCEPTION': e})
                return JSONResponse(
                    BaseResponse(errcode=RET.DATAERR, errmsg=error_map[RET.DATAERR] + ': PDF转图片失败').dict())
            else:
                image_path_list.append(img_path)

    if len(image_path_list) == 0:
        logger.error({'DATA ERROR': 'image_path_list为空'})
        return JSONResponse(BaseResponse(errcode=RET.DATAERR, errmsg=error_map[RET.DATAERR]).dict())

    res = []

    for j, im_path in enumerate(image_path_list):
        origin_img = cv2.imread(im_path)

        if origin_img is None:
            return JSONResponse(BaseResponse(errcode=RET.DATAERR, errmsg=error_map[RET.DATAERR] + ': 图片为空').dict())

        ocr_res = get_ocr_general_res(origin_img)
        res.append({'page': j, 'content': ocr_res})

    try:
        shutil.rmtree(file_path, ignore_errors=True)
        for img_path in image_path_list:
            shutil.rmtree(img_path, ignore_errors=True)
    except:
        pass

    return JSONResponse(BaseResponse(errcode=RET.OK, errmsg=error_map[RET.OK], data={'results': res}).dict())
