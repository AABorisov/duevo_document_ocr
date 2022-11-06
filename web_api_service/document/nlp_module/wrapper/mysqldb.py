# https://github.com/PyMySQL/PyMySQL
import pymysql


class MySqlDatabase:

    def __init__(self, config):
        self.connection = pymysql.connect(host=config["host"],
                             user=config['user'],
                             password=config['password'],
                             db=config['db'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

    def close(self):
        self.connection.close()

    def __prepare_ocr_data_for_writing(self, doc_id, page_id, ocr_data):
        res = []
        for ocr_word_tuple in list(ocr_data.itertuples(index=False, name=None)):
            res.append(ocr_word_tuple + (doc_id, page_id)) # TODO: MAYBE, created_at (?)
        return res

    def _write_ocr(self, ocr_rows_batch):
        with self.connection.cursor() as cursor:
            sql_query = """
                INSERT INTO `document_ocr` (`ocr_text`,
                    `upper_left_y`, `upper_left_x`,
                    `upper_right_y`, `upper_right_x`,
                    `lower_right_y`, `lower_right_x`,
                    `lower_left_y`, `lower_left_x`,
                    `document_id`, `page_id`
                )
                VALUES (%s,
                    %s,%s,
                    %s,%s,
                    %s,%s,
                    %s,%s,
                    %s,%s
                );
            """
            cursor.executemany(sql_query, ocr_rows_batch)
            batch_first_id = cursor.lastrowid
            row_count = cursor.rowcount

        # connection is not autocommit by default.
        # So you must commit to save your changes.
        self.connection.commit()

        return batch_first_id, row_count

    def write_ocr_result(self, doc_id, page_id, ocr_data):
        ocr_rows = self.__prepare_ocr_data_for_writing(doc_id, page_id, ocr_data)
        ocr_ids = []
        BATCH_SIZE = 256
        for batch_start_idx in range(0, len(ocr_rows), BATCH_SIZE):
            ocr_rows_batch = ocr_rows[batch_start_idx:batch_start_idx+BATCH_SIZE]
            batch_first_id, row_count = self._write_ocr(ocr_rows_batch)
            for ocr_id in range(batch_first_id, batch_first_id + row_count):
                ocr_ids.append(ocr_id)
        return ocr_ids

    def update_status_in_document_table(self, doc_id, status):
        with self.connection.cursor() as cursor:
            sql_query = """
                UPDATE document_processing.document_document SET status_id=%s
                WHERE id=%s;
            """
            cursor.execute(sql_query, (status, doc_id))

        self.connection.commit()

    def write_doc_classification_result(self, doc_id, doc_class_id):
        with self.connection.cursor() as cursor:
            sql_query = """
                INSERT INTO `document_classification` (
                    `document_id`,
                    `document_type_id`
                )
                VALUES (%s, %s);
            """
            cursor.execute(sql_query, (doc_id, doc_class_id))

        self.connection.commit()

    def write_nlp_attributes(self, doc_id, class_id, attr_dict):
        with self.connection.cursor() as cursor:
            # Read a single record
            #sql = """SELECT id, attribute_name FROM document_processing.document_attribute where document_type_id=%s and is_required=1;"""
            # в целом, можно убрать is_required=1 в запросе, тогда можем добавлять лбые поля.

            sql = """SELECT id, attribute_name, is_required FROM document_processing.document_attribute where document_type_id=%s;"""

            cursor.execute(sql, (class_id))
            records = cursor.fetchall()

        for record in records:
            attr_id = record['id']
            attr_name = record['attribute_name']
            is_required = record['is_required']

            if attr_name in attr_dict:
                # распознано
                # т.е. предполагается, что 'ocr_ids' есть и/или 'text' есть.

                status = 0
                attr_ids_str = None
                ocr_text = None

                if type(attr_dict[attr_name]['ocr_ids'])==list and len(attr_dict[attr_name]['ocr_ids']) > 0:
                    # в базе лист из ocr_id держится не как list, а как str => convert to string representation
                    attr_ids_str = str(attr_dict[attr_name]['ocr_ids'])
                if type(attr_dict[attr_name]['text'])==str and attr_dict[attr_name]['text'] != '':
                    ocr_text = attr_dict[attr_name]['text']
                if attr_ids_str is not None and ocr_text is not None:
                    status = 1
                if attr_ids_str is None and ocr_text is not None:
                    status = 2

                with self.connection.cursor() as cursor:
                    sql = """
                        INSERT INTO document_processing.document_nlp (is_active, attribute_id, document_id, ocr_word_ids, status, ocr_text)
                        VALUES (%s, %s, %s, %s, %s, %s);
                    """
                    cursor.execute(sql, (1, attr_id, doc_id, attr_ids_str, status, ocr_text))
                self.connection.commit()
            else:
                # не распознано
                if is_required == 1:
                    status = 0
                    with self.connection.cursor() as cursor:
                        sql = """
                            INSERT INTO document_processing.document_nlp (is_active, attribute_id, document_id, status)
                            VALUES (%s, %s, %s, %s);
                        """
                        cursor.execute(sql, (1, attr_id, doc_id, status))
                    self.connection.commit()


def test_nlp(mysqldb):
    from doc.parser import Parser
    from main import generate_general_attributes_dict
    parser = Parser()
    ocr_csv_paths = ['~/storage/0.csv', '~/storage/1.csv', '~/storage/2.csv',
                     '~/storage/3.csv', '~/storage/4.csv', '~/storage/5.csv',
                     '~/storage/6.csv', '~/storage/7.csv', '~/storage/8.csv',
                     '~/storage/9.csv', '~/storage/10.csv']
    text_attributes_dict, ocr_ids_dict = parser.parse(ocr_csv_paths, doc_type=1)
    general_attrs_dict = generate_general_attributes_dict(text_attributes_dict, ocr_ids_dict)
    print('general_attrs_dict=', general_attrs_dict)
    #mysqldb.write_nlp_attributes(35, 1, general_attrs_dict)


if __name__ == '__main__':
    config = {
        "host": "116.203.223.126",
        "port": 3306,
        "db": "document_processing",
        "user": "dueva",
        "password": "Dev197374labS###"
    }
    mysqldb = MySqlDatabase(config)

    # 1. OCR test
    #import pandas as pd
    ##ocr_df = pd.read_csv('~/storage/0.csv', nrows=3, index_col=0)
    #ocr_df = pd.read_csv('~/storage/0.csv', index_col=0)
    #del ocr_df['ocr_id']
    #print(ocr_df)
    #ocr_ids = mysqldb.write_ocr_result(doc_id=5, page_id=5, ocr_data=ocr_df)
    #ocr_df = ocr_df.assign(ocr_id=pd.Series(ocr_ids))
    #print(ocr_df)

    # 2. Test: store attributes
    #attr_dict = {'Номер': [], 'Дата': [10], 'Выдавший орган': [11,12,13]}
    #mysqldb.write_nlp_attributes(doc_id=5, class_id=5, attr_dict=attr_dict)

    # 3. Test: update
    #mysqldb.update_status_in_document_table(doc_id=5)

    test_nlp(mysqldb)


    mysqldb.close()
    print('finish')