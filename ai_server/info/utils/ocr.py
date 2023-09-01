# *_*coding:utf-8 *_*
# @Author : YueMengRui
import numpy as np
import cv2
import requests
import base64
from info import logger
from info.configs.base_configs import OCR_BYTE_URL, OCR_GENERAL_URL


def get_ocr_byte_res(img):
    data = {
        'file': np.array(cv2.imencode('.jpg', img)[1]).tobytes()
    }

    try:
        res = requests.post(url=OCR_BYTE_URL,
                            files=data)
        logger.info(res.json())
        txt = res.json()['data']['results']
    except Exception as e:
        logger.error({'EXCEPTION': e})
        txt = 'None'

    return txt


def get_ocr_general_res(img):
    data = {
        'image': base64.b64encode(np.array(cv2.imencode('.png', img)[1]).tobytes()).decode()
    }

    try:
        res = requests.post(url=OCR_GENERAL_URL,
                            json=data)
        return res.json()['data']['results']
        # txt_list = res.json()['data']['results']
        # txt_list = [x['text'][0] for x in txt_list]
        # txt = '\n'.join(txt_list)
    except Exception as e:
        print({'EXCEPTION': e})
        raise 'error'
