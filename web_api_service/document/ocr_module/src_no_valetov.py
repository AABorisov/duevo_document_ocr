import json
import os
import shutil
from collections import defaultdict

import requests
from pdf2image import convert_from_path
import time
import logging
import sys
import numpy as np
import re
from PIL import Image as IM
import cv2
import pytesseract as pt
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from pytesseract import Output
from PIL import Image as pilimg
from document.models import Document, TesseractClassifier
from document.rabbitmq_client import RabbitmqClient
from document.utils import add_ocr_tesseract_record, add_page_to_db_and_save_to_folder, add_record_tesseract_classifier
from document_processing import settings

"""
SELECT id, ocr_text as `text`, upper_left_y, upper_left_x, upper_right_y, upper_right_x, lower_right_y, lower_right_x, lower_left_y, lower_left_x
FROM document_processing.document_ocr_tesseract
WHERE page_id in (SELECT id from document_processing.document_page WHERE document_id=97);
"""

regular_dict_old = {
    'Свид__АГР': [
        'КОМИТЕТ \w{2,4} АРХИТЕКТУР\w \w{1,2} ГРАДОСТРОИТЕЛЬСТВ\w'.lower(),
        'по архитектур\w \w{1,2} градостроит\w',
        'ВЫПИСКА ИЗ ПРОТОКОЛА'.lower(),
        'свидетельств\w \w{1,4} утверждени\w'
    ],
    'Разр__на_стр': [
        'КОМИТЕТ ГОСУДАРСТВЕННОГО СТРОИТЕЛЬНОГО НАДЗОРА'.lower(),
        'РАЗРЕШЕНИ\w на строительство'.lower(),
        'строительство объекта',
        'разрешени[е|я]\s{0,3}\w{0,2}\s{0,3}строительство'
    ],
    'Разр__на_ввод': [
        'комитет\s{0,3}государственного\s{0,3}строительного\s{0,3}надзор',
        'разрешени[ею] \w+ ввод объект\w{0,1} \w+ эксплуатацию',
        'разрешени[е|я]\s{0,3}\w{0,2}\s{0,3}ввод'
    ],
    'ЗУ': [
        'земельн[ыо][гйм][о]{0,1} комитет',
        # 'земельн[ыо][гйм][о]{0,1} участ[ко][ак]', # похожая запись в БТИ "6. Поликарпова ул.,д.2 корп.4 изм.pdf" 4стр
        'договор[у]{0,1} \w+ земельн[ыо][гйм][о]{0,1} участ[ко][ак]',
        'догово\w{0,3}\s{0,3}аренд\w{0,3}\s{0,3}земельн\w{0,4}\s{0,3}участ\w{0,4}',
        'догов\w{0,3}\s{0,3}безвозмездн\w{0,3}\s{0,3}пользован\w{0,3}\s{0,3}земельн\w{0,3}\s{0,3}участк\w{0,3}\s{0,3}',
        'земельно\w{0,3}\s{0,3}участ\w{0,3}\s{0,3}догов\w{0,3}\s{0,3}арен\w{0,3}\s{0,3}здан\w{0,3}',
        'догов\w{0,3}\s{0,3}безвозмездн\w{0,3}\s{0,3}земельн\w{0,3}\s{0,3}участк\w{0,3}',
        'договор[у]{0,1} \w+ предоставлении участк[ао][м]{0,1}',
        'догов\w{0,3}\s{0,3}краткосрочн\w{0,3}\s{0,3}арен\w{0,3}\s{0,3}земельно\w{0,3}\s{0,3}участ\w{0,3}',
        '[оаеёэ]\s{0,3}предоставлен\w{0,3}\s{0,3}участ\w{0,3}',
        'безвозмездного пользования дополнительное соглашение аренд[аы]'
    ],
    'БТИ': [
        'ТЕХНИЧЕСКИЙ ПАСПОРТ'.lower(),
        'технический\s{0,5}паспорт',    # Evgenii+++
        'техническ[\w\s\(\)]+паспорт\w{0,3}',
        'фгу\w{0,3}\s{0,3}ростехинвентариза\w{0,3}\s{0,3}федеральн\w{0,4}\s{0,3}бти',
        'благоустройст\w{0,3}\s{0,3}обще\w{0,2}\s{0,2}\w{0,3}\s{0,3}жило\w{0,3}\s{0,3}основн\w{0,3}\s{0,3}площа\w{0,3}',
        'ЭКСПЛИКАЦИ[яю]'.lower()  # Предпоследняя страница
    ]
}


def debug(value):
    print('=================')
    print(value)
    print('=================')


def pdf_to_img_my_v1(file_pdf_path, show=True):
    # storage.goai.ru
    PUNCT = ['.', ',', ':', ';', ' ']
    dir_, filename = os.path.split(file_pdf_path)
    for sign in PUNCT:
        filename = filename.replace(sign, '_')
    if '_pdf' in filename:
        ind = filename.index('_pdf')
    elif '_pdf'.upper() in filename:
        ind = filename.index('_pdf'.upper())
    else:
        logging.info('Cannot remade %s' % filename)
        return None
    new_dir_name = dir_ + filename[:ind] + '_pictures'
    os.popen(r'mkdir %s' % new_dir_name).read()
    if show:
        logging.info(new_dir_name)
    # Pdf to images
    pages = convert_from_path(file_pdf_path,
                              150,
                              output_folder=new_dir_name, )
    cnt = 1
    for page in pages:
        pic_name = os.path.join(new_dir_name, 'out_%s.png' % str(cnt))
        page.save(pic_name, 'JPEG')
        cnt = cnt + 1
    for file in os.listdir(new_dir_name):
        if '.png' in file:
            continue
        os.popen(r'rm %s' % os.path.join(new_dir_name, file)).read()
    return new_dir_name


def rotate(image, center=None, scale=1.0, show=True):
    angle = 360 - int(re.search('(?<=Rotate: )\d+', pt.image_to_osd(image)).group(0))
    if angle == 0 or angle == 360:
        return np.asarray(image)
    (h, w) = np.asarray(image).shape[:2]

    if center is None:
        center = (w / 2, h / 2)

    # Perform the rotation
    M = cv2.getRotationMatrix2D(center, angle, scale)
    rotated = cv2.warpAffine(np.asarray(image), M, (w, h))
    if show:
        logging.info('Rotated on %s angle' % str(angle))
    return rotated


# img analyse

def ImToText2(img_):
    img_2 = IM.fromarray(img_)
    q = pt.image_to_string(img_2, lang='rus')  # --psm 12 --oem 3
    q = [i.strip() for i in q.split('\n') if i.strip()]
    q1 = [i.replace('\t', ' ') for i in q]
    return q1


def get_threshold(q0):
    """Valetov"""
    # threshold for lines detection by y axe
    heights = []
    for i in q0:
        if not i[-6].isnumeric(): continue
        w = int(i[-4])
        h = int(i[-3])
        if w==0: continue
        if int(i[-4]) > 0: heights.append(h)
    return np.median(heights)


def get_te(q0, thrs, no_list):
    """Valetov"""
    te = defaultdict(list)
    levels = []
    for i in q0:
        text = i[-1]
        if not i[-6].isnumeric(): continue
        x = int(i[-6])
        y = int(i[-5]) # ордината
        w = int(i[-4])
        h = int(i[-3])
        if text in no_list or w==0: continue
        new = True
        for level in levels:
            if abs(y-level)<thrs:
                te[level].append([x, text])
                new=False
                break
        if new:
            te[y].append([x, text])
            levels.append(y)

    return te


# main var img
def ImToText1(img_, image_path, bd=200):
    img_2 = IM.fromarray(img_)
    print(img_2)
    q = pt.image_to_data(img_2, lang='rus')  # --psm 12 --oem 3
    q = [i.strip() for i in q.split('\n') if i.strip()]
    q0 = [i.split('\t') for i in q]
    # Теперь когда есть информация о положении слов на картинке а именно их абсцисса и ординада, можно их упорядочить по строкам и внутри строк
    te = {}
    no_list = ['*', '-', '-1', '—', '|', '/', '\\', '.',
               ',']  # Если строка состоит лишь из этих символов(обычно это рудименты меток и графических элементов)
    picture_rudiments = ['‘', '"']
    # такую строку не учитываем
    # thrs = get_threshold(q0)
    # print(thrs)
    # te = get_te(q0, thrs, no_list)
    """
    # Evgenii+++ Get document_id and page_id from image name
    image_name_noext = os.path.splitext(image_name)[0]
    split_image_name = image_name_noext.split('_')
    document_id = int(split_image_name[0])
    page_id = int(split_image_name[1])

    # Create path to save processed files with boxes
    split_image_path = os.path.split(image_path)[0:-1]
    ocr_path = split_image_path[0]
    ocr_image_name = str(document_id) + '_' + str(page_id) + '_ocr.jpeg'
    ocr_image_path = os.path.join(ocr_path, ocr_image_name)
    """

    # Evgenii+++
    # plt.clf()
    # plt.imshow(img_2)
    cnt = 0
    # Create empty list for words
    ocr_words = []

    for i in q0:
        cnt += 1
        text = i[-1]

        # ордината Y
        I = i[-5]
        # абсцисса X
        J = i[-6]

        if text in no_list or (not I.isnumeric()):
            continue

        for j in picture_rudiments:
            text = text.replace(j, '')

        if text != '95':
            # Width
            width = i[-4]
            # Height
            height = i[-3]

            width = int(width)
            height = int(height)
            x0 = int(J)
            y0 = int(I)
            x1 = x0 + width
            y1 = y0 + height
            upper_left_y = int(I)  # y0
            upper_left_x = int(J)  # x0
            upper_right_y = upper_left_y
            upper_right_x = upper_left_x + width
            lower_right_y = upper_left_y + height  # y1
            lower_right_x = upper_left_x + width  # x1
            lower_left_y = upper_right_y + height
            lower_left_x = upper_left_x

            # Add new word to ocr array
            ocr_words.append({
                "ocr_text": text,
                "upper_left_y": upper_left_y,
                "upper_left_x": upper_left_x,
                "upper_right_y": upper_right_y,
                "upper_right_x": upper_right_x,
                "lower_right_y": lower_right_y,
                "lower_right_x": lower_right_x,
                "lower_left_y": lower_left_y,
                "lower_left_x": lower_left_x,
                "status": 2
            })

        # for i in picture_rudiments:
        #     text = text.replace(i, '')
        if int(I) in te:
            te[int(I)] = te[int(I)] + [[int(J), text]]  # Составим словарь опираясь на ординату
        else:
            te[int(I)] = [[int(J), text]]

    ll = sorted(te)  # Упорядочим по ординате

    ld = [te[i] for i in sorted(te)]
    LL = []
    for i in ll:
        if ll.index(i) == 0:
            LL = LL + [i]
            continue
        else:
            # также ввиду неточности анализа некоторые фрагменты одной строки могут иметь немного отличающиеся ординаты(введем допуск)
            if i in range(LL[-1], LL[-1] + 6 + 1):
                LL = LL + [LL[-1]]
            else:
                LL = LL + [i]
    # сформируем окончательный словарь и упорядочим слова(фрагменты) внутри строки
    fdin = {}

    for i in range(len(LL)):

        if LL[i] in fdin:
            fdin[LL[i]] = fdin[LL[i]] + ld[i]
        else:
            fdin[LL[i]] = ld[i]
    debug('------FDIN--------')
    debug(fdin)
    finlist = [' '.join([j[1] for j in sorted(fdin[i])]) for i in sorted(fdin)]
    finlist = [i for i in finlist if '@' not in i]
    print(img_)
    # Evgenii+++
    # plt.savefig(ocr_image_path, dpi=500)

    # Create word dictionary
    qq = ' '.join(finlist).replace('95', '').lower()
    res = {}
    for key in regular_dict_old:
        res.setdefault(key, 0)
        for i in regular_dict_old[key]:
            promres = re.compile(i).findall(qq)
            res[key] = res[key] + len(set(promres))

    # Try to find doc type
    detected_type = sorted([[i[1], i[0]] for i in list(res.items())], reverse=True)
    # Default vars
    is_detected = False
    document_type = 6
    debug('___________DICT__________')
    debug(qq)
    debug('___________DETECTED TYPE__________')
    debug(detected_type)

    if int(detected_type[0][0]) > 0:
        is_detected = True

    if is_detected:
        if detected_type[0][1] == 'Свид__АГР':
            document_type = 5
        elif detected_type[0][1] == 'Разр__на_ввод':
            document_type = 3
        elif detected_type[0][1] == 'БТИ':
            document_type = 1
        elif detected_type[0][1] == 'Разр__на_стр':
            document_type = 4
        elif detected_type[0][1] == 'ЗУ':
            document_type = 2

    # Create OCR dict
    ocr_data = {
        "is_detected": is_detected,
        "document_type": document_type,
        "finlist": finlist,
        "ocr_words": ocr_words,
        "dictionary": qq
    }

    return ocr_data


def adjust_height(img, target_height):
    print(img)
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
    # маска крупных объектов
    mask = cv2.dilate(cv2.medianBlur(res, 5), np.ones((5, 5), np.uint8), iterations=3)
    # вырезание крупных объектов по маске
    res = cv2.bitwise_and(res, res, mask=mask)

    return cv2.bitwise_not(res)


def remove_lines_from_image(image_path):
    image = cv2.imread(image_path)
    mask = np.ones(image.shape, dtype=np.uint8) * 255
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilate = cv2.dilate(thresh, kernel, iterations=3)

    cnts = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        area = cv2.contourArea(c)
        if area < 5000:
            x, y, w, h = cv2.boundingRect(c)
            mask[y:y + h, x:x + w] = image[y:y + h, x:x + w]

    # cv2.imshow('thresh', thresh)
    # cv2.imshow('dilate', dilate)
    # cv2.imshow('mask', mask)
    # cv2.imwrite(image_path + '.jpeg', mask)


def docimg_to_text(path, file_id, with_rotate=False, show=False):
    print('------------')
    dict_image_text = {}

    cnt = 0
    page_number = 0
    document_id = 0

    # Evgenii++ Sort images by name
    dict_image_text.setdefault(os.path.split(path)[-1], {})
    image_list = os.listdir(path)
    image_list.sort(key=lambda fname: int(fname.split('.')[0]))

    # Default document type 6 - unknown
    default_document_type = 6

    for pic in image_list:  # на данный момент работаем только с первым изображением(лицевым)
        pic_path = os.path.join(path, pic)
        image_path = pic_path
        image_name = pic
        print(pic)
        try:
            im = np.asarray(IM.open(str(pic_path)))
        except:
            print('There is no file!')
            print(sys.exc_info()[1])
            continue
        try:
            if with_rotate:
                im1 = rotate(im)
            else:
                im1 = im
            im2 = im1.mean(axis=-1).astype('uint8')
            (h, w) = im2.shape[:2]
        except:
            print('Problem with rotation!')
            print(sys.exc_info()[1])
            continue
        try:
            im3 = cv2.fastNlMeansDenoising(im2, None, 20, 7)
        except:
            print('Problem with denoising!')
            print(sys.exc_info()[1])
            continue
        # im4 = im3
        source = cv2.imread(image_path)
        height = h
        im4 = pre_process_image(source, height)
        im4 = im3
        # cv2.imwrite(image_path, im2)
        # print(image_path)

        # Count pages
        cnt += 1
        page_number += 1

        # Get OCR config
        ocr_data = ImToText1(im4, image_path)

        is_detected = ocr_data["is_detected"]
        document_type = ocr_data["document_type"]
        ocr_words = ocr_data["ocr_words"]
        text_ = ocr_data["finlist"]
        dictionary = ocr_data["dictionary"]

        print('--------------FINLIST------------')
        debug(text_)

        # First step create document
        if cnt == 1:

            if is_detected:
                default_document_type = document_type

            document = Document.objects.create(
                file_id=file_id,
                status_id=11,
                is_processed=False,
            )
#Обработан нашим OCR / Отправка в google OCR
            #Построение NLP tesseract
            document_id = document.id

            tesseract_classifier = add_record_tesseract_classifier(document_id, default_document_type)
        # Check
        elif cnt == 2 and is_detected and default_document_type == 6 and document_type != 6:
            tesseract_classifier = TesseractClassifier.objects.get(document_id=document_id, document_type_id=6)
            tesseract_classifier.document_type_id = document_type
            tesseract_classifier.save()
            default_document_type = document_type
        else:
            if is_detected and default_document_type != document_type:
                page_number = 1
                default_document_type = document_type

                document = Document.objects.create(
                    file_id=file_id,
                    status_id=8,
                    is_processed=False,
                )

                document_id = document.id

                tesseract_classifier = add_record_tesseract_classifier(document_id, default_document_type)

        # Save page to folder and DB
        page = add_page_to_db_and_save_to_folder(document_id, image_path, page_number, dictionary, ocr_words, im4)

        # Add ocr words to DB
        for ocr_word in ocr_words:
            add_ocr_tesseract_record(ocr_word["upper_left_y"], ocr_word["upper_left_x"], ocr_word["upper_right_y"],
                                     ocr_word["upper_right_x"],
                                     ocr_word["lower_right_y"], ocr_word["lower_right_x"], ocr_word["lower_left_y"],
                                     ocr_word["lower_left_x"],
                                     ocr_word["ocr_text"], page.id)

        # Evgenii+++
        dict_image_text[os.path.split(path)[-1]].update({pic: text_})

    # Evgenii++ remove tmp_folder
    shutil.rmtree(path, ignore_errors=True)

    return dict_image_text
