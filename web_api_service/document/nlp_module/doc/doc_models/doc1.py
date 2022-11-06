""" Parsing fields from 1 type БТИ (small subset)."""

from ..utils import similar

from datetime import date
from natasha import MorphVocab, DatesExtractor

from yargy.interpretation import fact
from yargy import rule, and_, Parser
from yargy.predicates import gte, lte
from yargy.predicates import caseless, normalized, dictionary
from yargy import or_


YEAR = and_(
    gte(1600),
    lte(2100)
)
DATE = rule(
    YEAR
)

YEAR_FINDER = Parser(DATE)


morph = MorphVocab()
DATE_FINDER = DatesExtractor(morph)

FIELD_NAMES = ['Номер', 'Дата', 'Выдавший орган', 
'Дата заполнения документа', 'Наименование объекта', 'Инвентарный номер', 
'Год постройки', 'Год ввода в эксплуатацию', 'Кадастровый номер ЗУ', 'Кадастровый номер ОКС']

class Doc1():
    def __init__(self, fields=FIELD_NAMES):
        self.fields = FIELD_NAMES
    
    def parse_doc_number(self, list_of_rows, doc_pandas_rows):
        return None, []
    
    def parse_date(self, list_of_rows, doc_pandas_rows):
        for ix, (row, pd_row) in enumerate(zip(list_of_rows, doc_pandas_rows)):
            if 'паспорт составлен' in row or similar('паспорт составлен по состоянию на', row, 0.7):
                row = row.replace("\"", "")
                match = DATE_FINDER.find(row)
                if match:
                    doc_date = date(match.fact.year, match.fact.month, match.fact.day)
                    return str(doc_date), [x.ocr_id if hasattr(x, 'ocr_id') else 'no ocr_id column' for x in pd_row] ## yyyy-mm-dd (iso format)
        return None, []

    def parse_issuer(self, list_of_rows, doc_pandas_rows):
        for row, pd_row in zip(list_of_rows, doc_pandas_rows):
            if similar("фгуп ростехинвентаризация - федеральное бти", row, 0.7):
                return "ФГУП 'Ростехинвентаризация - федеральное БТИ'".upper(), [x.ocr_id if hasattr(x, 'ocr_id') else 'no ocr_id column' for x in pd_row]
        return None, []
    
    def parse_date_of_filling(self, list_of_rows, doc_pandas_rows):
        # currently seem to be same as parse_date
        return None, []
    
    def parse_object(self, list_of_rows, doc_pandas_rows, coords):
        for ix, (row, pd_row) in enumerate(zip(list_of_rows, doc_pandas_rows)):
            if '(наименование объекта)' in row:
                interim = list_of_rows[ix-1]
                #print(interim)
                st_ix = interim.find('\"') 
                st_ix = st_ix if st_ix > 0 else 0
                end_ix = interim.find('\"', st_ix+1)
                end_ix = end_ix if end_ix > 0 else len(interim) - 1

                interim_pd = doc_pandas_rows[ix-1]
                return interim[st_ix:end_ix+1], [x.ocr_id if hasattr(x, 'ocr_id') else 'no ocr_id column' for x in pd_row] + \
                    [x.ocr_id if hasattr(x, 'ocr_id') else 'no ocr_id column' for x in interim_pd]
        return None, []

    def parse_inventory_number(self, list_of_rows, doc_pandas_rows):
        return None
    
    def parse_build_year(self, list_of_rows, doc_pandas_rows):
        for row, pd_row in zip(list_of_rows, doc_pandas_rows):
            if 'год постройки' in row:
                match = YEAR_FINDER.find(row)
                if match.tokens:
                    return str(match.tokens[0].value), [x.ocr_id if hasattr(x, 'ocr_id') else 'no ocr_id column' for x in pd_row]
        return None, []
    
    def parse_comisssioning_year(self, list_of_rows, doc_pandas_rows):
        for row, pd_row in zip(list_of_rows, doc_pandas_rows):
            if ('год' in row and 'эксплуатацию' in row) or similar('год ввода в эксплуатацию (завершения строительства)', row, 0.7):
                match = YEAR_FINDER.find(row)
                if match.tokens:
                    return str(match.tokens[0].value), [x.ocr_id if hasattr(x, 'ocr_id') else 'no ocr_id column' for x in pd_row]
        return None, []
    
    def parse_cadastre_number_ZU(self, list_of_rows, doc_pandas_rows, coords):
        line = ' '.join(list_of_rows)

        start_pattn = 'расположен объект'
        end_pattn = 'назначение'

        try:
            st_ix = line.find(start_pattn)
            field = line[st_ix + len(start_pattn): line.find(end_pattn, st_ix)].replace(' ', '')
            if field:
                return field
        except Exception as e:
            print(f"Error {e}")
        
        start_pattn = 'участка, в пределах'
        end_pattn = 'которого расположен объект'

        try:
            st_ix = line.find(start_pattn)
            return line[st_ix + len(start_pattn): line.find(end_pattn, st_ix)].replace(' ', '')
        except Exception as e:
            print(f"Error {e}")

        return None
    
    def parse_cadastre_number_OKS(self, list_of_rows, doc_pandas_rows):
        return None
    
    def parse_fields(self, list_of_rows, coords=None, doc_pandas_rows=None):
        date = self.parse_date(list_of_rows,doc_pandas_rows)
        answers = [self.parse_doc_number(list_of_rows, doc_pandas_rows), 
                   date,
                   self.parse_issuer(list_of_rows, doc_pandas_rows),
                   date,
                   self.parse_object(list_of_rows, doc_pandas_rows,coords),
                   self.parse_inventory_number(list_of_rows, doc_pandas_rows),
                   self.parse_build_year(list_of_rows, doc_pandas_rows),
                   self.parse_comisssioning_year(list_of_rows, doc_pandas_rows),
                   self.parse_cadastre_number_ZU(list_of_rows, doc_pandas_rows, coords),
                   self.parse_cadastre_number_OKS(list_of_rows, doc_pandas_rows)]
        answers = [x if x is not None else [] for x in answers]
        ocr_ids = [ [] for x in answers]


        return dict(zip(FIELD_NAMES, answers)), dict(zip(FIELD_NAMES, ocr_ids))