import pandas as pd
import numpy as np
import os

from collections import defaultdict

def process_2(text,name):
    all_traits = defaultdict(list)

    text=text.replace('ГОРОДА МОСКВЕ','ГОРОДА МОСКВЫ')
    user_to_type = {'Пользователь':'ДОГОВОР БЕЗВОЗМЕЗДНОГО ПОЛЬЗОВАНИЯ ЗЕМЕЛЬНЫМ УЧАСТКОМ', 
                    'Арендодатель':'ДОГОВОР АРЕНДЫ ЗЕМЕЛЬНОГО УЧАСТКА',
                    'Покупатель':'ДОГОВОР КУПЛИ-ПРОДАЖИ ЗЕМЕЛЬНОГО УЧАСТКА'}
    type_  = ''
    for user_type in user_to_type:
        if user_type.upper() in text.upper():
            type_ = user_to_type[user_type]
    number_ = name.replace(' ','').replace('№','')[:11]
    #number_text = text.split('(Номер договора)')[0]
    #found_number=False
    #for number_sign in ['Ne','No','№']:
        #if number_sign in number_text:
            #number_text = number_text.split(number_sign)[1]
            #found_number = True
    #if found_number:
    #    number_ = number_text
    #    else:
    #        raise Exception(number_text)
    date_ = ''
    date_text = text.split('(Число')[0].split(')')[1]
    years = [str(j) for j in range(1988,2020)]
    for year in years:
        if year in date_text:
            curr_date = date_text.split(year)[0]+year
            if len(curr_date) < 20:
                date_ = curr_date
    organs = ['Департамент земельных ресурсов города Москвы','Департамент городского имущества города Москвы',
             'Московский земельный комитет','Москомзем',  
              'Комитет по управлению имуществом Администрации Подольского муниципального района']
    organ_ = None
    for organ in organs:
        if organ.upper() in text.upper():
            organ_ = organ
    if organ_ is None:
        raise Exception(name)
    square_text = text.replace('кв. м','кв.м').replace('квадратных метров','кв.м')
    square_text = text.split('кв.м')[0].split(' ')
    for val in square_text:
        try:
            square_ = str(int(val))+' кв.м'
        except:
            pass
    replace_text = text.replace('адресные ориентиры','по адресу').replace('адресный ориентир','по адресу')
    if 'по адресу' in text.lower():
        address_ = text.lower().split('по адресу')[1].split('предоставляемый')[0][:100]
        for split_val in ['(','предоставляемый','кадастровый','принадлежащем','заключили',
                          'площадью','принадлежащее','масштаб','мосuтоб','моcumоб','мacumаб',
                          'срок','именуемый' ,'dem.cad',' предоставляег^ый']:
            address_ = address_.split(split_val)[0]
    else:
        address_ = ''
    land_categories = ['земли населенных пунктов','земли сельскохозяйственного назначения','земли запаса','земли лесного фонда',
                      'земли водного фонда','земли особо охраняемых территорий и объектов','земли особо охраняемых территорий',
                       'границах особо охраняемой природной территории',
                       'земли особо охраняемых объектов',
                       'земли промышленности','земли энергетики','земли транспорта', 'земли связи',
                       'земли радиовещания','земли телевидения', 'земли информатики', 
                       'земли для обеспечения космической деятельности', 'земли обороны', 
                       'земли безопасности','земли иного специального назначения']
    category_ = ''
    for tofind_category in land_categories:
        if tofind_category in text.lower():
            category_ = tofind_category
    
    purpose_ = ''
    rent_phrases = ['с целью','в целях','в пользование','в аренду','в безвозмездное пользование','срочное пользование', ' а пользование',
                'вид функционального использования участка']
    for rent_phrase in rent_phrases:
        if rent_phrase in text.lower() and purpose_ == '':
            purpose_texts = text.lower().split(rent_phrase)
            purpose_ = purpose_texts[1][:100]
            #try:
            #    ind1,ind2 = purpose_texts[1].index('.'),purpose_texts[1].index('(')
            #    purpose_ = purpose_texts[1][:min(ind1,ind2)]
            #except:
            #    raise Exception(purpose_texts)
            
    subjects_ =''
    from_ =''
    to_ =''
    other_ =''
    conditions_ =''
    traits_ = ''
    if 'план земельного участка' in text.lower():
        plan_ = 'ecть'
    else:
        plan_ = 'нет'
    
    ANSWER = {'Тип документа':type_,#ok
              'Номер':number_,#ok
              'Дата':date_,#best_done
              'Выдавший орган ':organ_,#ok
              'Основная часть – предмет договора/его площадь':square_,#ok
              'Основная часть – предмет договора/категория земель':category_,#best_done
              'Основная часть – предмет договора/адресный ориентир':address_,
              'Основная часть – предмет договора/Целевое назначение земельного участка.':purpose_,
              'Основная часть – предмет договора/Хозяйствующие субъекты при наличии разделение на доли.':subjects_,
              'Срок действия договора аренды/с даты':from_,
              'Срок действия договора аренды/до даты':to_,
              'Срок действия договора аренды/другое':other_,
               'Особые условия (особые условия использования земельного участка)':conditions_,
                'Основная часть – предмет договора/характеристики земельного участка':traits_,
               'План земельного участка':plan_#ok
              }
    for key in ANSWER:
        all_traits[key].append(ANSWER[key])
    return ANSWER
