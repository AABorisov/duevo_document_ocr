import os
import pathlib
import csv
import datetime
from django.db.models import Q
from django import template
from xml.dom.minidom import parseString
import magic
# from MySQLdb import _mysql
import psycopg2
from dicttoxml import dicttoxml
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render, redirect, get_object_or_404
import mimetypes
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db import connections
from psycopg2.extras import NamedTupleCursor
import json
import requests
from document.forms import *
from document.nlp_module.doc.parser import Parser
from document.ocr_module.main import *
from document.utils import *
from document_processing import constants
from django.http import HttpResponse, JsonResponse, Http404
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.urls import reverse_lazy, reverse, resolve
from document.models import *
from document_processing import settings
from pdf2image import convert_from_path
from django.utils import translation
from django.db.models import Sum

'''
labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
datasets: [
                {
                    label: 'Digital Goods',
                    backgroundColor: 'rgba(60,141,188,0.9)',
                    borderColor: 'rgba(60,141,188,0.8)',
                    pointRadius: false,
                    pointColor: '#3b8bba',
                    pointStrokeColor: 'rgba(60,141,188,1)',
                    pointHighlightFill: '#fff',
                    pointHighlightStroke: 'rgba(60,141,188,1)',
                    data: [28, 48, 40, 19, 86, 27, 90]
                },
                {
                    label: 'Electronics',
                    backgroundColor: 'rgba(210, 214, 222, 1)',
                    borderColor: 'rgba(210, 214, 222, 1)',
                    pointRadius: false,
                    pointColor: 'rgba(210, 214, 222, 1)',
                    pointStrokeColor: '#c1c7d1',
                    pointHighlightFill: '#fff',
                    pointHighlightStroke: 'rgba(220,220,220,1)',
                    data: [65, 59, 80, 81, 56, 55, 40]
                },
            ]
'''


class DashboardView(View):

    @staticmethod
    def get(request):

        # Apply filters
        if not check_session_key_not_empty(request.session, 'nlp_document_type'):
            request.session['nlp_document_type'] = "__all__"

        if not check_session_key_not_empty(request.session, 'nlp_number'):
            request.session['nlp_number'] = "__all__"

        if not check_session_key_not_empty(request.session, 'nlp_date'):
            request.session['nlp_date'] = ""

        if not check_session_key_not_empty(request.session, 'nlp_authority'):
            request.session['nlp_authority'] = "__all__"

        if not check_session_key_not_empty(request.session, 'nlp_customer'):
            request.session['nlp_customer'] = "__all__"

        if not check_session_key_not_empty(request.session, 'nlp_builder'):
            request.session['nlp_builder'] = "__all__"

        if not check_session_key_not_empty(request.session, 'nlp_project_organization'):
            request.session['nlp_project_organization'] = "__all__"

        if not check_session_key_not_empty(request.session, 'nlp_project_author_manager'):
            request.session['nlp_project_author_manager'] = "__all__"

        if not check_session_key_not_empty(request.session, 'nlp_cadastral_number'):
            request.session['nlp_cadastral_number'] = "__all__"

        document_ids_list = get_list_of_document_ids_by_applied_filter(request)

        documents = Document.objects.filter(is_active=True, id__in=document_ids_list)
        labels = get_labels_for_stacked_chart(documents)
        datasets = get_datasets_for_stacked_chart(labels, documents)
        # print(get_nextautoincrement(Page))
        # print(datetime.datetime.now())
        json_datasets = json.dumps(datasets)
        json_labels = json.dumps(labels)

        # Donut chart
        json_donut_labels = get_labels_for_donut_chart()
        json_donut_datasets = get_datasets_for_donut_chart(document_ids_list)

        tree_view = get_tree_view_menu()

        # filters
        # doc_classes = get_doc_class_data()
        nlp_document_types = nlp_distinct_data('document_type')
        nlp_numbers = nlp_distinct_data('document_number')
        # nlp_dates = nlp_distinct_data('document_date')
        nlp_authorities = nlp_distinct_data('issuing_authority')
        nlp_customers = nlp_distinct_data('customer')
        nlp_builders = nlp_distinct_data('builder')
        nlp_project_organizations = nlp_distinct_data('project_organization')
        nlp_project_author_managers = nlp_distinct_data('project_author_manager')
        nlp_cadastral_numbers = nlp_distinct_data('cadastral_number')

        context = {
            # filters
            "nlp_numbers": nlp_numbers,
            "nlp_date": request.session['nlp_date'],
            "nlp_authorities": nlp_authorities,
            "nlp_document_types": nlp_document_types,
            "nlp_customers": nlp_customers,
            "nlp_builders": nlp_builders,
            "nlp_project_organizations": nlp_project_organizations,
            "nlp_project_author_managers": nlp_project_author_managers,
            "nlp_cadastral_numbers": nlp_cadastral_numbers,

            "tree_view": tree_view,
            "json_labels": json_labels,
            "json_datasets": json_datasets,
            "json_donut_labels": json_donut_labels,
            "json_donut_datasets": json_donut_datasets,
            "title": _("Dashboard"),
            "navbar": constants.NAVBAR_DASHBOARD,
        }
        return render(request, 'document/dashboard.html', context=context)

    def post(self, request):

        print(request.POST)
        request.session['nlp_document_type'] = request.POST.get('nlp_document_type')
        request.session['nlp_number'] = request.POST.get('nlp_number')
        request.session['nlp_date'] = request.POST.get('nlp_date')
        request.session['nlp_authority'] = request.POST.get('nlp_authority')

        request.session['nlp_customer'] = request.POST.get('nlp_customer')
        request.session['nlp_builder'] = request.POST.get('nlp_builder')
        request.session['nlp_project_organization'] = request.POST.get('nlp_project_organization')
        request.session['nlp_project_author_manager'] = request.POST.get('nlp_project_author_manager')
        request.session['nlp_cadastral_number'] = request.POST.get('nlp_cadastral_number')

        # Get ids
        document_ids_list = get_list_of_document_ids_by_applied_filter(request)
        documents = Document.objects.filter(is_active=True, id__in=document_ids_list)

        labels = get_labels_for_stacked_chart(documents)
        datasets = get_datasets_for_stacked_chart(labels, documents)
        print(get_nextautoincrement(Page))
        print(datetime.datetime.now())
        json_datasets = json.dumps(datasets)
        json_labels = json.dumps(labels)

        # Donut chart
        json_donut_labels = get_labels_for_donut_chart()
        json_donut_datasets = get_datasets_for_donut_chart(document_ids_list)

        tree_view = get_tree_view_menu()

        # filters
        # doc_classes = get_doc_class_data()
        nlp_document_types = nlp_distinct_data('document_type')
        nlp_numbers = nlp_distinct_data('document_number')
        # nlp_dates = nlp_distinct_data('document_date')
        nlp_authorities = nlp_distinct_data('issuing_authority')
        nlp_customers = nlp_distinct_data('customer')
        nlp_builders = nlp_distinct_data('builder')
        nlp_project_organizations = nlp_distinct_data('project_organization')
        nlp_project_author_managers = nlp_distinct_data('project_author_manager')
        nlp_cadastral_numbers = nlp_distinct_data('cadastral_number')

        context = {

            "nlp_customers": nlp_customers,
            "nlp_builders": nlp_builders,
            "nlp_project_organizations": nlp_project_organizations,
            "nlp_project_author_managers": nlp_project_author_managers,
            "nlp_cadastral_numbers": nlp_cadastral_numbers,

            "tree_view": tree_view,
            "nlp_numbers": nlp_numbers,
            "nlp_date": request.session['nlp_date'],
            "nlp_authorities": nlp_authorities,
            "nlp_document_types": nlp_document_types,
            "json_labels": json_labels,
            "json_datasets": json_datasets,
            "json_donut_labels": json_donut_labels,
            "json_donut_datasets": json_donut_datasets,
            "title": _("Dashboard"),
            "navbar": constants.NAVBAR_DASHBOARD,
        }
        return render(request, 'document/dashboard.html', context=context)


@login_required
def stacked_chart_json(request):
    document_ids = request.session['document_ids_list']
    documents = Document.objects.filter(is_active=True, id__in=document_ids)
    print('++++++++++++++')
    print(document_ids)
    print('++++++++++++++')

    labels = get_labels_for_stacked_chart(documents)
    datasets = get_datasets_for_stacked_chart(labels, documents)

    json_datasets = json.dumps(datasets)
    json_labels = json.dumps(labels)
    data = {
        "labels": json_labels,
        "datasets": json_datasets,
    }
    return JsonResponse(data)


@login_required
def donut_chart_json(request):
    json_datasets = get_datasets_for_donut_chart(request.session['document_ids_list'])
    json_labels = get_labels_for_donut_chart()
    data = {
        "labels": json_labels,
        "datasets": json_datasets,
    }
    return JsonResponse(data)


class FileUploadView(View):

    @staticmethod
    def get(request):
        categories = Category.objects.filter(is_active=True)
        context = {
            "categories": categories,
            "title": _("Document upload"),
            "navbar": constants.NAVBAR_DOCUMENT_UPLOAD,
        }
        return render(request, 'document/document_upload.html', context=context)

    @staticmethod
    def post(request):
        print(request.POST.get('category'))
        print(request.FILES.getlist('files'))

        # Get file path
        today_path = get_year_month_day_path()

        # Creates 'documents' dir
        files_path = os.path.join(settings.MEDIA_ROOT, 'files', today_path)
        if not os.path.exists(files_path):
            pathlib.Path(files_path).mkdir(parents=True, exist_ok=True)

        fs = FileSystemStorage()

        category_id = request.POST.get('category')
        description = request.POST.get('description')
        duplicate_files = []

        for file in request.FILES.getlist('files'):
            mime = magic.Magic(mime=True)
            mime_type = mime.from_buffer(file.read())
            extension = mime_type.split('/').pop()
            print(extension)
            print(mime_type)
            original_name = file.name
            file_id = get_nextautoincrement(File)
            file_path = fs.save('files/' + today_path + '/' + str(file_id) + '.' + extension, file)
            print(file_path)
            print('ORIGINAL_NAME: ' + original_name)
            # Upload photo to Processing server

            # Check in database if filename exists
            filename_exist = is_file_exists(original_name)

            if filename_exist is False:

                File.objects.create(
                    user_id=request.user.id,
                    category_id=category_id,
                    original_name=original_name,
                    description=description,
                    file_path=file_path,
                    mime_type=mime_type,
                )
            else:
                duplicate_files.append(original_name)

        print(duplicate_files)
        print(len(duplicate_files))

        if len(duplicate_files) != 0:
            for duplicate_file in duplicate_files:
                message_text = _(f'This file "{duplicate_file}" duplicated!')
                messages.warning(request, message_text)

        message_text = _('Files uploaded successfully!')
        messages.success(request, message_text)

        return redirect('dashboard_url')


@login_required
def ajax_file_table_json(request):
    if request.session['is_filter_applied']:
        files = File.objects.filter(is_active=True, document__in=request.session['document_ids_list'])
    else:
        files = File.objects.filter(is_active=True)

    files = files.values('id', 'original_name', 'category__title', 'user__email', 'is_processed',
                         'created_at')  # or any kind of queryset

    json_data = list(files)
    return JsonResponse(json_data, safe=False)


@login_required
def document_json_data(request):
    documents = Document.objects.filter(is_active=True, id__in=request.session['document_ids_list']).values('id',
                                                                                                            'file__original_name',
                                                                                                            'tesseractclassifier__document_type__doc_type_name',
                                                                                                            'file__user__email',
                                                                                                            'created_at',
                                                                                                            'status__id',
                                                                                                            'status__title',
                                                                                                            'status__color',
                                                                                                            'status__is_detail')  # or any kind of queryset
    json_data = list(documents)
    return JsonResponse(json_data, safe=False)


@login_required
def nlp_json_data(request):
    document_ids_list = get_list_of_document_ids_by_applied_filter(request)
    nlp_data = NlpResult.objects.filter(document__in=document_ids_list).values('id', 'document__file__original_name',
                                                                               'document_id', 'document_type',
                                                                               'document__status__is_detail',
                                                                               'document__status__color',
                                                                               'document__status_id',
                                                                               'document_number', 'document_date',
                                                                               'issuing_authority', 'cadastral_number',
                                                                               'administrative_district', 'district',
                                                                               'address', 'object_name',
                                                                               'customer', 'builder',
                                                                               'project_organization',
                                                                               'project_author_manager')

    json_data = list(nlp_data)
    return JsonResponse(json_data, safe=False)


@login_required
def file_download(request, file_id):
    try:
        file = File.objects.get(id=file_id)
        file_path = file.file_path.path
        print(file_path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type=file.mime_type)
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
    except File.DoesNotExist:
        print('File.DoesNotExist:')
    raise Http404


class DetailDocumentView(View):

    @staticmethod
    def get(request, document_id, page_id):
        document = Document.objects.get(id=document_id)
        pages = Page.objects.filter(document=document, is_active=True)

        request.session['tree_page_id'] = page_id
        request.session['tree_doc_id'] = document.id
        request.session['tree_class_id'] = get_doc_class_id(document.id)

        # Create json from Adygzhy table
        json_pages = create_pages_json(pages)

        # Create json from OCR TESSERACT
        json_pages_tesseract = create_pages_json_tesseract(pages)
        # nlp_data = create_json_nlp(document_id)
        nlp_data = create_json_nlp_table(document_id, page_id)

        # Nlp tesseract
        nlp_tesseract_data = create_json_nlp_tesseract_table(document_id, page_id)
        # print(type(nlp_data['nlp_dict']))
        doc_class_data = get_doc_class_data()
        available_attributes_data = get_available_attributes(document_id)
        # print(nlp_data['nlp_dict'])
        tree_view = get_tree_view_menu()

        context = {
            "document": document,
            "nlp_json": nlp_data['nlp_json'],
            "nlp_dict": nlp_data['nlp_dict'],
            # Nlp tesseract
            "tree_view": tree_view,
            "nlp_tesseract_json": nlp_tesseract_data['nlp_tesseract_json'],
            "nlp_tesseract_dict": nlp_tesseract_data['nlp_tesseract_dict'],
            "available_attributes_json": available_attributes_data['available_attributes_json'].decode(),
            "available_attributes_dict": available_attributes_data['available_attributes_dict'],
            "doc_class_json": doc_class_data['doc_class_json'],
            "doc_class_dict": doc_class_data['doc_class_dict'],
            "json_pages": json_pages,
            "json_pages_tesseract": json_pages_tesseract,
            "pages": pages,
            "title": _("Document detail"),
            "navbar": constants.NAVBAR_DOCUMENT_DETAIL,
        }

        return render(request, 'document/document_detail.html', context=context)

    @staticmethod
    def post(request):
        pass


@login_required
def google_nlp_recalculate(request, document_id):
    # delete Nlp and ocr
    Nlp.objects.filter(document_id=document_id).delete()
    Ocr.objects.filter(document_id=document_id).delete()
    Classification.objects.filter(document_id=document_id).delete()
    NlpResult.objects.filter(document_id=document_id).delete()

    Page.objects.filter(document_id=document_id).update(is_sent_to_server=False)

    document = Document.objects.get(id=document_id)
    document.is_processed = False
    document.status_id = 9
    document.save()

    return redirect('dashboard_url')


@login_required
def tesseract_nlp_recalculate(request, document_id):
    # delete Nlp and ocr
    NlpTesseract.objects.filter(document_id=document_id).delete()

    # Get doc type id
    document_type_id = get_document_type_id_by_document_id(document_id)

    # If document type BTI use my parser
    if document_type_id == 1:

        pages = Page.objects.filter(document_id=document_id)
        dictionary = ''

        for page in pages:
            q0 = OcrTesseract.objects.filter(page_id=page.id)

            # Теперь когда есть информация о положении слов на картинке а именно их абсцисса и ординада, можно их упорядочить по строкам и внутри строк
            te = {}
            no_list = ['*', '-', '-1', '—', '|', '/', '\\', '.',
                       ',']  # Если строка состоит лишь из этих символов(обычно это рудименты меток и графических элементов)
            picture_rudiments = ['‘', '"']

            thrs = get_threshold_recalculate(q0)
            print(thrs)

            cnt = 0
            ocr_words = []
            te = defaultdict(list)
            levels = []
            for i in q0:
                cnt += 1
                text = i.user_text if i.user_text else i.ocr_text
                text = re.sub(r'[^\w\№\.\;\(\)\-\:]', '', text)
                # ордината Y
                y = i.upper_left_y
                # абсцисса X
                x = i.upper_left_x

                for j in picture_rudiments:
                    text = text.replace(j, '')

                new = True
                for level in levels:
                    if abs(y - level) < thrs:
                        te[level].append([x, text])
                        new = False
                        break
                if new:
                    te[y].append([x, text])
                    levels.append(y)

            ll = sorted(te)  # Упорядочим по ординате

            ld = [te[i] for i in sorted(te)]
            LL = []
            for i in ll:
                if ll.index(i) == 0:
                    LL = LL + [i]
                    continue
                else:
                    # также ввиду неточности анализа некоторые фрагменты одной строки могут иметь немного отличающиеся ординаты(введем допуск)
                    if i in range(LL[-1], LL[-1] + 6 + 1):
                        LL = LL + [LL[-1]]
                    else:
                        LL = LL + [i]
            # сформируем окончательный словарь и упорядочим слова(фрагменты) внутри строки
            fdin = {}

            for i in range(len(LL)):
                if LL[i] in fdin:
                    fdin[LL[i]] = fdin[LL[i]] + ld[i]
                else:
                    fdin[LL[i]] = ld[i]

            finlist = [' '.join([j[1] for j in sorted(fdin[i])]) for i in sorted(fdin)]
            finlist = [i for i in finlist if '@' not in i]

            # Create word dictionary
            qq = ' '.join(finlist).replace('95', '').lower()
            # print(qq)
            dictionary = qq

            dictionary += dictionary + ' '
            page.dictionary = qq
            page.save()

        add_dict = {}
        dictionary = get_document_dictionary_by_document_id(document_id)
        add_dict = parsing_of_bti(dictionary, document_id)

        print('-------------TEXT-----------')
        print(dictionary)

    else:
        answer = create_nlp_tesseract_table(document_id)
        print(answer)

    # Redirect back to document detail
    return redirect(reverse('document_detail_url', kwargs={"document_id": document_id, "page_id": 0}))


class PageDetailView(View):

    @staticmethod
    def get(request, page_id):
        tree_view = get_tree_view_menu()

        page = Page.objects.get(id=page_id)

        request.session['tree_page_id'] = page_id
        request.session['tree_doc_id'] = page.document.id
        request.session['tree_class_id'] = get_doc_class_id(page.document.id)
        context = {
            "tree_view": tree_view,
            "page": page,
            "title": _("Document detail"),
            "navbar": constants.NAVBAR_PAGE_DETAIL,
        }

        return render(request, 'document/page_detail.html', context=context)

    @staticmethod
    def post(request):
        pass


def generate_csv_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="csv_report.csv"'

    nlp_data = SvidAgrDocuments.objects.filter().using('ocr')
    print('NLP')
    print(nlp_data)
    writer = csv.writer(response, delimiter=';')
    writer.writerow(
        ['Название документа', 'Тип документа', 'Номер', 'Дата', 'Выдавший орган', 'Административный округ', 'Район',
         'Адрес', 'Наименование объекта', 'Функциональное назначение объекта', 'Заказчик', 'Застройщик',
         'Проектная организация', 'Руководитель авторов проекта'])
    for nlp in nlp_data:

        try:
            print(nlp.doc_id)
            document = Document.objects.get(id=nlp.doc_id)
            writer.writerow(
                [document.original_name, nlp.class_field.class_name, nlp.number, nlp.date, nlp.issuing_authority,
                 nlp.administrative_district,
                 nlp.district, nlp.address, nlp.object_name, nlp.functional_purpose_of_object, nlp.customer,
                 nlp.builder,
                 nlp.project_organization, nlp.project_author_manager])
        except Document.DoesNotExist:
            print('Document.DoesNotExist')
            continue

    return response


def generate_xml_view(request):
    nlp_data = SvidAgrDocuments.objects.filter().using('ocr')

    nlp_element = []

    for nlp in nlp_data:
        try:
            document = Document.objects.get(id=nlp.doc_id)
            doc_name = document.original_name
            nlp_element.append({
                "doc_name": doc_name,
                "type_name": nlp.class_field.class_name,
                "date": nlp.date,
                "issuing_authority": nlp.issuing_authority,
                "administrative_district": nlp.administrative_district,
                "district": nlp.district,
                "address": nlp.address,
                "object_name": nlp.object_name,
                "functional_purpose_of_object": nlp.functional_purpose_of_object,
                "builder": nlp.builder,
                "project_organization": nlp.project_organization,
                "project_author_manager": nlp.project_author_manager,

            })
        except Document.DoesNotExist:
            print('Document.DoesNotExist' + str(nlp.doc_id))
            continue

    xml = dicttoxml(nlp_element)
    xml = xml.decode()
    dom = parseString(xml)
    response = HttpResponse(dom.toprettyxml(), content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename="xml_report.xml"'
    return response


@csrf_exempt
def ajax_edit_ocr_table(request):
    if request.method == 'POST':
        ocr_id = request.POST.get('id')
        user_text = request.POST.get('user_text')

        try:
            ocr = Ocr.objects.get(id=ocr_id)
            if ocr.status != 4:
                ocr.status = 3
            ocr.user_text = user_text
            ocr.save()
            print('NEXT ID WAS EDITED')
            print(ocr.id)
            return JsonResponse({"success": "Updated successfully"})
        except Ocr.DoesNotExist:
            return JsonResponse({"error": "No record in DB"})

    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
def ajax_edit_ocr_tesseract_table(request):
    if request.method == 'POST':
        ocr_id = request.POST.get('id')
        user_text = request.POST.get('user_text')

        try:
            ocr = OcrTesseract.objects.get(id=ocr_id)
            if ocr.status != 4:
                ocr.status = 3
            ocr.user_text = user_text
            ocr.save()
            print('NEXT ID WAS EDITED')
            print(ocr.id)
            return JsonResponse({"success": "Updated successfully"})
        except OcrTesseract.DoesNotExist:
            return JsonResponse({"error": "No record in DB"})

    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
def ajax_edit_nlp_table(request):
    if request.method == 'POST':
        ocr_id = request.POST.get('id')
    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
def ajax_global_search(request):
    if 'term' in request.GET:
        ocr_word = request.GET.get('term')
        ocr_data = Ocr.objects.filter(
            Q(ocr_text__icontains=ocr_word.lower()) | Q(user_text__icontains=ocr_word.lower())) \
            .values('page_id', 'document_id', 'ocr_text', 'user_text', 'status').distinct()
        json_data = []

        # try:
        #     nlp_result = NlpResult.objects.filter(
        #         Q(document_number__icontains=ocr_word.lower()) | Q(issuing_authority__icontains=ocr_word.lower())\
        #         | Q(issuing_authority__icontains=ocr_word.lower()))
        #
        # except NlpResult.DoesNotExist:
        #     print('NlpResult.DoesNotExist')

        for ocr in ocr_data:
            try:
                page = Page.objects.get(id=ocr['page_id'])

                ocr_text = ocr['ocr_text']
                ocr_status = ocr['status']
                user_text = ocr['user_text']

                json_data.append({
                    'value': reverse('document_detail_url', args=[page.document_id, page.id]),
                    # 'label': f'{_("Word")}: {str(ocr.ocr_text)}; {_("Document name")}: {str(page.document.original_name)}; {_("Page number")}: {str(page.page_number)}'
                    'label': f'{_("Word")}: {ocr_text if ocr_status == 2 else user_text}; {_("Doc ID")}: {page.document_id}; {_("Document name")}: {page.document.file.original_name}; {_("Page number")}: {page.page_number}',
                    'ocr_text': f'{ocr_text if ocr_status == 2 else user_text}'
                })
            except Page.DoesNotExist:
                print('Page.DoesNotExist; Word: ' + str(ocr_word))
                continue

        # json_data = list(ocr_data)
        print(json_data)
        return JsonResponse(json_data, safe=False)

    return JsonResponse({"error": "Only GET method is allowed"})


@csrf_exempt
@login_required
def ajax_add_new_ocr_record(request):
    """Получаем с фронта координаты и данные по новой OCR записи"""

    if request.method == 'POST':
        page_id = request.POST.get('page_id')
        document_id = request.POST.get('doc_id')
        x0 = request.POST.get('x0')
        y0 = request.POST.get('y0')
        x1 = request.POST.get('x1')
        y1 = request.POST.get('y1')
        user_text = request.POST.get('user_text')

        new_ocr = add_new_ocr_record(x0, y0, x1, y1, user_text, page_id, document_id)

        return JsonResponse({
            "ocr_id": new_ocr.id,
            "status": new_ocr.status
        })

    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
@login_required
def ajax_add_nlp_record(request):
    """Добавляем новую запись nlp"""
    if request.method == 'POST':
        nlp_id = request.POST.get('nlp_id')
        document_id = request.POST.get('doc_id')
        attribute_id = request.POST.get('attribute_id')
        ocr_word_ids = request.POST.getlist('ocr_word_ids[]')
        # Convert str list to int
        ocr_word_ids = list(map(int, ocr_word_ids))

        # Add nlp record
        added_nlp = add_nlp_record(document_id, attribute_id, ocr_word_ids)

        if added_nlp:
            return JsonResponse({
                "nlp_id": added_nlp.id,
                "doc_id": added_nlp.document.id,
                "attribute_category_id": added_nlp.attribute.attribute_category.id if added_nlp.attribute.attribute_category else None,
                "attribute_category_name": added_nlp.attribute.attribute_category.category_name if added_nlp.attribute.attribute_category else None,
                "attribute_id": added_nlp.attribute.id,
                "attribute_name": added_nlp.attribute.attribute_name,
                "status": added_nlp.status,
                "ocr_word_ids": added_nlp.ocr_word_ids,
                "ocr_text": added_nlp.ocr_text
            })
        return JsonResponse({"error": "Can not add nlp record"})
    return JsonResponse({"error": "Only POST method is allowed"})


# Tesseract layout section
@csrf_exempt
@login_required
def ajax_add_new_ocr_tesseract_record(request):
    """Получаем с фронта координаты и данные по новой OCR записи"""

    if request.method == 'POST':
        page_id = request.POST.get('page_id')
        document_id = request.POST.get('doc_id')
        x0 = request.POST.get('x0')
        y0 = request.POST.get('y0')
        x1 = request.POST.get('x1')
        y1 = request.POST.get('y1')

        upper_left_y = y0  # y0
        upper_left_x = x0  # x0
        lower_right_y = y1  # y1
        lower_right_x = x1  # x1

        upper_right_y = upper_left_y
        upper_right_x = lower_right_x

        lower_left_y = lower_right_y
        lower_left_x = upper_left_x

        user_text = request.POST.get('user_text')

        new_ocr = add_new_ocr_tesseract_record(upper_left_y, upper_left_x, lower_right_y, lower_right_x, upper_right_y, upper_right_x, lower_left_y, lower_left_x, user_text, page_id)

        return JsonResponse({
            "ocr_id": new_ocr.id,
            "status": new_ocr.status
        })

    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
@login_required
def ajax_edit_nlp_record(request):
    if request.method == 'POST':
        nlp_id = request.POST.get('nlp_id')
        ocr_text = request.POST.get('ocr_text')
        document_id = request.POST.get('doc_id')
        ocr_word_ids = request.POST.getlist('ocr_word_ids[]')
        # convert str list to int
        ocr_word_ids = list(map(int, ocr_word_ids))

        # edit nlp record
        edited_nlp = edit_nlp_record(nlp_id, ocr_word_ids, ocr_text)

        if edited_nlp:
            return JsonResponse({"success": f"NLP record with ID {edited_nlp.id} was updated"})
        return JsonResponse({"error": f"NLP record with ID {edited_nlp.id} not exists"})
    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
@login_required
def ajax_edit_nlp_tesseract_record(request):
    if request.method == 'POST':
        nlp_id = request.POST.get('nlp_id')
        ocr_text = request.POST.get('ocr_text')
        document_id = request.POST.get('doc_id')
        ocr_word_ids = request.POST.getlist('ocr_word_ids[]')
        # convert str list to int
        ocr_word_ids = list(map(int, ocr_word_ids))

        # edit nlp record
        edited_nlp = edit_nlp_tesseract_record(nlp_id, ocr_word_ids, ocr_text)

        if edited_nlp:
            return JsonResponse({"success": f"NLP record with ID {edited_nlp.id} was updated"})
        return JsonResponse({"error": f"NLP record with ID {edited_nlp.id} not exists"})
    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
@login_required
def ajax_remove_ocr_table(request):
    if request.method == 'POST':
        ocr_id = request.POST.get('ocr_id')
        response = remove_ocr_record(Ocr, ocr_id)
        return JsonResponse(response)
    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
@login_required
def ajax_remove_ocr_tesseract_table(request):
    if request.method == 'POST':
        ocr_id = request.POST.get('ocr_id')
        response = remove_ocr_record(OcrTesseract, ocr_id)
        return JsonResponse(response)
    return JsonResponse({"error": "Only POST method is allowed"})


@csrf_exempt
@login_required
def ajax_add_nlp_tesseract_record(request):
    """Добавляем новую запись nlp"""
    if request.method == 'POST':
        nlp_id = request.POST.get('nlp_id')
        document_id = request.POST.get('doc_id')
        attribute_id = request.POST.get('attribute_id')
        ocr_word_ids = request.POST.getlist('ocr_word_ids[]')
        # Convert str list to int
        ocr_word_ids = list(map(int, ocr_word_ids))

        # Add nlp record
        added_nlp = add_nlp_tesseract_record(document_id, attribute_id, ocr_word_ids)

        if added_nlp:
            return JsonResponse({
                "nlp_id": added_nlp.id,
                "doc_id": added_nlp.document.id,
                "attribute_category_id": added_nlp.attribute.attribute_category.id if added_nlp.attribute.attribute_category else None,
                "attribute_category_name": added_nlp.attribute.attribute_category.category_name if added_nlp.attribute.attribute_category else None,
                "attribute_id": added_nlp.attribute.id,
                "attribute_name": added_nlp.attribute.attribute_name,
                "status": added_nlp.status,
                "ocr_word_ids": added_nlp.ocr_word_ids,
                "ocr_text": added_nlp.ocr_text
            })
        return JsonResponse({"error": "Can not add nlp record"})
    return JsonResponse({"error": "Only POST method is allowed"})


@login_required
def convert_nlp_table_to_nlp_result(request):
    """Конвертируем nlp таблицу в nlp_result"""
    nlp_result_rows = generate_fields_for_ocr_result()
    print(nlp_result_rows)
    # Synchronize with nlp_result table
    synchronize_nlp_to_nlp_result(nlp_result_rows)

    js = json.dumps(nlp_result_rows)
    print(js)
    return redirect('dashboard_url')


@csrf_exempt
@login_required
def ajax_convert_nlp_table_to_nlp_result(request):
    """Конвертируем nlp таблицу в nlp_result"""
    nlp_result_rows = generate_fields_for_ocr_result()
    # print(nlp_result_rows)
    # Synchronize with nlp_result table
    synchronize_nlp_to_nlp_result(nlp_result_rows)

    js = json.dumps(nlp_result_rows)
    return JsonResponse({"Success": "Nlp was synchronized successfully"})
