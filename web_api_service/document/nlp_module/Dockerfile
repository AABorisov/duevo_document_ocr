FROM python:3.7.7-buster

# WARNING: you must place google cloud json file into wrapper/config!!!

USER root
# Tesseract
RUN apt update && apt install -y tesseract-ocr libtesseract-dev

WORKDIR /root/app

# python packages
ADD requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .

WORKDIR /root/app/wrapper
RUN chmod 0777 main.py

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/root/app"

CMD ["python3", "/root/app/wrapper/main.py"]
