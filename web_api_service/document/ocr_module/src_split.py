import json
import os
import shutil
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

from document.models import Document, TesseractClassifier
from document.rabbitmq_client import RabbitmqClient
from document.utils import add_ocr_tesseract_record, add_page_to_db_and_save_to_folder, add_record_tesseract_classifier


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
        'строительство объекта'
    ],
    'Разр__на_ввод': [
        'КОМИТЕТ СТРОИТЕЛЬНОГО НАДЗОРА'.lower(),
        'разрешени[ею] \w+ ввод объект\w{0,1} \w+ эксплуатацию'
    ],
    'ЗУ': [
        'земельн[ыо][гйм][о]{0,1} комитет',
        # 'земельн[ыо][гйм][о]{0,1} участ[ко][ак]', # похожая запись в БТИ "6. Поликарпова ул.,д.2 корп.4 изм.pdf" 4стр
        'договор[у]{0,1} \w+ земельн[ыо][гйм][о]{0,1} участ[ко][ак]',
        'договор[у]{0,1} \w+ предоставлении участк[ао][м]{0,1}',
        'безвозмездного пользования дополнительное соглашение аренд[аы]'
    ],
    'БТИ': [
        'ТЕХНИЧЕСКИЙ ПАСПОРТ'.lower(),
        'технический\s{0,5}паспорт',    # Evgenii+++
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
            if i in range(LL[-1], LL[
                                      -1] + 6 + 1):  # также ввиду неточности анализа некоторые фрагменты одной строки могут иметь немного отличающиеся ординаты(введем допуск)
                LL = LL + [LL[-1]]
            else:
                LL = LL + [i]
    fdin = {}  # сформируем окончательный словарь и упорядочим слова(фрагменты) внутри строки

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
    }

    return ocr_data


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

    # Config for RabbitMQ
    """
    rabbitmq_cfg = {
        "host": "89.223.95.49",
        "port": 5672,
        "user": "dueva",
        "password": "n3dF8dfXpweZv",
        "exchange": "doc-analysis"
    }
    print('RabbitmqClient connect')
    # создаем клиента
    rabbitmq_client = RabbitmqClient(rabbitmq_cfg)
    """
    # For rabbit celery
    pages_array = []
    docs_array = []
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

        im4 = im3

        # Count pages
        cnt += 1
        page_number += 1

        # Get OCR config
        ocr_data = ImToText1(im4, image_path)

        is_detected = ocr_data["is_detected"]
        document_type = ocr_data["document_type"]
        ocr_words = ocr_data["ocr_words"]
        text_ = ocr_data["finlist"]

        # First step create document
        if cnt == 1:

            if is_detected:
                default_document_type = document_type

            document = Document.objects.create(
                file_id=file_id,
                status_id=8,
                is_processed=True,
            )

            document_id = document.id

            tesseract_classifier = add_record_tesseract_classifier(document_id, default_document_type)
        # elif cnt == 2 and is_detected
        else:
            if is_detected and default_document_type != document_type:
                page_number = 1
                default_document_type = document_type

                document = Document.objects.create(
                    file_id=file_id,
                    status_id=8,
                    is_processed=True,
                )

                document_id = document.id

                tesseract_classifier = add_record_tesseract_classifier(document_id, default_document_type)

        # Save page to folder and DB
        page = add_page_to_db_and_save_to_folder(document_id, image_path, page_number)
        print('********PAGE PATH********')
        print(page.page_image.path)

        # Send image to Adygzhy
        """
        url = 'http://89.223.95.49:8887/upload'
        files = {'media': open(page.page_image.path, 'rb')}
        response = requests.post(url, files=files)
        json_string = response.text
        print('Adygzhy json:')
        print(json_string)
        json_data = json.loads(json_string)
        page_link = json_data[0]['link']
        page_id = json_data[0]['page_id']
        doc_id = json_data[0]['doc_id']
        """

        page.doc_id = document_id
        page.page_id = page.id
        page.page_link = None
        page.save()

        # Add ocr words to DB
        for ocr_word in ocr_words:
            add_ocr_tesseract_record(ocr_word["upper_left_y"], ocr_word["upper_left_x"], ocr_word["upper_right_y"],
                                     ocr_word["upper_right_x"],
                                     ocr_word["lower_right_y"], ocr_word["lower_right_x"], ocr_word["lower_left_y"],
                                     ocr_word["lower_left_x"],
                                     ocr_word["ocr_text"], page.id)

        # Evgenii+++
        dict_image_text[os.path.split(path)[-1]].update({pic: text_})

    # Например, у нас есть такой документ для обработки:

    # скорее всего, удобно будет отправлять сообщения в формате JSON, так что
    # rabbitmq_client.send_msg(json.dumps(doc))

    # в конце работы закроем соединение
    # rabbitmq_client.close_connection()

    # Evgenii++ remove tmp_folder
    shutil.rmtree(path, ignore_errors=True)

    return dict_image_text
