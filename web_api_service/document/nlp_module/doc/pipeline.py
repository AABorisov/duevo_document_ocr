""" Example pipelines. """

from glob import glob

from .api import Classifier

doc_class = Classifier()

ocrs = glob('../data/google/*/*')


doc_class.classify_document(ocrs)
