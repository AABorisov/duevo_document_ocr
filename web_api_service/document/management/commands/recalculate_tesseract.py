from django.core.management.base import BaseCommand, CommandError
from document.nlp_module.doc.parser import Parser
import csv
from document.models import *
from document_processing import settings
from document.nlp_module.doc.ocr import *

class Command(BaseCommand):
    args = ''
    help = 'Export data to remote server'

    def handle(self, *args, **options):
        """
        def postprocess(self, df):
        df = df[~pd.isna(df['text'])]
        df = df[df['text']!=' ']
        df = df.reset_index(drop=True)
        data = pd.DataFrame([{
            'text':t.text,
            'upper_left_y':t.top,
            'upper_left_x':t.left,
            'upper_right_y':t.top,
            'upper_right_x':t.left + t.width,
            'lower_right_y':t.top + t.height,
            'lower_right_x':t.left + t.width,
            'lower_left_y':t.top + t.height,
            'lower_left_x':t.left,
        } for t in list(df.itertuples())])
        data = data.sort_values(['upper_left_y', 'upper_left_x']).reset_index(drop=1)
        return data
        """
        """        """
        csv_path = os.path.join(settings.BASE_DIR, 'document/management/commands/saved', 'test.csv')
        ocrs = OcrTesseract.objects.filter(page__document_id=41)
        row_list = [
            ['ocr_id', 'text', 'upper_left_y', 'upper_left_x', 'upper_right_y', 'upper_right_x', 'lower_right_y',
             'lower_right_x', 'lower_left_y', 'lower_left_x']]
        for ocr in ocrs:
            row_list.append(
                [ocr.id, ocr.ocr_text, ocr.upper_left_y, ocr.upper_left_x, ocr.upper_right_y, ocr.upper_right_x,
                 ocr.lower_right_y, ocr.lower_right_x, ocr.lower_left_y, ocr.lower_left_x])
        
        with open(csv_path, 'w', newline='') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerows(row_list)
        p = Parser()
        answer = p.parse([csv_path], 2)
        print(answer)

        # jpg_path = os.path.join(settings.BASE_DIR, 'document/management/commands/saved', '41_414.jpeg')
        #csv_path = os.path.join(settings.BASE_DIR, 'document/management/commands/saved', 't.csv')
        # t_ocr = TesseractOCR()
        # df = t_ocr.detect(jpg_path)
        # print(df)
        # data = t_ocr.postprocess(df)
        # data.to_csv(csv_path, index=False)
        # print(data)
        # df.to_csv(csv_path, index=False)
        # p = Parser()
        # answer = p.parse([csv_path], 5)
        #
        # print(answer)