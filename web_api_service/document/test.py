import os
from pathlib import Path

from pdf2image import convert_from_path


BASE_DIR = Path(__file__).resolve().parent.parent

pdf_folder = os.path.join(BASE_DIR, 'static', 'pdf')
pdf_pages = os.path.join(BASE_DIR, 'static', 'pdf_pages')

files = os.scandir(pdf_folder)

print(pdf_folder)
print(files)

for file in files:
    if file.is_dir() or file.is_file():
        print(file.name)

        file_path = os.path.join(pdf_folder, file.name)
        print(file_path)

        # Work with PDF
        pages = convert_from_path(file_path, 200)

        print(pages)
        cnt = 0
        for page in pages:
            cnt += 1
            jpeg_name = os.path.join(pdf_pages, str(cnt) + '.jpeg')
            page.save(jpeg_name, 'JPEG')

