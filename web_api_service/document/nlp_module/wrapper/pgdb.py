import psycopg2


class PostgreSqlDatabase:

    def __init__(self, config):
        self.connection_string = config["database_url"]
        self.connection = self.get_connection()

    def get_connection(self):
        pg_conn = psycopg2.connect(self.connection_string)
        pg_conn.autocommit = False
        return pg_conn

    def __prepare_ocr_data_for_writing(self, doc_id, page_id, ocr_data):
        res = []
        for ocr_word_tuple in list(ocr_data.itertuples(index=False, name=None)):
            res.append((doc_id, page_id) + ocr_word_tuple)
        return res

    def write_ocr_result(self, doc_id, page_id, ocr_data):
        pg_cursor = self.connection.cursor()

        ocr_rows = self.__prepare_ocr_data_for_writing(doc_id, page_id, ocr_data)
        pg_cursor.executemany("""
            INSERT INTO ocr_results(doc_id, page_id, ocr_text,
                upper_left_y, upper_left_x,
                upper_right_y, upper_right_x,
                lower_right_y, lower_right_x,
                lower_left_y, lower_left_x
            )
            VALUES (%s,%s,%s,
                %s,%s,
                %s,%s,
                %s,%s,
                %s,%s
            )""",
            ocr_rows
        )

        self.connection.commit()
        pg_cursor.close()

    def write_doc_classification_result(self, doc_id, doc_class_id):
        pg_cursor = self.connection.cursor()

        pg_cursor.execute("""
            INSERT INTO doc_classification_results(doc_id, class_id)
            VALUES (%s, %s);
            """,
            (doc_id, doc_class_id)
        )

        self.connection.commit()
        pg_cursor.close()

    def write_attributes_for_5type(self, doc_id, class_id, attributes_dict):
        pg_cursor = self.connection.cursor()
        number = attributes_dict['Номер']
        date = attributes_dict['Дата']
        issuing_authority = attributes_dict['Выдавший орган']

        pg_cursor.execute("""
            INSERT INTO svid_agr_documents(doc_id, class_id, number, date, issuing_authority)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (doc_id, class_id,
             number, date, issuing_authority)
        )

        self.connection.commit()
        pg_cursor.close()