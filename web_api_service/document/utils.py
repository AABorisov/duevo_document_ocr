import csv
import datetime
import json
import pathlib
import re
import time
import uuid
import shutil
from typing import Optional, Union

import dateparser
from django.db.models import QuerySet
from matplotlib import pyplot as plt, patches
from django.core.mail import send_mail
from django.db import connection, connections
from pdf2image import convert_from_path

from document.models import *
from document.nlp_module.doc.parser import Parser
from document_processing import settings


def convert_any_date_format_to_date(any_format: str) -> Optional[str]:
    """Принимает на вход любой формат и конвертирует его в дату"""
    raw_date = any_format.lower()
    dt = re.sub('[^а-яa-z0-9\ \.\-]+', '', raw_date)
    res = dateparser.parse(dt)
    if res:
        return res.strftime("%Y-%m-%d")
    return res


def generate_random_name(filename):
    uuid.uuid1()


def is_file_exists(original_name):
    try:
        file = File.objects.get(original_name__exact=original_name)
        return file.id
    except File.DoesNotExist:
        return False


def get_labels_for_stacked_chart(documents):
    labels = []
    for document in documents:
        created_date = document.created_at.strftime('%Y-%m-%d')
        if created_date not in labels:
            labels.append(created_date)

    return labels


def get_datasets_for_stacked_chart(labels, documents):
    datasets = []
    data_1 = []
    data_2 = []
    data_3 = []
    data_4 = []
    data_5 = []
    data_6 = []
    data_7 = []
    data_8 = []
    data_undefined = []
    # Get statuses
    statuses = Status.objects.all()

    for label in labels:
        count_statuses_1 = documents.filter(created_at__contains=label, status_id=1).count()
        count_statuses_2 = documents.filter(created_at__contains=label, status_id=2).count()
        count_statuses_3 = documents.filter(created_at__contains=label, status_id=3).count()
        count_statuses_4 = documents.filter(created_at__contains=label, status_id=4).count()
        count_statuses_5 = documents.filter(created_at__contains=label, status_id=5).count()
        count_statuses_6 = documents.filter(created_at__contains=label, status_id=6).count()
        count_statuses_7 = documents.filter(created_at__contains=label, status_id=7).count()
        count_statuses_8 = documents.filter(created_at__contains=label, status_id=8).count()
        data_1.append(count_statuses_1)
        data_2.append(count_statuses_2)
        data_3.append(count_statuses_3)
        data_4.append(count_statuses_4)
        data_5.append(count_statuses_5)
        data_6.append(count_statuses_6)
        data_7.append(count_statuses_7)
        data_8.append(count_statuses_8)
        data_undefined.append(0)

    for status in statuses:

        if status.id == 1:
            data = data_1
        elif status.id == 2:
            data = data_2
        elif status.id == 3:
            data = data_3
        elif status.id == 4:
            data = data_4
        elif status.id == 5:
            data = data_5
        elif status.id == 6:
            data = data_6
        elif status.id == 7:
            data = data_7
        elif status.id == 8:
            data = data_8
        else:
            data = data_undefined

        datasets.append({
            "label": status.title,
            "backgroundColor": status.color,
            "borderColor": status.color,
            "pointRadius": False,
            "pointColor": 'rgba(210, 214, 222, 1)',
            "pointStrokeColor": status.color,
            "pointHighlightFill": '#fff',
            "pointHighlightStroke": status.color,
            "data": data
        })

    return datasets


def get_labels_for_donut_chart():
    labels = []
    statuses = Status.objects.all()

    for status in statuses:
        labels.append(status.title)
    return json.dumps(labels)


def get_datasets_for_donut_chart(document_ids_list):
    statuses = Status.objects.all()
    datasets = []
    data = []
    background_color = []
    for status in statuses:
        documents_amount = Document.objects.filter(status=status, is_active=True, id__in=document_ids_list).count()
        print(documents_amount)
        data.append(documents_amount)
        background_color.append(status.color)

    datasets.append({
        "data": data,
        "backgroundColor": background_color
    })

    return json.dumps(datasets)


def get_last_page_id():
    page = Page.objects.last()
    if page is None:
        return 1
    else:
        return page.id + 1


def get_nextautoincrement(model):
    cur = connection.cursor()
    cur.execute(
        "SELECT Auto_increment FROM information_schema.tables WHERE TABLE_SCHEMA = 'document_processing' AND table_name='%s';" % model._meta.db_table)
    row = cur.fetchone()
    cur.close()
    return row[0]


def create_pages_json(pages):
    pages_array = []
    for page in pages:
        words_array = []
        page_charts = []

        # Get words coordinates for specific page
        ocrs = Ocr.objects.filter(page_id=page.id)
        document_id = page.document_id
        page_id = page.page_id
        for ocr in ocrs:
            words_array.append({
                "id": ocr.id,
                "doc_id": document_id,
                "page_id": page_id,
                "ocr_text": ocr.ocr_text,
                "user_text": ocr.user_text,
                "y0": ocr.upper_left_y,
                "x0": ocr.upper_left_x,
                "y1": ocr.lower_right_y,
                "x1": ocr.lower_right_x,
                "status": ocr.status,
            })
        # Get charts coordinates and orientation for specific page
        charts = Schema.objects.filter(page_id=page.id)
        for chart in charts:
            page_charts.append({
                "page_id": page_id,
                "chart_link": chart.link,
                "orientation": chart.orientation,
                "upper_left_y": chart.upper_left_y,
                "upper_left_x": chart.upper_left_x,
                "upper_right_y": chart.upper_right_y,
                "upper_right_x": chart.upper_right_x,
                "lower_right_y": chart.lower_right_y,
                "lower_right_x": chart.lower_right_x,
                "lower_left_y": chart.lower_left_y,
                "lower_left_x": chart.lower_left_x,
            })

        pages_array.append({
            "page_id": page.id,
            "page_link": page.page_link,
            "page_link_local": page.page_image.url,
            "page_link_local_thumbnail": page.page_thumbnail.url,
            "words_coordinates": words_array,
            "charts": page_charts,
        })
    return json.dumps(pages_array)


def create_pages_json_tesseract(pages):
    pages_array = []
    for page in pages:
        words_array = []
        page_charts = []

        # Get words coordinates for specific page
        ocrs = OcrTesseract.objects.filter(page_id=page.id)
        document_id = page.document_id
        page_id = page.page_id
        for ocr in ocrs:
            words_array.append({
                "id": ocr.id,
                "doc_id": document_id,
                "page_id": page_id,
                "ocr_text": ocr.ocr_text,
                "user_text": ocr.user_text,
                "y0": ocr.upper_left_y,
                "x0": ocr.upper_left_x,
                "y1": ocr.lower_right_y,
                "x1": ocr.lower_right_x,
                "status": ocr.status,
            })
        # Get charts coordinates and orientation for specific page
        charts = Schema.objects.filter(page_id=page.id)
        for chart in charts:
            page_charts.append({
                "page_id": chart.page.id,
                "chart_link": page_id,
                "orientation": chart.orientation,
                "upper_left_y": chart.upper_left_y,
                "upper_left_x": chart.upper_left_x,
                "upper_right_y": chart.upper_right_y,
                "upper_right_x": chart.upper_right_x,
                "lower_right_y": chart.lower_right_y,
                "lower_right_x": chart.lower_right_x,
                "lower_left_y": chart.lower_left_y,
                "lower_left_x": chart.lower_left_x,
            })

        pages_array.append({
            "page_id": page_id,
            "page_link": page.page_link,
            "page_link_local": page.page_image.url,
            "page_link_local_thumbnail": page.page_thumbnail.url,
            "words_coordinates": words_array,
            "charts": page_charts,
        })
    return json.dumps(pages_array)


def get_tree_view_menu():
    doc_classes = DocumentType.objects.all()

    # loop through classes
    doc_class_array = []
    for doc_class in doc_classes:
        doc_results = TesseractClassifier.objects.filter(document_type_id=doc_class.id)

        # loop through doc results
        document_array = []
        for doc_result in doc_results:

            try:
                document = Document.objects.get(id=doc_result.document_id, is_active=True)
                pages = Page.objects.filter(document=document)
                # loop through pages
                page_array = []
                for page in pages:
                    page_array.append({
                        "page_id": page.id,
                        "page_title": page.original_name,
                        "page_thumbnail": page.page_thumbnail,
                        "page_number": page.page_number,
                        "page_description": page.description,
                        "page_status": page.status_id,
                    })
                document_array.append({
                    "document_id": document.id,
                    "document_title": document.file.original_name,  # document.file.original_name
                    "document_description": document.description,
                    "document_path": document.file.file_path,  # document.file.file_path
                    "document_status": document.status_id,
                    "document_pages": page_array,
                })
            except Document.DoesNotExist:
                print('Document not exists')
                continue

        # Add to doc_class_array
        doc_class_array.append({
            "doc_class_id": doc_class.id,
            "doc_class_name": doc_class.doc_type_name,
            "doc_class_documents": document_array,
        })
    return doc_class_array


# def get_attributes_nlp_ocr(nlp_id):
#     attributes = {}
#     number_ids = []
#     date_ids = []
#     issuing_authority_ids = []
#     customer_ids = []
#     builder_ids = []
#     project_organization_ids = []
#     project_author_manager_ids = []
#
#     nlp_ocr_data = NlpOcr.objects.filter(nlp_id=nlp_id).using('ocr')
#     print('NLP OCR')
#     numbers = nlp_ocr_data.filter(attribute='number').using('ocr')
#     dates = nlp_ocr_data.filter(attribute='date').using('ocr')
#     issuing_authorities = nlp_ocr_data.filter(attribute='issuing_authority').using('ocr')
#     customers = nlp_ocr_data.filter(attribute='customer').using('ocr')
#     builders = nlp_ocr_data.filter(attribute='builder').using('ocr')
#     project_organizations = nlp_ocr_data.filter(attribute='project_organization').using('ocr')
#     project_author_managers = nlp_ocr_data.filter(attribute='project_author_manager').using('ocr')
#
#     for number in numbers:
#         number_ids.append(number.ocr_id)
#
#     for date in dates:
#         date_ids.append(date.ocr_id)
#
#     for issuing_authority in issuing_authorities:
#         issuing_authority_ids.append(issuing_authority.ocr_id)
#
#     for customer in customers:
#         customer_ids.append(customer.ocr_id)
#
#     for builder in builders:
#         builder_ids.append(builder.ocr_id)
#
#     for project_organization in project_organizations:
#         project_organization_ids.append(project_organization.ocr_id)
#
#     for project_author_manager in project_author_managers:
#         project_author_manager_ids.append(project_author_manager.ocr_id)
#
#     attributes = {
#         'number': number_ids,
#         'date': date_ids,
#         'issuing_authority': issuing_authority_ids,
#         'customer': customer_ids,
#         'builder': builder_ids,
#         'project_organization': project_organization_ids,
#         'project_author_manager': project_author_manager_ids,
#     }
#
#     return attributes


def create_json_empty_nlp_table(document_id):
    doc_class_id = 6
    nlp_id = 0
    attributes = []
    return None


def get_search_text(document_id: int, attribute_link_name: str) -> Optional[str]:
    try:
        nlp_result = NlpResult.objects.get(document_id=document_id)
        result = getattr(nlp_result, attribute_link_name)
    except NlpResult.DoesNotExist:
        print('NlpResult.DoesNotExist')
        result = None
    return result


def get_search_nlp_result(document_id: int, attribute_link_name: str, search_text: str) -> Optional[NlpResult]:
    search_type = 'iexact'
    if search_text is None:
        return None
    column_filter = attribute_link_name + '__' + search_type
    nlp_result = NlpResult.objects.filter(**{column_filter: search_text}).exclude(document_id=document_id)
    return nlp_result


def count_linked_documents(document_id: int, attribute_link_name: str) -> Optional[int]:
    """Получаем количество одинаковых атрибутов"""
    search_text = get_search_text(document_id, attribute_link_name)
    if search_text is None:
        return None
    nlp_results = get_search_nlp_result(document_id, attribute_link_name, search_text)
    return nlp_results.count()


def get_linked_documents(document_id: int, attribute_link_name: str, attribute_link_id: int) -> Optional[list]:
    """Получаем список связанных документов"""
    linked_documents = []

    search_text = get_search_text(document_id, attribute_link_name)
    if search_text is None:
        return None
    nlp_results = get_search_nlp_result(document_id, attribute_link_name, search_text)

    for nlp_result in nlp_results:
        document = Document.objects.get(id=nlp_result.document_id)
        classification = Classification.objects.get(document_id=nlp_result.document_id)

        attribute_id = None
        attribute_name = None
        ocr_text = None
        try:
            nlp = Nlp.objects.get(document_id=document.id, attribute__attribute_link_id=attribute_link_id)
            attribute_id = nlp.attribute.id
            attribute_name = nlp.attribute.attribute_name
            ocr_text = search_text
        except Nlp.DoesNotExist:
            print('Nlp.DoesNotExist')
            continue

        linked_documents.append({
            "document_id": nlp_result.document_id,
            "document_name": document.file.original_name,
            "doc_class_id": classification.document_type_id,
            "doc_class_name": classification.document_type.doc_type_name,
            "ocr_engines": ['google'],
            "nlp": {
                "attribute_id": attribute_id,
                "attribute_name": attribute_name,
                "ocr_text": ocr_text.isoformat() if isinstance(ocr_text, datetime.date) else ocr_text
            }
        })

    return linked_documents


def create_json_nlp_table(document_id: int, active_page_id: int) -> dict:
    """
    , {
          document_id: 25,
          document_name: '2.pdf',
          doc_class_id: 2,
          doc_class_name: 'ЗУ',
          ocr_engines: ['google'],
          nlp: {
            attribute_id: 2,
            attribute_name: ‘Кадастровый номер БТИ’,
            ocr_text: ‘тот самый номер’
          },
        },
    @param document_id:
    @return:
    """
    # Check if we determine document classification
    try:
        classification = Classification.objects.get(document_id=document_id)
        doc_class_name = classification.document_type.doc_type_name
        doc_class_id = classification.document_type.id
    except Classification.DoesNotExist:
        print('Classification.DoesNotExist')
        return json_empty_nlp(document_id)

    nlps = Nlp.objects.filter(document_id=document_id)

    # Add nlp attribute to array
    nlp_attr_array = []
    for nlp in nlps:
        nlp_attr_array.append({
            "nlp_id": nlp.id,
            "attribute_id": nlp.attribute_id,
            "attribute_name": nlp.attribute.attribute_name,
            "attribute_category_id": nlp.attribute.attribute_category.id if nlp.attribute.attribute_category else None,
            "attribute_category_name": nlp.attribute.attribute_category.category_name if nlp.attribute.attribute_category else None,
            "ocr_word_ids": nlp.ocr_word_ids,
            "ocr_text": nlp.ocr_text,
            "status": nlp.status,
            # linked docs
            "link_id": nlp.attribute.attribute_link_id if nlp.attribute.attribute_link_id else None,
            "link_name": nlp.attribute.attribute_link.description if nlp.attribute.attribute_link_id else None,
            "documents_count": count_linked_documents(document_id,
                                                      nlp.attribute.attribute_link.attribute_link_name) if nlp.attribute.attribute_link_id else 0,
            "documents": get_linked_documents(document_id, nlp.attribute.attribute_link.attribute_link_name,
                                              nlp.attribute.attribute_link_id) if nlp.attribute.attribute_link_id else None,
        })

    # Create NLP dict
    nlp_dict = {
        "document_id": document_id,
        "active_page_id": None if active_page_id == 0 else active_page_id,
        "doc_class_id": doc_class_id,
        "doc_class_name": doc_class_name,
        "nlp_table": nlp_attr_array
    }

    nlp_data = {
        "nlp_json": json.dumps(nlp_dict),
        "nlp_dict": nlp_dict,
    }

    return nlp_data


def create_json_nlp_tesseract_table(document_id: int, active_page_id: int) -> dict:
    """Передаем таблицу nlp_tesseract с атрибутами"""
    # Check if we determine document classification
    try:
        classification = TesseractClassifier.objects.get(document_id=document_id)
        doc_class_name = classification.document_type.doc_type_name
        doc_class_id = classification.document_type.id
    except TesseractClassifier.DoesNotExist:
        print('TesseractClassifier.DoesNotExist')
        return json_empty_nlp(document_id)

    nlps = NlpTesseract.objects.filter(document_id=document_id)

    # Add nlp attribute to array
    nlp_attr_array = []
    for nlp in nlps:
        nlp_attr_array.append({
            "nlp_id": nlp.id,
            "attribute_id": nlp.attribute.id,
            "attribute_name": nlp.attribute.attribute_name,
            "attribute_category_id": nlp.attribute.attribute_category.id if nlp.attribute.attribute_category else None,
            "attribute_category_name": nlp.attribute.attribute_category.category_name if nlp.attribute.attribute_category else None,
            "ocr_word_ids": nlp.ocr_word_ids,
            "ocr_text": nlp.ocr_text,
            "status": nlp.status,
        })

    # Create NLP dict
    nlp_dict = {
        "document_id": document_id,
        "active_page_id": None if active_page_id == 0 else active_page_id,
        "doc_class_id": doc_class_id,
        "doc_class_name": doc_class_name,
        "nlp_table": nlp_attr_array
    }

    nlp_data = {
        "nlp_tesseract_json": json.dumps(nlp_dict),
        "nlp_tesseract_dict": nlp_dict,
    }

    return nlp_data


def get_available_attributes(document_id):
    """
    Return all available attributes
    @param document_id: int
    @return: dict
    """
    # Check if we determine document classification
    # try:
    #     doc_classification = Classification.objects.get(document_id=document_id)
    #     attributes = Attribute.objects.filter(document_type_id=doc_classification.document_type.id, is_active=1)
    # except Classification.DoesNotExist:
    #     print('Document.DoesNotExist')

    doc_types = DocumentType.objects.filter(is_active=1)

    doc_type_array = []
    for doc_type in doc_types:
        attr_array = []
        attributes = Attribute.objects.filter(document_type_id=doc_type.id, is_active=1)
        for attribute in attributes:
            attr_array.append({
                "attribute_id": attribute.id,
                "attribute_name": attribute.attribute_name,
                # "attribute_category_id": attribute.attribute_category_id if attribute.attribute_category else None,
                # "attribute_category_name": attribute.attribute_category.category_name if attribute.attribute_category else None,
            })

        doc_type_array.append({
            "doc_class_id": doc_type.id,
            "doc_class_name": doc_type.doc_type_name,
            "attributes": attr_array
        })

        available_attributes_data = {
            "available_attributes_json": json.dumps(doc_type_array, ensure_ascii=False).encode('utf8'),
            "available_attributes_dict": doc_type_array,
        }

    return available_attributes_data


def create_json_nlp_class_5(document_id):
    nlps = SvidAgrDocuments.objects.filter(doc_id=document_id).using('ocr')
    for nlp in nlps:
        attributes = []
        nlp_ocr_data = NlpOcr.objects.filter(nlp=nlp)

        nlp_json = {
            "id": nlp.id,
            "doc_id": document_id,
            "class_id": nlp.class_field.id,
            "class_name": nlp.class_field.class_name,
            "number": nlp.number,
            "date": nlp.date,
            "issuing_authority": nlp.issuing_authority,
            "administrative_district": nlp.administrative_district,
            "district": nlp.district,
            "address": nlp.address,
            "object_name": nlp.object_name,
            "functional_purpose_of_object": nlp.functional_purpose_of_object,
            "customer": nlp.customer,
            "builder": nlp.builder,
            "project_organization": nlp.project_organization,
            "project_author_manager": nlp.project_author_manager,
            "attributes": get_attributes_nlp_ocr(nlp.id)
        }
        print('----------------------------------------------')
        print(get_attributes_nlp_ocr(nlp))
        nlp_data = {
            "nlp_json": json.dumps(nlp_json),
            "nlp_dict": nlp_json,

        }
        return nlp_data


# def json_empty_nlp(document_id):
#     doc_class_id = 6
#     nlp_id = 0
#     attributes = {
#         'number': [],
#         'date': [],
#         'issuing_authority': [],
#         'customer': [],
#         'builder': [],
#         'project_organization': [],
#         'project_author_manager': [],
#     }
#     try:
#         nlp_tbl = SvidAgrDocuments.objects.using('ocr').get(doc_id=document_id)
#         nlp_id = nlp_tbl.id
#     except SvidAgrDocuments.DoesNotExist:
#         print('SvidAgrDocuments.DoesNotExist')
#
#     try:
#         doc_class = Classification.objects.get(document_id=document_id)
#         doc_class_id = doc_class.class_field.id
#     except DocClassificationResults.DoesNotExist:
#         print('DocClassificationResults.DoesNotExist')
#
#     nlp = {
#         "id": nlp_id,
#         "doc_id": document_id,
#         "class_field": doc_class_id,
#         "number": None,
#         "date": None,
#         "issuing_authority": None,
#         "administrative_district": None,
#         "district": None,
#         "address": None,
#         "object_name": None,
#         "functional_purpose_of_object": None,
#         "customer": None,
#         "builder": None,
#         "project_organization": None,
#         "project_author_manager": None,
#         "attributes": get_attributes_nlp_ocr(nlp_id)
#     }
#     nlp_data = {
#         "nlp_json": json.dumps(nlp),
#         "nlp_dict": nlp,
#     }
#     return nlp_data


# def create_json_nlp(document_id):
#     try:
#         doc_class = DocClassificationResults.objects.using('ocr').get(doc_id=document_id)
#         if doc_class.class_field.id == 5:
#             return create_json_nlp_class_5(document_id)
#     except DocClassificationResults.DoesNotExist:
#         print('DocClassificationResults.DoesNotExist')
#     return json_empty_nlp(document_id)


def get_doc_class_data():
    """
    Return all documents types
    @return: dict
    """
    doc_types = DocumentType.objects.all()
    doc_types_array = []
    for doc_type in doc_types:
        doc_types_array.append({
            "doc_class_id": doc_type.id,
            "doc_class_name": doc_type.doc_type_name,
        })

    doc_type_data = {
        "doc_class_json": json.dumps(doc_types_array),
        "doc_class_dict": doc_types_array,
    }

    return doc_type_data


def get_doc_class_id(document_id: int) -> int:
    """
    Get document type by doc_id, if there is no document in classification table return doc_type_id - 6
    @param document_id: int
    @return: int
    """
    document_type_id = 6
    try:
        doc_classification = Classification.objects.get(document_id=document_id)
        document_type_id = doc_classification.document_type.id
    except Classification.DoesNotExist:
        print('Classification.DoesNotExist')

    return document_type_id


# def get_nlp_number_dict():
#     nlps = SvidAgrDocuments.objects.distinct('number').using('ocr')
#     number_array = []
#     for nlp in nlps:
#         number_array.append({
#             "number": nlp.number
#         })
#     return number_array


# def get_nlp_date_dict():
#     nlps = SvidAgrDocuments.objects.distinct('date').using('ocr')
#     date_array = []
#     for nlp in nlps:
#         date_array.append({
#             "date": nlp.date
#         })
#     return date_array


# def get_nlp_authority_dict():
#     nlps = SvidAgrDocuments.objects.distinct('issuing_authority').using('ocr')
#     issuing_authority_array = []
#     for nlp in nlps:
#         issuing_authority_array.append({
#             "issuing_authority": nlp.issuing_authority
#         })
#     return issuing_authority_array


def nlp_distinct_data_old(field_name):
    nlps = NlpResult.objects.distinct(field_name)
    date_array = []
    for nlp in nlps:
        if getattr(nlp, field_name):
            date_array.append({
                field_name: getattr(nlp, field_name)
            })
    return date_array


def nlp_distinct_data(field_name):
    nlps = NlpResult.objects.all().values(field_name).distinct()
    data_array = []

    for nlp in nlps:
        val = nlp[field_name]
        if val is None:
            continue
        data_array.append({
            field_name: val
        })

    return data_array


def nlp_customer_dict():
    nlps = NlpResult.objects.distinct('customer')
    date_array = []
    for nlp in nlps:
        if nlp.customer:
            date_array.append({
                "customer": nlp.customer
            })
    return date_array


def get_doc_name(document_id):
    doc_name = ''
    try:
        document = Document.objects.get(id=document_id)
        doc_name = document.original_name
    except Document.DoesNotExist:
        print('Document.DoesNotExist')
    return doc_name


def check_session_key_not_empty(session, key):
    """Если приходит ключ __all__ то значит пользователь выбрал все значения в фильтре"""
    if key in session:
        if str(session[key]) == "__all__" or session[key] is None:
            return False
        else:
            return True
    return False


def add_new_ocr_record(x0: int, y0: int, x1: int, y1: int, user_text: str, page_id: int, document_id: int) -> Ocr:
    """Записываем в базу новый OCR"""
    ocr = Ocr.objects.create(
        document_id=document_id,
        page_id=page_id,
        user_text=user_text,
        upper_left_y=y0,
        upper_left_x=x0,
        lower_right_y=y1,
        lower_right_x=x1,
        status=4
    )

    return ocr


def add_nlp_record(document_id: int, attribute_id: int, ocr_word_ids: list) -> Optional[Nlp]:
    """Добавление NLP TESSERACT записи"""

    try:
        nlp = Nlp.objects.create(
            document_id=document_id,
            attribute_id=attribute_id,
            ocr_word_ids=ocr_word_ids,
            status=4,
        )
    except Exception as e:
        print(e)
        return None

    return nlp


def add_new_ocr_tesseract_record(upper_left_y, upper_left_x, lower_right_y, lower_right_x, upper_right_y, upper_right_x, lower_left_y, lower_left_x, user_text: str, page_id: int) -> OcrTesseract:
    """Записываем в базу новый OCR TESSERACT"""
    ocr = OcrTesseract.objects.create(
        page_id=page_id,
        user_text=user_text,
        upper_left_y=upper_left_y,
        upper_left_x=upper_left_x,
        lower_right_y=lower_right_y,
        lower_right_x=lower_right_x,
        upper_right_y=upper_right_y,
        upper_right_x=upper_right_x,
        lower_left_y=lower_left_y,
        lower_left_x=lower_left_x,
        status=4
    )

    return ocr


def edit_nlp_record(nlp_id: int, ocr_word_ids: list, ocr_text: Optional[str]) -> Optional[Nlp]:
    """Редактирование NLP TESSERACT записи"""
    try:
        nlp = Nlp.objects.get(id=nlp_id)
        nlp.ocr_word_ids = ocr_word_ids
        if ocr_text is not None:
            nlp.ocr_text = ocr_text
        if nlp.status != 4:
            nlp.status = 3
        nlp.save()
    except Nlp.DoesNotExist:
        print('Nlp.DoesNotExist')
        return None
    return nlp


def edit_nlp_tesseract_record(nlp_id: int, ocr_word_ids: list, ocr_text: Optional[str]) -> Optional[NlpTesseract]:
    """Редактирование NLP TESSERACT записи"""
    try:
        nlp = NlpTesseract.objects.get(id=nlp_id)
        nlp.ocr_word_ids = ocr_word_ids
        if ocr_text is not None:
            nlp.ocr_text = ocr_text
        if nlp.status != 4:
            nlp.status = 3
        nlp.save()
    except NlpTesseract.DoesNotExist:
        print('NlpTesseract.DoesNotExist')
        return None
    return nlp


def add_nlp_tesseract_record(document_id: int, attribute_id: int, ocr_word_ids: list) -> Optional[NlpTesseract]:
    """Добавление NLP TESSERACT записи"""

    try:
        nlp = NlpTesseract.objects.create(
            document_id=document_id,
            attribute_id=attribute_id,
            ocr_word_ids=ocr_word_ids,
            status=4,
        )
    except Exception as e:
        print(e)
        return None

    return nlp


def test_mail(user_email: str) -> None:
    try:
        send_mail(
            'Subject here',
            'Here is the message.',
            'labsdev@yandex.ru',
            [user_email],
            fail_silently=False,
        )
    except Exception as e:
        print('Problem')
        print(e)


def document_to_images_converter(document_path: str, document_id: int) -> str:
    page_short_path = 'pages'
    # Creates pages dir
    pages_path = os.path.join(settings.MEDIA_ROOT, page_short_path)

    # Check if dir "pages" exists
    if not os.path.exists(pages_path):
        os.mkdir(pages_path)

    pages_document_path = os.path.join(pages_path, str(document_id))

    # Check if dir "pages/document_id" exists
    if not os.path.exists(pages_document_path):
        os.makedirs(pages_document_path)

    # Work with PDF
    print('Start PDF convert')
    pages = convert_from_path(document_path, 200)

    cnt = 0
    for page in pages:
        cnt += 1
        last_page_id = str(get_nextautoincrement(Page))
        print('LAST PAGE ID: ' + last_page_id)
        print('DOC ID: ' + str(document_id))
        new_page_name = str(document_id) + '_' + last_page_id + '.jpeg'
        jpeg_path = os.path.join(pages_document_path, new_page_name)
        jpeg_short_path = os.path.join(page_short_path, str(document_id), new_page_name)

        print(jpeg_path)
        page.save(jpeg_path, 'JPEG')
        print('NEW PAGE NAME: ' + jpeg_short_path)

        # Save page to DB
        page_db = Page.objects.create(

            document_id=document_id,
            status_id=1,
            original_name=new_page_name,
            page_number=cnt,
            page_image=jpeg_short_path,
            # response info
            is_sent_to_server=False
        )

    # Return path to folder with pages (images)
    return pages_document_path


def file_to_images_converter(file_path: str) -> str:
    """Разбиваем PDF на картинки и сохраняем во временную директорию"""
    # Creates 'timestamp' folder
    timestamp_folder = str(int(time.time()))
    tmp_pages_folder = os.path.join(settings.MEDIA_ROOT, 'tmp_pages', timestamp_folder)
    if not os.path.exists(tmp_pages_folder):
        pathlib.Path(tmp_pages_folder).mkdir(parents=True, exist_ok=True)

    # Work with PDF
    print('Start PDF convert')
    pages = convert_from_path(file_path, 200)

    cnt = 0
    print('JPEG TMP PATH: ' + tmp_pages_folder)

    for page in pages:
        cnt += 1
        new_page_name = str(cnt) + '.jpeg'
        jpeg_path = os.path.join(tmp_pages_folder, new_page_name)
        print(jpeg_path)
        page.save(jpeg_path, 'JPEG')

    # Return path to folder with pages (images)
    return tmp_pages_folder


def add_ocr_tesseract_record(upper_left_y: int, upper_left_x: int, upper_right_y: int, upper_right_x: int,
                             lower_right_y: int, lower_right_x: int, lower_left_y: int, lower_left_x: int,
                             ocr_text: str, page_id: int) -> OcrTesseract:
    """Добавление одного слова в таблицу с координатами ocr_tesseract"""
    ocr_tesseract = OcrTesseract.objects.create(
        page_id=page_id,
        ocr_text=ocr_text,
        upper_left_y=upper_left_y,
        upper_left_x=upper_left_x,
        upper_right_y=upper_right_y,
        upper_right_x=upper_right_x,

        lower_right_y=lower_right_y,
        lower_right_x=lower_right_x,
        lower_left_y=lower_left_y,
        lower_left_x=lower_left_x,
        status=2
    )

    return ocr_tesseract


def add_record_tesseract_classifier(document_id: int, document_type_id: int) -> TesseractClassifier:
    print('===================DOC TYPE ID+++++++++++++++++')
    print(document_id)
    print(document_type_id)
    tesseract_classifier = TesseractClassifier.objects.create(
        document_id=document_id,
        document_type_id=document_type_id
    )
    return tesseract_classifier


def get_year_month_day_path() -> str:
    """Возвращает год меяц день ввиде пути"""
    today = datetime.datetime.now()
    today_path = os.path.join(str(today.year), str(today.month), str(today.day))
    return today_path


def add_page_to_db_and_save_to_folder(document_id: int, image_path: str, page_number: int, dictionary: str,
                                      ocr_words: dict, im4) -> Page:
    """Сохранения страниц в БД и на Сервере (картинки) и привязка их к документу"""

    # Creates 'document_id' folder
    pages_folder = 'pages'
    next_page_id = get_nextautoincrement(Page)
    new_page_name = str(document_id) + '_' + str(next_page_id) + '.jpeg'
    processed_page_name = str(document_id) + '_' + str(next_page_id) + '_ocr_layout.jpeg'
    pages_document_path = os.path.join(settings.MEDIA_ROOT, pages_folder, str(document_id))
    # Create folder if not exists
    if not os.path.exists(pages_document_path):
        pathlib.Path(pages_document_path).mkdir(parents=True, exist_ok=True)

    new_page_path = os.path.join(pages_document_path, new_page_name)
    ocr_layout_page_path = os.path.join(pages_document_path, processed_page_name)

    short_page_path = os.path.join(pages_folder, str(document_id), new_page_name)

    # Copy page from tmp_pages to pages
    shutil.copy(image_path, new_page_path)

    # Create image with ocr layout
    plt.clf()
    # plt.imshow(im4)

    # Create jpeg with ocr layout
    for ocr_word in ocr_words:
        x0 = ocr_word['upper_left_x']
        y0 = ocr_word['upper_left_y']
        # upper_left_y + height
        height = ocr_word['lower_right_y'] - ocr_word['upper_left_y']
        width = ocr_word['lower_right_x'] - ocr_word['upper_left_x']

        ax = plt.gca()
        rect = patches.Rectangle((x0, y0),
                                 width,
                                 height,
                                 linewidth=0.5,
                                 edgecolor='cyan',
                                 fill=False)
        ax.add_patch(rect)

    plt.savefig(ocr_layout_page_path, dpi=300)

    page = Page.objects.create(
        document_id=document_id,
        status_id=1,
        page_image=short_page_path,
        original_name=new_page_name,
        page_number=page_number,
        dictionary=dictionary,
    )

    return page


def remove_ocr_record(model: Union[Ocr, OcrTesseract], ocr_id: int) -> dict:
    """Удаление записи из ocr таблиц (google, tesseract)"""
    try:
        ocr = model.objects.get(id=ocr_id)
        ocr.delete()
        return {"success": f"Ocr ID: {ocr_id} was removed"}
    except model.DoesNotExist:
        return {"error": f"Record with Ocr ID: {ocr_id} does not exist"}


def get_list_of_ocr_ids_and_glue_in_text(model: Union[Ocr, OcrTesseract], ocr_word_ids: list) -> str:
    """Достаем список слов из OCR и склеиваем их в строку"""
    text_result = ''
    for ocr_word_id in ocr_word_ids:
        try:
            ocr = model.objects.get(id=ocr_word_id)
            if ocr.status > 2:
                text_result += str(ocr.user_text) + ' '
            else:
                text_result += str(ocr.ocr_text) + ' '
        except model.DoesNotExist:
            text_result += ''

    return text_result


def glue_words_or_get_ocr_text(ocr_word_ids: Optional[list], ocr_text: str) -> str:
    """Склеиваем слова через пробел или выводим ocr текст"""
    text_result = ''

    # Check if ocr_word_ids not None
    if ocr_word_ids:
        if all(v != 0 for v in ocr_word_ids):
            text_result = get_list_of_ocr_ids_and_glue_in_text(Ocr, ocr_word_ids)
    else:
        text_result = ocr_text

    return text_result


def generate_fields_for_ocr_result() -> list:
    """Подготовить массив из словарей с полями для OCR RESULT"""
    documents = Nlp.objects.filter(is_active=True).values('document_id').distinct()

    document_list = []
    for document in documents:
        nlps = Nlp.objects.filter(document_id=document['document_id'])
        try:
            classification = Classification.objects.get(document_id=document['document_id'])
            document_type = classification.document_type.doc_type_name
        except Classification.DoesNotExist:
            document_type = 'Неизвестный тип'
        document_number = document_date = issuing_authority = cadastral_number = administrative_district = None
        district = address = object_name = customer = builder = project_organization = project_author_manager = None

        for nlp in nlps:
            nlp_dict = {}
            if nlp.attribute.attribute_link_id == 1:
                document_number = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)
                if document_number is not None:
                    document_number = document_number[:50]

            if nlp.attribute.attribute_link_id == 2:
                document_date = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)
                if document_date is not None:
                    document_date = document_date[:50]
                    document_date = convert_any_date_format_to_date(document_date)

            if nlp.attribute.attribute_link_id == 3:
                issuing_authority = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)

            if nlp.attribute.attribute_link_id == 4:
                cadastral_number = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)
                if cadastral_number is not None:
                    cadastral_number = cadastral_number[:20]

            if nlp.attribute.attribute_link_id == 5:
                administrative_district = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)
                if administrative_district is not None:
                    administrative_district = administrative_district[:200]

            if nlp.attribute.attribute_link_id == 6:
                district = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)
                if district is not None:
                    district = district[:200]

            if nlp.attribute.attribute_link_id == 7:
                address = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)

            if nlp.attribute.attribute_link_id == 8:
                object_name = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)

            if nlp.attribute.attribute_link_id == 9:
                customer = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)

            if nlp.attribute.attribute_link_id == 10:
                builder = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)

            if nlp.attribute.attribute_link_id == 11:
                project_organization = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)
                if project_organization is not None:
                    project_organization = project_organization[:200]

            if nlp.attribute.attribute_link_id == 12:
                project_author_manager = glue_words_or_get_ocr_text(nlp.ocr_word_ids, nlp.ocr_text)
                if project_author_manager is not None:
                    project_author_manager = project_author_manager[:200]

        nlp_dict = {
            "document_number": document_number,
            "document_date": document_date,
            "issuing_authority": issuing_authority,
            "cadastral_number": cadastral_number,
            "administrative_district": administrative_district,
            "district": district,
            "address": address,
            "object_name": object_name,
            "customer": customer,
            "builder": builder,
            "project_organization": project_organization,
            "project_author_manager": project_author_manager,
        }

        document_list.append({
            "document_id": document['document_id'],
            "document_type": document_type,
            "nlp_result": nlp_dict
        })

    return document_list


def synchronize_nlp_to_nlp_result(nlp_result_rows: list) -> None:
    """Синхронизация таблицы nlp в nlp_result"""
    for nlp_result_row in nlp_result_rows:
        print(nlp_result_row['document_id'])
        print(nlp_result_row['document_type'])
        print(nlp_result_row['nlp_result']['document_number'])

        try:
            nlp_result = NlpResult.objects.get(document_id=nlp_result_row['document_id'])

            # Update DB fields
            nlp_result.document_type = nlp_result_row['document_type']
            nlp_result.document_number = nlp_result_row['nlp_result']['document_number']
            nlp_result.document_date = nlp_result_row['nlp_result']['document_date']
            nlp_result.issuing_authority = nlp_result_row['nlp_result']['issuing_authority']
            nlp_result.cadastral_number = nlp_result_row['nlp_result']['cadastral_number']
            nlp_result.administrative_district = nlp_result_row['nlp_result']['administrative_district']
            nlp_result.district = nlp_result_row['nlp_result']['district']
            nlp_result.address = nlp_result_row['nlp_result']['address']
            nlp_result.object_name = nlp_result_row['nlp_result']['object_name']
            nlp_result.customer = nlp_result_row['nlp_result']['customer']
            nlp_result.builder = nlp_result_row['nlp_result']['builder']
            nlp_result.project_organization = nlp_result_row['nlp_result']['project_organization']
            nlp_result.project_author_manager = nlp_result_row['nlp_result']['project_author_manager']
            # save to db
            nlp_result.save()

        except NlpResult.DoesNotExist:
            # Create new record to DB
            NlpResult.objects.create(
                document_id=nlp_result_row['document_id'],
                document_type=nlp_result_row['document_type'],
                document_number=nlp_result_row['nlp_result']['document_number'],
                document_date=nlp_result_row['nlp_result']['document_date'],
                issuing_authority=nlp_result_row['nlp_result']['issuing_authority'],
                cadastral_number=nlp_result_row['nlp_result']['cadastral_number'],
                administrative_district=nlp_result_row['nlp_result']['administrative_district'],
                district=nlp_result_row['nlp_result']['district'],
                address=nlp_result_row['nlp_result']['address'],
                object_name=nlp_result_row['nlp_result']['object_name'],
                customer=nlp_result_row['nlp_result']['customer'],
                builder=nlp_result_row['nlp_result']['builder'],
                project_organization=nlp_result_row['nlp_result']['project_organization'],
                project_author_manager=nlp_result_row['nlp_result']['project_author_manager'],
            )


def get_document_type_id_by_name(document_type_name: str) -> int:
    try:
        document_type = DocumentType.objects.get(doc_type_name=document_type_name)
        document_type_id = document_type.id
    except DocumentType.DoesNotExist:
        document_type_id = 6

    return document_type_id


def get_files_table() -> list:
    files = File.objects.filter(is_active=True) \
        .values('id', 'original_name', 'category__title', 'user__email', 'is_processed')  # or any kind of queryset

    return list(files)


def get_document_ids_not_synchronized(document_ids_list):
    """Получаем список doc id которые не синхронизировались с таблицей nlp_result"""
    documents = Document.objects.filter().exclude(id__in=document_ids_list).values_list('id', flat=True)
    all_ids = document_ids_list + list(documents)
    return all_ids


def get_list_of_document_ids_by_applied_filter(request) -> list:
    """Получает список doc id по применненым фильтрам"""
    nlp_data = NlpResult.objects.filter().values('id', 'document__file__original_name', 'document_id', 'document_type',
                                                 'document__status__is_detail', 'document__status__color',
                                                 'document__status_id',
                                                 'document_number', 'document_date', 'issuing_authority',
                                                 'cadastral_number',
                                                 'administrative_district', 'district', 'address', 'object_name',
                                                 'customer', 'builder', 'project_organization',
                                                 'project_author_manager')

    # If at least one filter is applied will be True
    is_filter_applied = False

    # Apply filters
    if check_session_key_not_empty(request.session, 'nlp_document_type'):
        nlp_data = nlp_data.filter(document_type=request.session['nlp_document_type'])
        is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_number'):
        nlp_data = nlp_data.filter(document_number=request.session['nlp_number'])
        is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_date'):
        if request.session['nlp_date']:
            print('____________________DATE RANGE________________')
            print(request.session['nlp_date'])
            print(request.session['nlp_date'].split(' - '))
            nlp_data = nlp_data.filter(document_date__range=request.session['nlp_date'].split(' - '))
            is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_authority'):
        nlp_data = nlp_data.filter(issuing_authority=request.session['nlp_authority'])
        is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_customer'):
        nlp_data = nlp_data.filter(customer=request.session['nlp_customer'])
        is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_builder'):
        nlp_data = nlp_data.filter(builder=request.session['nlp_builder'])
        is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_project_organization'):
        nlp_data = nlp_data.filter(project_organization=request.session['nlp_project_organization'])
        is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_project_author_manager'):
        nlp_data = nlp_data.filter(project_author_manager=request.session['nlp_project_author_manager'])
        is_filter_applied = True

    if check_session_key_not_empty(request.session, 'nlp_cadastral_number'):
        nlp_data = nlp_data.filter(cadastral_number=request.session['nlp_cadastral_number'])
        is_filter_applied = True

    document_ids_list = []
    for nlp in nlp_data:
        document_ids_list.append(nlp['document_id'])

    if is_filter_applied is not True:
        doc_ids_list_not_synchronized = get_document_ids_not_synchronized(document_ids_list)
        document_ids_list = doc_ids_list_not_synchronized

    # Create document list ids
    request.session['document_ids_list'] = document_ids_list
    request.session['is_filter_applied'] = is_filter_applied

    return document_ids_list


def get_document_type_id_by_document_id(document_id: int) -> int:
    tesseract_classifier = TesseractClassifier.objects.get(document_id=document_id)
    return tesseract_classifier.document_type.id


def get_attributes_by_document_type_id(document_type_id: int) -> Attribute:
    return Attribute.objects.filter(document_type_id=document_type_id, is_active=True)


def get_status_for_nlp_by_ocr_text(ocr_text: Optional[str]) -> int:
    if ocr_text:
        return 2
    return 0


def get_ocr_or_user_text(ocr_text: Optional[str], user_text: Optional[str], status: int) -> Optional[str]:
    if status > 2:
        return (user_text[:250] + '..') if len(user_text) > 250 else user_text
    return (ocr_text[:250] + '..') if len(ocr_text) > 250 else ocr_text


def get_nlp_tesseract_status_by_attribute_value(attribute_value: Union[str, tuple, None]) -> int:
    default_values = ['Земли не найдены', 'Орган не найден', 'нет']

    if isinstance(attribute_value, str):
        if attribute_value in default_values:
            return 0
        if len(attribute_value) == 0:
            return 0
        return 2
    else:
        return 0


def create_nlp_tesseract_table(document_id: int) -> tuple:
    document_type = TesseractClassifier.objects.get(document_id=document_id)
    document_type_id = document_type.document_type_id

    csv_tmp_folder = os.path.join(settings.STATIC_ROOT, 'csv_tmp')
    if not os.path.exists(csv_tmp_folder):
        os.mkdir(csv_tmp_folder)

    csv_path = os.path.join(csv_tmp_folder, str(document_id) + '.csv')

    ocrs = OcrTesseract.objects.filter(page__document_id=document_id)
    row_list = [
        ['ocr_id', 'text', 'upper_left_y', 'upper_left_x', 'upper_right_y', 'upper_right_x', 'lower_right_y',
         'lower_right_x', 'lower_left_y', 'lower_left_x']]
    for ocr in ocrs:
        row_list.append(
            [ocr.id, get_ocr_or_user_text(ocr.ocr_text, ocr.user_text, ocr.status), ocr.upper_left_y,
             ocr.upper_left_x,
             ocr.upper_right_y, ocr.upper_right_x,
             ocr.lower_right_y, ocr.lower_right_x, ocr.lower_left_y, ocr.lower_left_x])

    with open(csv_path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerows(row_list)
    p = Parser()
    attributes = p.parse([csv_path], document_type_id)
    print(attributes)

    for attribute_name in attributes[0]:

        try:
            print('+++-----------------------')
            print(type(attribute_name))
            print(attribute_name)
            print(attributes[0][attribute_name])
            print('-----------------------+++')

            attribute = Attribute.objects.get(attribute_name__exact=attribute_name, document_type_id=document_type_id)

            if get_nlp_tesseract_status_by_attribute_value(attributes[0][attribute_name]) == 2:
                NlpTesseract.objects.create(
                    attribute_id=attribute.id,
                    document_id=document_id,
                    ocr_text=attributes[0][attribute_name] if isinstance(attributes[0][attribute_name], str) else None,
                    status=2
                )
        except Attribute.DoesNotExist:
            print('Attribute.DoesNotExist:')
            continue
        except Attribute.MultipleObjectsReturned:
            print('Attribute.MultipleObjectsReturned:')
            continue

    # Delete csv
    if os.path.exists(csv_path):
        os.remove(csv_path)
    else:
        print("The file does not exist")

    return attributes


def get_document_dictionary_by_document_id(document_id: int) -> str:
    pages = Page.objects.filter(document_id=document_id)
    dictionary = ''

    for page in pages:
        dictionary += page.dictionary + ' '

    return dictionary


def get_year(string: str) -> Optional[int]:
    year = re.compile(r'[0-9]{4}').findall(string)
    if year:
        year = year[0]
    else:
        year = None

    return year
