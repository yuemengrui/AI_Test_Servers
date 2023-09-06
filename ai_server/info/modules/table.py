# *_*coding:utf-8 *_*
# @Author : YueMengRui
import os
import cv2
import fitz
import uuid
import base64
import requests
import datetime
import numpy as np
from fastapi import APIRouter
from info import logger
from info.configs.base_configs import TEMP
from .protocol import TableRequest, BaseResponse
from fastapi.responses import JSONResponse
from info.utils.response_code import RET, error_map
from info.utils.box_segmentation import get_box
from info.utils.table_process import split_rows
from info.utils.ocr import get_ocr_byte_res

router = APIRouter()


# @router.api_route('/ai/ocr/table/v1', methods=['POST'], response_model=BaseResponse, summary="Table OCR")
# def table_ocr(table_req: TableRequest):
#     try:
#         img_data = base64.b64decode(table_req.image)
#         image = cv2.imdecode(np.asarray(bytearray(img_data), dtype='uint8'), cv2.IMREAD_COLOR)
#         image, boxes = get_box(image, **table_req.table_seg_configs)
#     except Exception as e:
#         logger.error(e)
#         return JSONResponse(BaseResponse(errcode=RET.PARAMERR, errmsg=error_map[RET.PARAMERR]).dict())
#
#     row_boxes = split_rows(boxes)  # 把所有表格分成一行一行
#     keys = []
#     for key_box in row_boxes[0]:
#         crop_img = image[key_box[1]:key_box[3], key_box[0]:key_box[2]]
#         ocr_res = get_ocr_byte_res(crop_img)
#         keys.append(ocr_res)
#
#     res = []
#
#     for row_box in row_boxes[1:]:
#         temp = {}
#         for i, box in enumerate(row_box):
#             ocr_res = get_ocr_byte_res(image[box[1]:box[3], box[0]:box[2]])
#             if i >= len(keys):
#                 k = "None"
#             else:
#                 k = keys[i]
#
#             temp[k] = ocr_res
#
#         res.append(temp)
#
#     return JSONResponse(BaseResponse(errcode=RET.OK, errmsg=error_map[RET.OK], data={'results': res}).dict())


@router.api_route('/ai/ocr/table', methods=['POST'], response_model=BaseResponse, summary="Table OCR")
def table_ocr(table_req: TableRequest):
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    if table_req.file_type == 1:
        file_path = os.path.join(TEMP, nowtime + uuid.uuid1().hex + '.pdf')
    else:
        file_path = os.path.join(TEMP, nowtime + uuid.uuid1().hex + '.jpg')

    try:
        file_data = requests.get(table_req.file_url).content
        with open(file_path, 'wb') as f:
            f.write(file_data)
    except Exception as e:
        logger.error({'EXCEPTION': e})
        return JSONResponse(BaseResponse(errcode=RET.FILEGETERR, errmsg=error_map[RET.FILEGETERR]).dict())

    image_path_list = []
    if table_req.file_type == 1:
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
    else:
        image_path_list.append(file_path)

    if len(image_path_list) == 0:
        logger.error({'DATA ERROR': 'image_path_list为空'})
        return JSONResponse(BaseResponse(errcode=RET.DATAERR, errmsg=error_map[RET.DATAERR]).dict())

    res = []

    for im_path in image_path_list:
        origin_img = cv2.imread(im_path)

        if origin_img is None:
            return JSONResponse(BaseResponse(errcode=RET.DATAERR, errmsg=error_map[RET.DATAERR] + ': 图片为空').dict())

        img, boxes = get_box(origin_img, **table_req.table_seg_configs)

        table = []
        for box in boxes:
            crop_img = img[box[1]:box[3], box[0]:box[2]]
            ocr_res = get_ocr_byte_res(crop_img)
            table.append({"box": box, "text": ocr_res})

        res.append(table)

    return JSONResponse(BaseResponse(errcode=RET.OK, errmsg=error_map[RET.OK], data={'results': res}).dict())
