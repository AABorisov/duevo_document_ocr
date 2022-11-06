""" API for OCR and analysis. """

import pandas as pd
from typing import List

from .ocr import GoogleOCR
from .classifier import check_doc

class Classifier(object):
    def classify_document(self, files: List):
        
        return check_doc(files)