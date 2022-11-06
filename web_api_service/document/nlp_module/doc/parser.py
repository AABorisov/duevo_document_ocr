""" Parser implementation """
import pandas as pd

from .utils import make_rows, fix_gramma

from .doc_models.doc5 import Doc5
from .doc_models.doc2 import Doc2
from .doc_models.doc1 import Doc1


class Parser(object):
    def __init__(self):
        self.doc5 = Doc5()
        self.doc2 = Doc2()
        self.doc1 = Doc1()
        self.box_data = []

    def debug(self, files):
        doc_rows = []
        doc_pandas_rows = []
        for f in files:
            df = pd.read_csv(f)
            try:
                df = df.sort_values(['upper_left_y', 'upper_left_x']).reset_index(drop=1)
                pandas_rows, file_rows, coords = make_rows(df)
                file_rows = fix_gramma(file_rows)
            except:
                print("Broken file! skipping")
                file_rows = []
            doc_rows += file_rows
            doc_pandas_rows += pandas_rows
        return doc_pandas_rows

    def parse(self, files, doc_type):

        # gather text only and create list_of_rows
        doc_rows = []
        doc_pandas_rows = []
        # pandas_rows = ''
        for f in files:
            df = pd.read_csv(f)
            try:
                df = df.sort_values(['upper_left_y', 'upper_left_x']).reset_index(drop=1)
                pandas_rows, file_rows, coords = make_rows(df)
                file_rows = fix_gramma(file_rows)
            except:
                print("Broken file! skipping")
                file_rows = []
            doc_rows += file_rows
            doc_pandas_rows += pandas_rows

        # parse text only info
        if doc_type == 5 or doc_type == 'Свид. АГР' or doc_type == '5_Свид. АГР':
            return self.doc5.parse_fields(doc_rows, doc_pandas_rows=doc_pandas_rows)
        elif doc_type == 1:
            return self.doc1.parse_fields(doc_rows, doc_pandas_rows=doc_pandas_rows, coords=coords)
        elif doc_type == 2:
            # doc_line = ' '.join(doc_rows)
            return self.doc2.parse_fields(doc_rows)
        else:
            raise NotImplementedError
