""" Document classifier. """
import pandas as pd
import pkg_resources


import joblib
import tensorflow_hub as hub
import numpy as np
import tensorflow_text

from .utils import fix_gramma, make_rows, check_text

resource_package = __name__
resource_path = '/'.join(('models', 'doc_classifier.joblib'))  # Do not use os.path.join()
doc_classifier_path = pkg_resources.resource_filename(resource_package, resource_path)

DOC_CLASSIFIER = joblib.load(doc_classifier_path)

UNIVERSAL_ENCODER = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")

#DOC_CLASSES = np.array(['БТИ', 'ЗУ', 'Разр. на ввод', 'Разр. на стр-во', 'Свид. АГР'])

DOC_CLASSES = np.array([1, 2, 3, 4, 5])

def check_doc(files):
    doc_as_line = ''
    for f in files:
        df = pd.read_csv(f)
        try:
            _, txt, _ = make_rows(df)
        except Exception as e:
            print(e)
            return None
            #raise Exception(f"Broken file! {f}")
        txt = fix_gramma(txt)
        line = ' '.join(txt) + ' '
        doc_as_line += line
    try:


        v = UNIVERSAL_ENCODER([doc_as_line])
        v = v.numpy().reshape(1,512)
        l = DOC_CLASSIFIER.predict(v)
        return DOC_CLASSES[l][0]
        # if check_text('НА ВВОД ОБЪЕКТА В ЭКСПЛУАТАЦИЮ' , txt): # 3
        #     return 'РАЗРЕШЕНИЕ НА ВВОД ОБЪЕКТА В ЭКСПЛУАТАЦИЮ'
        # elif check_text('ЭКСПЛИКАЦИЯ', txt): # 1 (2)
        #      return 'ЭКСПЛИКАЦИЯ'
        # elif check_text('ТЕХНИЧЕСКИЙ ПАСПОРТ', txt): # 1 (1)
        #     return 'ТЕХНИЧЕСКИЙ ПАСПОРТ'
        # elif check_text(['ДОГОВОР АРЕНДЫ ЗЕМЕЛЬНОГО УЧАСТКА', 'договор аренды земли'], txt): # 2
        #     return 'ДОГОВОР АРЕНДЫ ЗЕМЕЛЬНОГО УЧАСТКА'
        # elif check_text('разрешения на строительство', txt): # 4
        #     return 'РАЗРЕШЕНИЕ НА СТРОИТЕЛЬСТВО'
        # elif check_text(['АРХИТЕКТУРНО-ГРАДОСТРОИТЕЛЬНОГО РЕШЕНИЯ', 
        #                  'АРХИТЕКТУРНО-ГРАДОСТРОИТЕЛЬНОЕ РЕШЕНИЕ'], txt): # 5
        #     return 'СВИДЕТЕЛЬСТВО ОБ УТВЕРЖДЕНИИ АРХИТЕКТУРНО-ГРАДОСТРОИТЕЛЬНОГО РЕШЕНИЯ'
    except Exception as e:
        print(e)
        return None
    return None