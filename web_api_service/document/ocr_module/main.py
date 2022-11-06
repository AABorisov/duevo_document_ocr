import json

from .src import *


# Свид__АГР
from ..models import NlpTesseract
from ..utils import document_to_images_converter, add_record_tesseract_classifier, file_to_images_converter, \
    get_status_for_nlp_by_ocr_text, get_year


def parsing_of_svid_agr(t: str, document_id: int) -> dict:
    # t = ' '.join(list_)
    print(t)
    document_date = re.compile(r'([0-9]{2}[.][0-9]{2}[.][0-9]{2})|([0-9]{2}\s{1,2}[а-я]{2,8}\s{1,2}[0-9]{2,4})').findall(t)
    if document_date:
        print("++++++++++++++++")
        print(document_date)
        document_date = document_date[0]

    else:
        document_date = None

    p1 = re.compile(r'[Кк]од строительного объекта?:?[ ]?[0-9-/А-ЯA-Z]+[ ]').findall(t)
    if p1:
        p1 = p1[0]
    else:
        p1 = None
    # 53 ([рР]егистрационный №?:?[ ]?[0-9-/А-ЯA-Z]+[ ])|([0-9]{4}[\/[0-9\-]{3,5})
    p2 = re.compile(r'([0-9]{2,3}[-][0-9][\/][0-9][\-][0-9]{1,2})|([0-9]{4}[\/][0-9][\-][0-9]{2})|([0-9]{1,3}[\-][0-9][\-][0-9]{1,3})|([0-9]{2}[\-][0-9]{2}[\-][0-9]{2}[\/][мМ])').findall(t)

    if p2:
        p2 = p2[0]
        print('___________________')
        print(p2)
        print('___________________')
    else:
        p2 = None
    p3 = re.compile(r'[рР]айон:?[ ]?\w+[ ]').findall(t)
    if p3:
        p3 = p3[0]
    else:
        p3 = None
    # p4 = re.compile(r'[рР]айон:?[ ]?\w+[ ]').findall(t)
    # Номер
    NlpTesseract.objects.create(
        attribute_id=53,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(p2),
        ocr_text=p2
    )

    # Дата
    NlpTesseract.objects.create(
        attribute_id=54,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(document_date),
        ocr_text=document_date
    )

    # Район
    NlpTesseract.objects.create(
        attribute_id=57,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(p3),
        ocr_text=p3
    )

    return {'object_code': p1, 'reg_number': p2, 'district': p3}


# Разр__на_ввод
# Разр__на_ввод1pictures
def parsing_of_razr_on_vv(t: str, document_id: int):
    # t = ' '.join(list_)
    # print(t)
    p1 = re.compile(r'[Кк]ому:?[^0-9]+[\'\"][0-9-/А-ЯA-Zа-яa-z_ ]+[\'\"]').findall(t)
    if p1:
        p1 = p1[0]
    else:
        p1 = None
    # разрешение на ввод объекта в эксплуатацию
    p2 = re.compile(r'эксплуатаци[юя]:?[ ]?№[ ]?\w[0-9-]+|объект[ауе]?:?[ ]?№[ ]?\w+').findall(t)
    if p2:
        p2 = p2[0]
    else:
        p2 = None
    # p4 = re.compile(r'[рР]айон:?[ ]?\w+[ ]').findall(t)
    return {'to_whom': p1, 'expluatation': p2}


def get_month_from_list(month_list: list) -> str:
    print(type(month_list[0]))
    months = month_list[0]
    for month in months:
        print('month ', month)
        if month:

            return month
    return ''


# БТИ
# БТИ26__ул_Шеногина__дом_3__строение_45_измpictures
def parsing_of_bti(t: str, document_id: int) -> dict:
    """
    [0-9]{1,2}([\ \'\.а-я]|[0-9]{2})+[0-9]{2,4} # ' 28 '.22. 2009 на января г
    """
    # 3
    # document_month = re.compile(r'(декабр[ья])|(январ[ья])|(феврал[ья])|(март[ао]{0,2})|(апрел[ья])|(ма[йя])|(июн[ья]])|(июл[ья])|(август[а]{0,1})|(сентябр[ья])|(октябр[ья])|(ноябр[ья])').findall(t)
    # document_date = re.compile(r'[0-9]{1,2}[\ \'\.]{0,3}[0-9]{4}').findall(t)

    document_date = re.compile(r'[\d]{1,2}[а-я\ \'\.]+[0-9]{4}').findall(t)
    if document_date:
        print("++++++++++++++++")
        print(document_date)
        document_date = document_date[0]

    else:
        document_date = None

    # 4
    issuing_authority = re.compile(r'фгу\w{0,3}\s{0,3}ростехинвентаризац\w{0,3}\s{0,3}московск\w{0,3}\s{0,3}федеральн\w{0,3}\s{0,3}бти|фгу\w{0,2}\s{0,2}ростехинвентаризац\w{0,3}\s{0,2}федеральн\w{0,3}\s{0,2}бти').findall(t)
    if issuing_authority:
        print("++++++++++++++++")
        print(issuing_authority)
        issuing_authority = issuing_authority[0]
        issuing_authority = 'ФГУП "РОСТЕХИНВЕНТАРИЗАЦИЯ-ФЕДЕРАЛЬНОЕ БТИ"'
    else:
        issuing_authority = None
    """
    77-09-05-008075
    77:03:0004004:5715
    50:27:0030312:311
    77:01:0001093:15
    ([0-9]{0,2}[\-\:][0-9]{0,2}[\-\:][0-9]{0,2}[\-\:][0-9]{0,8})
    ([0-9]{0,2}[\-\:][0-9]{0,2}[\-\:][0-9]{0,8}[\:\-][0-9]{0,6})
    ([0-9]{0,2}[\-\:][0-9]{0,2}[\-\:][0-9]{0,8}[\:\-][0-9]{0,6})
    [0-9\:\-]{0,25}
    """
    # 12
    cadastral_number = re.compile(r'[0-9\:\-]{10,25}').findall(t)
    if cadastral_number:
        print("++++++++++++++++")
        print(cadastral_number)
        cadastral_number = cadastral_number[0]

    else:
        cadastral_number = None

    # 7
    object_name = re.compile(r'\w{0,3}оизводствен\w{0,3}\s{0,3}[а-яА-Я0-9\.\ \,]+оснаст\w{0,3}[а-яА-Я0-9\.\ \,]+инструме\w{0,4}').findall(t)
    object_name_1 = re.compile(r'тепли\w{0,2}\s{0,2}н[а-я0-9 \. \ ]{0,20}с\s{0,2}сетя\w{0,2}').findall(t)
    object_name_2 = re.compile(r'корпу\w{0,2}\s{0,2}лаборатор\w{0,2}\s{0,2}силов\w{0,2}\s{0,2}установ[а-я0-9\ ]{0,7}высотн\w{0,2}\s{0,2}лаборатор\w{0,2}').findall(t)
    object_name_3 = re.compile(r'компре\w{0,2}орн\w{0,2}\s{0,2}станц\w{0,2}\s{0,2}с\s{0,2}сетя\w{0,2}').findall(t)
    object_name_4 = re.compile(r'корп\w{0,3}\s{0,2}ремонтн[а-я\-\ ]{0,5}еханическо\w{0,3}\s{0,2}цех\w{0,3}\s{0,2}н\w{0,3}\s{0,2}[а-я0-9\-\ \,]{0,4}').findall(t)
    if object_name:
        object_name = 'Производственный корпус оснастки и инструмента'
    elif object_name_1:
        object_name = 'Теплицы нр. 1,2,3 с сетями'
    elif object_name_2:
        object_name = 'Корпус лабораторий силовых установок и высотная лаборатория'
    elif object_name_3:
        object_name = 'Компрессорная станция с сетями'
    elif object_name_4:
        object_name = 'Корпус ремонтно-механического цеха нр 4,13'
    else:
        object_name = None

    p1 = re.compile(r'[Кк]варт[.]?[ ]?№[ ]?\d+').findall(t)
    if p1:
        p1 = p1[0]
    else:
        p1 = None
    # разрешение на ввод объекта в эксплуатацию
    p2 = re.compile(r'[Оо]бъем[ ]?[0-9.,]+').findall(t)
    if p2:
        p2 = p2[0]
    else:
        p2 = None
    p3 = re.compile(r'[Вв]ладелец[ ]?\w+[\"А-Яа-я ]+').findall(t)
    if p3:
        p3 = p3[0]
    else:
        p3 = None

    # 19 Состав объекта / площадь
    area = re.compile(r'[0-9]+[.[0-9]+]?\s{0,3}кв.м.').findall(t)
    if area:
        area = area[0]
    else:
        area = None

    # 10 Год постройки
    year_build = re.compile(r'го\w{0,2}\sпострой[а-я0-9\ ]+[0-9]{4}').findall(t)
    if year_build:
        year_build = get_year(year_build[0])
    else:
        year_build = None

    # 11 Год ввода в эксплуатацию
    year_exploitation = re.compile(r'го\w{0,2}\s{0,2}вво[а-я0-9\ ]+ксплуатацию[а-я0-9\ \(\)]+[0-9]{4}').findall(t)
    if year_exploitation:
        year_exploitation = get_year(year_exploitation[0])
    else:
        year_exploitation = None


    # Дата
    NlpTesseract.objects.create(
        attribute_id=3,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(document_date),
        ocr_text=document_date
    )

    # Выдавший орган
    NlpTesseract.objects.create(
        attribute_id=4,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(issuing_authority),
        ocr_text=issuing_authority
    )
    # Наименование объекта
    NlpTesseract.objects.create(
        attribute_id=7,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(object_name),
        ocr_text=object_name
    )
    # Кадастровый номер ЗУ
    NlpTesseract.objects.create(
        attribute_id=12,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(cadastral_number),
        ocr_text=cadastral_number
    )
    # Наименование владельцев
    NlpTesseract.objects.create(
        attribute_id=16,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(p3),
        ocr_text=p3
    )

    # 19 Состав объекта / площадь
    NlpTesseract.objects.create(
        attribute_id=19,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(area),
        ocr_text=area
    )

    # 10 Год постройки
    NlpTesseract.objects.create(
        attribute_id=10,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(year_build),
        ocr_text=year_build
    )

    # 11 Год ввода в эксплуатацию
    NlpTesseract.objects.create(
        attribute_id=11,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(year_exploitation),
        ocr_text=year_exploitation
    )

    return {'quart': p1, 'square': area, 'owner': p3}


# Разр__на_стр
def parsing_of_build_permission(t: str, document_id: int) -> dict:
    # t = ' '.join(list_)
    # print(t)
    deal_number = re.compile(r'[Дд]ело[ ]*№[ ]*[0-9]*').findall(t)
    if deal_number:
        deal_number = deal_number[0]
    else:
        deal_number = None
    doc_number = re.compile(r'[a-zA-Zа-яА-Я][0-9]+-[0-9]+').findall(t)
    if doc_number:
        doc_number = doc_number[0]
    else:
        doc_number = None
    client = re.compile(r'[Кк]ому: \S+[ ]\S+[ ]').findall(t)
    if client:
        client = client[0]
    else:
        client = None
    issuing_authority = re.compile(r'ПРАВИТЕЛЬСТВО [А-Я]+[ ][А-Я]+[ ][А-Я]+[ ][А-Я]+[ ][А-Я]+').findall(t)
    if issuing_authority:
        issuing_authority = issuing_authority[0]
    else:
        issuing_authority = None
    date = re.compile(r'«[0-9]+»[ ]*[а-яА-Я]+[ ]*[0-9]{4}').findall(t)
    if date:
        date = date[0]
    else:
        date = None

    return {'deal_number': deal_number,
            'doc_number': doc_number,
            'client': client,
            'issuing_authority': issuing_authority,
            'date': date}


# ЗУ
def parsing_of_rent_contract(t: str, document_id: int) -> dict:
    # t = ' '.join(list_)
    # print(t)
    scale = re.compile(r'Масштаб [0-9][ ]*:[ ]*[0-9]*').findall(t)
    if scale:
        scale = scale[0]
    else:
        scale = None
    cadastr = re.compile(r'[0-9]{2}[ ]*:[ ]*[0-9]{2}[ ]*:[0-9]+[ ]*:[ ]*[0-9]+').findall(t)
    if cadastr:
        cadastr = cadastr[0]
    else:
        cadastr = None
    # 26
    doc_number = re.compile(r'№ [a-zA-Zа-яА-Я]-[0-9]{2}-[0-9]+').findall(t)
    if doc_number:
        doc_number = doc_number[0]
    else:
        doc_number = None
    # 32
    area = re.compile(r'[0-9]+[.[0-9]+]? КВ.М. ПЛОЩАДЬ').findall(t)
    if area:
        area = area[0]
    else:
        area = None
    term = re.compile(r'сроком на \S+[ ]\S+[ ]').findall(t)
    if term:
        term = term[0]
    else:
        term = None
    account = re.compile(r'№[ ]?[0-9]{20}').findall(t)
    if account:
        account = account[0]
    else:
        account = None

    # 65 [\d]{1,2}[а-я\ \'\.]+[0-9]{4}
    cadastral_number = re.compile(r'[0-9\:\-]{10,25}').findall(t)
    if cadastral_number:
        print("++++++++++++++++")
        print(cadastral_number)
        cadastral_number = cadastral_number[0]

    else:
        cadastral_number = None

    # 27
    document_date = re.compile(r'[\d]{1,2}[а-я\ \'\.]+[0-9]{4}').findall(t)
    if document_date:
        print("++++++++++++++++")
        print(document_date)
        document_date = document_date[0]

    else:
        document_date = None
    print('+++++++++++++++++++++++++++++++++')
    print(doc_number, document_date, cadastral_number)
    NlpTesseract.objects.create(
        attribute_id=26,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(doc_number),
        ocr_text=doc_number
    )

    NlpTesseract.objects.create(
        attribute_id=27,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(document_date),
        ocr_text=document_date
    )

    NlpTesseract.objects.create(
        attribute_id=65,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(cadastral_number),
        ocr_text=cadastral_number
    )
    # 32
    NlpTesseract.objects.create(
        attribute_id=32,
        document_id=document_id,
        status=get_status_for_nlp_by_ocr_text(area),
        ocr_text=area
    )

    return {'scale': scale,
            'cadastr': cadastr,
            'doc_number': doc_number,
            'area': area,
            'term': term,
            'account': account}


def get_result(PATH: str, file_id: int, show=True):
    logging.info('Start work')
    # PATH1 = pdf_to_img_my_v1(PATH)
    # Evgenii +++
    PATH1 = file_to_images_converter(PATH)

    logging.info('images in %s' % PATH1)
    debug('images in %s' % PATH1)
    # Get all text from images
    Q = docimg_to_text(path=PATH1, file_id=file_id, with_rotate=False, show=True)
    debug('-------QQQQQQ--------')
    debug(Q)
    logging.info('Text extraction complete!')

    qq = ''
    flag = list(Q.keys())[0]
    for i in Q[flag]:
        # print('Q[flag][i]')
        # print(Q[flag][i])
        q = ' '.join(Q[flag][i]).replace('95', '').lower()
        qq = qq + ' ' + q

    Q_all = []
    for i in Q[flag]:
        Q_all = Q_all + Q[flag][i]

    logging.info('Name: ', flag, '\n')

    res = {}
    for key in regular_dict_old:
        res.setdefault(key, 0)
        for i in regular_dict_old[key]:
            promres = re.compile(i).findall(qq)
            res[key] = res[key] + len(set(promres))

    RES = sorted([[i[1], i[0]] for i in list(res.items())], reverse=True)

    fin_dict = {'file_name': flag,
                'doc_type': RES[0][1],
                # Свид__АГР
                'object_code': None,
                'reg_number': None,
                'district': None,
                # Разр__на_ввод
                'to_whom': None,
                'expluatation': None,
                # БТИ
                'quart': None,
                'square': None,
                'owner': None,
                # ЗУ
                'scale': None,
                'cadastr': None,
                'doc_number': None,
                'area': None,
                'term': None,
                'account': None,
                # Разр__на_стр
                'deal_number': None,
                'doc_number': None,
                'client': None,
                'issuing_authority': None,
                'date': None,
                'all_text': Q_all,
                }

    add_dict = {}

    fin_dict.update(add_dict)

    return fin_dict
