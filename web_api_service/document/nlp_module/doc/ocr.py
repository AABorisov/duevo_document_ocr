""" OCR interfaces."""
import os

from google.cloud import vision
import pytesseract

import pandas as pd
import numpy as np
from PIL import Image
import io
from collections import namedtuple

from document_processing import settings
from .utils import near, NEAR_CONST


class GoogleOCR(object):

    def __init__(self, key_json_path=None):

        self.client = vision.ImageAnnotatorClient() if key_json_path is None \
            else vision.ImageAnnotatorClient.from_service_account_json(key_json_path)

    def detect(self, input):
        if isinstance(input, bytes):
            image = vision.Image(content=input)
        else:
            image = input
        response = self.client.text_detection(image=image)

        if response.error.message:
            raise Exception(
                '{}\nFor more info on error messages, check: '
                'https://cloud.google.com/apis/design/errors'.format(
                    response.error.message))
        return response.text_annotations

    # def decode(self, byte_content):
    #     return Image.open(io.BytesIO(byte_content))

    def postprocess(self, text):
        data = pd.DataFrame([{
            'text': t.description,
            'upper_left_y': t.bounding_poly.vertices[0].y,
            'upper_left_x': t.bounding_poly.vertices[0].x,
            'upper_right_y': t.bounding_poly.vertices[1].y,
            'upper_right_x': t.bounding_poly.vertices[1].x,
            'lower_right_y': t.bounding_poly.vertices[2].y,
            'lower_right_x': t.bounding_poly.vertices[2].x,
            'lower_left_y': t.bounding_poly.vertices[3].y,
            'lower_left_x': t.bounding_poly.vertices[3].x,
        } for t in text[1:]])
        try:
            data = data.sort_values(['upper_left_y', 'upper_left_x']).reset_index(drop=1)
        except:
            print("except", data)
        return data


class TesseractOCR(object):
    def detect(self, input):
        if isinstance(input, bytes):
            img = Image.open(io.BytesIO(input))
        elif Image.isImageType(input):
            img = input
        elif isinstance(input, str):
            img = Image.open(input)
        else:
            raise RuntimeError(f"Wrong input format! {type(input)}")
        try:
            df = pytesseract.image_to_data(img, lang='rus', output_type='data.frame')
        except Exception as e:
            print(e)
            print('Make sure you downloaded rus datapack, see readme')
        return df

    def postprocess(self, df):
        df = df[~pd.isna(df['text'])]
        df = df[df['text'] != ' ']
        df = df.reset_index(drop=True)
        data = pd.DataFrame([{
            'text': t.text,
            'upper_left_y': t.top,
            'upper_left_x': t.left,
            'upper_right_y': t.top,
            'upper_right_x': t.left + t.width,
            'lower_right_y': t.top + t.height,
            'lower_right_x': t.left + t.width,
            'lower_left_y': t.top + t.height,
            'lower_left_x': t.left,
        } for t in list(df.itertuples())])
        data = data.sort_values(['upper_left_y', 'upper_left_x']).reset_index(drop=1)
        return data
