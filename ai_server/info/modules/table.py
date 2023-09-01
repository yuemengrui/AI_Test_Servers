# *_*coding:utf-8 *_*
# @Author : YueMengRui
import cv2
import base64
import numpy as np
from fastapi import APIRouter
from info import logger
from .protocol import TableRequest, BaseResponse
from fastapi.responses import JSONResponse
from info.utils.response_code import RET, error_map
from info.utils.box_segmentation import get_box
from info.utils.table_process import split_rows
from info.utils.ocr import get_ocr_byte_res

router = APIRouter()


@router.api_route('/ai/ocr/table', methods=['POST'], response_model=BaseResponse, summary="Table OCR")
def table_ocr(table_req: TableRequest):
    try:
        img_data = base64.b64decode(table_req.image)
        image = cv2.imdecode(np.asarray(bytearray(img_data), dtype='uint8'), cv2.IMREAD_COLOR)
        image, boxes = get_box(image, **table_req.table_seg_configs)
    except Exception as e:
        logger.error(e)
        return JSONResponse(BaseResponse(errcode=RET.PARAMERR, errmsg=error_map[RET.PARAMERR]).dict())

    row_boxes = split_rows(boxes)  # 把所有表格分成一行一行
    keys = []
    for key_box in row_boxes[0]:
        crop_img = image[key_box[1]:key_box[3], key_box[0]:key_box[2]]
        ocr_res = get_ocr_byte_res(crop_img)
        keys.append(ocr_res)

    res = []

    for row_box in row_boxes[1:]:
        temp = {}
        for i, box in enumerate(row_box):
            ocr_res = get_ocr_byte_res(image[box[1]:box[3], box[0]:box[2]])
            if i >= len(keys):
                k = "None"
            else:
                k = keys[i]

            temp[k] = ocr_res

        res.append(temp)

    return JSONResponse(BaseResponse(errcode=RET.OK, errmsg=error_map[RET.OK], data={'results': res}).dict())
