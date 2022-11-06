import os

import cv2
import numpy as np
from document_processing import settings

from django.core.management.base import BaseCommand, CommandError


def adjust_height(img, target_height):
    h, w = img.shape[0: 2]
    scale = target_height / h

    return cv2.resize(img, (int(scale * w), int(scale * h)), cv2.INTER_LANCZOS4)


def pre_process_image(img, target_height=2400):
    # зменение масштаба
    img2 = adjust_height(img, target_height)
    # конвертация в серое
    grey = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    # билатеральный фильтр
    grey = cv2.bilateralFilter(grey, 15, 30, 30)
    # адаптивный трешолд
    res = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 2)
    # инверсия цвета
    res = cv2.bitwise_not(res)
    # линии
    lines = cv2.HoughLines(res, 1, np.pi / 180, target_height // 5, None, min_theta=70 * np.pi / 180, max_theta=110 * np.pi / 180)
    # угол поворота
    med_angle = np.median([ln[0][1] for ln in lines]) / np.pi * 180
    delta = med_angle - 90
    center = (res.shape[1] // 2, res.shape[0] // 2)
    rot_mat = cv2.getRotationMatrix2D(center, delta, 1.0)
    # маска крупных объектов
    mask = cv2.dilate(cv2.medianBlur(res, 5), np.ones((5, 5), np.uint8), iterations=3)
    # вырезание крупных объектов по маске
    res = cv2.bitwise_and(res, res, mask=mask)
    # поворот
    res = cv2.warpAffine(res, rot_mat, (res.shape[1], res.shape[0]), flags=cv2.INTER_LINEAR)

    return cv2.bitwise_not(res)


class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        img_1 = os.path.join(settings.BASE_DIR, 'document/management/commands/26_339.png')
        img_2 = os.path.join(settings.BASE_DIR, 'document/management/commands/saved/26_339.png')
        print(img_1)
        source = cv2.imread(img_1)
        height = 3000
        res = pre_process_image(source, height)
        cv2.imwrite(img_2, res)
        # cv2.imshow("source image", adjust_height(source, height))
        # cv2.imshow("result", res)
        # cv2.waitKey(0)

