import os
import re

import numpy as np
import cv2
import pytesseract
from pytesseract import Output
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from PIL import Image as IM

from document.models import OcrTesseract
from document_processing import settings

"""
=================
Here is a summary description of each column, what they represent, and the range of valid values they can have.

level: hierarchical layout (a word is in a line, which is in a paragraph, which is in a block, which is in a page), a value from 1 to 5
1: page
2: block
3: paragraph
4: line
5: word
page_num: when provided with a list of images, indicates the number of the file, when provided with a multi-pages document, indicates the page number, starting from 1
block_num: block number within the page, starting from 0
par_num: paragraph number within the block, starting from 0
line_num: line number within the paragraph, starting from 0
word_num: word number within the line, starting from 0
left: x coordinate in pixels of the text bounding box top left corner, starting from the left of the image
top: y coordinate in pixels of the text bounding box top left corner, starting from the top of the image
width: width of the text bounding box in pixels
height: height of the text bounding box in pixels
conf: confidence value, from 0 (no confidence) to 100 (maximum confidence), -1 for all level except 5
text: detected text, empty for all levels except 5


--psm N
Set Tesseract to only run a subset of layout analysis and assume a certain form of image. The options for N are:

0 = Orientation and script detection (OSD) only.
1 = Automatic page segmentation with OSD.
2 = Automatic page segmentation, but no OSD, or OCR. (not implemented)
3 = Fully automatic page segmentation, but no OSD. (Default)
4 = Assume a single column of text of variable sizes.
5 = Assume a single uniform block of vertically aligned text.
6 = Assume a single uniform block of text.
7 = Treat the image as a single text line.
8 = Treat the image as a single word.
9 = Treat the image as a single word in a circle.
10 = Treat the image as a single character.
11 = Sparse text. Find as much text as possible in no particular order.
12 = Sparse text with OSD.
13 = Raw line. Treat the image as a single text line,
     bypassing hacks that are Tesseract-specific.

--oem N
Specify OCR Engine mode. The options for N are:

0 = Original Tesseract only.
1 = Neural nets LSTM only.
2 = Tesseract + LSTM.
3 = Default, based on what is available.    

"""


def image_to_text_tesseract(document_id: int, page_id: int, image_path: str) -> str:
    """Распознаем текст с картинки с помощью нашего OCR"""
    processed_image = os.path.join(settings.MEDIA_ROOT, 'pages', str(document_id) + '_' + str(page_id) + '_ocr.jpeg')
    long_text = ''
    image_cv = cv2.imread(image_path)

    image_result = cv2.fastNlMeansDenoisingColored(image_cv, None, 10, 10, 7, 21)
    # img_2 = IM.fromarray(image_result)

    # Cyrilic pattern
    text_pattern = '^[а-яА-Я0-9\:\;\.\-\,\=\ ]+$'

    d = pytesseract.image_to_data(image_result, output_type=Output.DICT, lang='rus')
    n_boxes = len(d['text'])

    cnt = 0
    cnt1 = 0
    plt.imshow(image_result)
    for i in range(n_boxes):
        cnt1 += 1
        if int(d['conf'][i]) > 60:

            if re.match(r'^\s*$', d['text'][i]):
                print('--EMPTY--')
                continue

            # if re.match(text_pattern, d['text'][i]):
            cnt += 1
            (x0, y0, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            print('-------START--------')
            x1 = x0 + w
            y1 = y0 + h
            print(x0, y0, x1, y1)
            print(type(d['text'][i]))
            print(d['text'][i])
            print('========FINISH========')
            long_text += d['text'][i] + ' '

            ocr_tesseract = OcrTesseract.objects.create(
                page_id=page_id,
                ocr_text=d['text'][i],
                upper_left_y=y0,
                upper_left_x=x0,
                lower_right_y=y1,
                lower_right_x=x1,
                status=2
            )

            ax = plt.gca()
            rect = patches.Rectangle((x0, y0),
                                     w,
                                     h,
                                     linewidth=0.5,
                                     edgecolor='cyan',
                                     fill=False)

            ax.add_patch(rect)

    plt.savefig(processed_image, dpi=500)

    return long_text
