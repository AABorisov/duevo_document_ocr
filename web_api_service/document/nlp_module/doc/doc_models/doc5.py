""" Parsing fields from 5 type Свид Агр. """

from ..utils import similar

FIELD_NAMES = ['Номер', 'Дата', 'Выдавший орган']


class Doc5():
    def __init__(self, fields=FIELD_NAMES):
        self.fields = FIELD_NAMES

    def parse_doc_number(self, list_of_rows, doc_pandas_rows=None):
        """ Assume format is char-char-char where char is 0-9 and /"""
        for row in list_of_rows:
            if 'регистрацион' in row.lower() or similar('Регистрационный No', row.lower(), 0.7):
                row = row.split(' ')
                for sub in row:
                    if sub.count('-') >= 1:
                        return sub
        return None

    def parse_date(self, list_of_rows, doc_pandas_rows=None):
        for row in list_of_rows:
            if 'дата: ' in row.lower() or 'дата ' in row.lower():
                row = row.split(' ')
                for sub in row:
                    if sub.count('.') == 2:
                        return sub
        return None

    def parse_issuer(self, list_of_rows, doc_pandas_rows=None):

        key_word = 'КОМИТЕТ ПО АРХИТЕКТУРЕ И ГРАДОСТРОИТЕЛЬСТВУ Г.МОСКВЫ'.lower()
        for ix, row in enumerate(list_of_rows):
            if key_word in row.lower() or similar(key_word, row, 0.7):
                return 'КОМИТЕТ ПО АРХИТЕКТУРЕ И ГРАДОСТРОИТЕЛЬСТВУ Г.МОСКВЫ'

    def parse_fields(self, list_of_rows, doc_pandas_rows):
        answers = [self.parse_doc_number(list_of_rows),
                   self.parse_date(list_of_rows),
                   self.parse_issuer(list_of_rows)]

        answers = [x if x is not None else [] for x in answers]
        ocr_ids = [[] for x in answers]
        return dict(zip(FIELD_NAMES, answers)), dict(zip(FIELD_NAMES, ocr_ids))
