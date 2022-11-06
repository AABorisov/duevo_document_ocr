import os, io, json, requests
from doc.ocr import GoogleOCR
from doc.api import Classifier
from config import ConfigProcessor
from amqp_processor import AmqpProcessor
from pgdb import PostgreSqlDatabase


STORAGE_PATH = None


def callback(img_paths, ocr, classifier):
    # I. OCR
    ocr_dfs = []
    for local_img_path in img_paths:
        # OCR
        with io.open(local_img_path, 'rb') as image_file:
            content = image_file.read()
            resp = ocr.detect(content)
        ocr_data_df = ocr.postprocess(resp)
        #pg_db.connection.commit() # <-- this was done in write_ocr_result() func

        ocr_dfs.append(ocr_data_df)

    # II. Classifier
    ocr_csv_paths = []
    for idx in range(len(ocr_dfs)):
        ocr_df = ocr_dfs[idx]
        ocr_csv_path = os.path.join(STORAGE_PATH, "{}.csv".format(idx))
        ocr_df.to_csv(ocr_csv_path)
        ocr_csv_paths.append(ocr_csv_path)
    doc_class = classifier.classify_document(files=ocr_csv_paths)
    print(doc_class)


if __name__ == '__main__':
    cfg_path = './config/dev.json'
    # 1.
    config_processor = ConfigProcessor(cfg_path)
    cfg = config_processor.get_configs()
    print(cfg)

    STORAGE_PATH = cfg['local_storage_path']

    ocr = GoogleOCR(key_json_path='./config/utm-06942e453718.json')
    classifier = Classifier()
    callback(['/home/neurus/storage/doc.png'], ocr, classifier)

    print('END')