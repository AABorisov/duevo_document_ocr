def getter(replace_dict={}, to_find={}, default='', start_markers=[], start_split_markers=[],
           stop_markers=[], stop_split_markers=[], conditions=[],
           return_last=False, postprocess=lambda x: x.strip()):
    def return_function(start_text, to_find=to_find, default=default, replace_dict=replace_dict,
                        start_markers=start_markers, start_split_markers=start_split_markers,
                        stop_markers=stop_markers, stop_split_markers=stop_split_markers,
                        return_last=False, conditions=conditions, postprocess=postprocess, debug=False,
                        max_rows=10):
        UNMET_SIGN = '$%#!@'
        if type(start_text) == list:

            text = UNMET_SIGN.join(start_text)
        else:
            assert UNMET_SIGN in start_text, start_text
            text = start_text
        text = text.lower()
        if len(to_find) > 0:
            if type(to_find) == list:
                to_find = {x: x for x in to_find}
            for key in to_find.keys():
                key_lower = key.lower()
                # key=key.replace(' ',UNMET_SIGN)
                where_are_unmet = []
                clean_text = ''
                len_ = len(text)
                for i in range(len_):
                    if i < len(text) and text[i:i + len(UNMET_SIGN)] == UNMET_SIGN:
                        where_are_unmet.append(i)
                        text = text[:i] + ' ' + text[(i + len(UNMET_SIGN)):]
                if debug:
                    print('Finding ' + key_lower + 'in ' + text[:1000])
                if key_lower in text:
                    if debug:
                        print('found')
                    before_text = text.split(key_lower)[0]
                    after_text = before_text + key_lower
                    start_count = sum([int(j < len(before_text)) for j in where_are_unmet])
                    end_count = sum([int(j <= len(after_text)) for j in where_are_unmet])
                    if end_count == start_count:
                        end_count += 1
                    return to_find[key], (start_count, end_count)
            if len(default) > 0:
                return default, (-1, -1)
        if len(conditions) > 0:
            for condition in conditions:
                if debug:
                    print('To condition ' + text)
                result = condition(text)
                if result is not None:
                    return result, (-1, -1)
        count0 = text.count(UNMET_SIGN)
        for key in replace_dict:
            count0 = text.count(UNMET_SIGN)
            text = text.replace(key, replace_dict[key])
            count1 = text.count(UNMET_SIGN)
            assert count0 == count1
        if type(start_markers) == str:
            start_markers = [start_markers]
        if type(stop_markers) == str:
            stop_markers = [stop_markers]
        if start_split_markers == []:
            start_split_markers = start_markers
        if stop_split_markers == []:
            stop_split_markers = stop_markers

        for start_marker, start_split_marker in zip(start_markers, start_split_markers):
            if start_marker.lower() in text:
                if debug:
                    print('Found ' + start_marker + ' split by ' + start_split_marker)
                text_splitted = text.split(start_split_marker.lower())[1:]
                text = start_split_marker.lower().join(text_splitted)
                count1 = text.count(UNMET_SIGN)
            else:
                pass
        count1 = text.count(UNMET_SIGN)

        start_signs = count0 - count1  # Number of string from which we start
        # print(count1)
        # print(start_signs)
        text = text.strip()
        if debug:
            print('start ')
            print(text)
        for stop_marker, stop_split_marker in zip(stop_markers, stop_split_markers):
            if stop_marker.lower() in text:
                text = text.split(stop_split_marker.lower())[0]
            count3 = text.count(UNMET_SIGN)
        end_signs = count3
        # print('End signs are '+str(end_signs))
        if debug:
            print('stop ')
            print(text)
        try:
            answer = postprocess(text)
            if type(answer) == str and UNMET_SIGN in answer:
                answer = answer.split(UNMET_SIGN)[0]
            end_signs = min(end_signs, start_signs + max_rows)
            return answer, (start_signs, start_signs + end_signs)
        except:
            raise Exception(text)

    return return_function


class Doc2():
    def __init__(self):
        print('+++++++++++++++++++++++++++++++++++++++DOC2++++++++++++++++++++++++++++++++++++++++++++++++')
        def find_year(x):
            for year in range(1988, 2020):
                if str(year) in str(x):
                    return year
            return ''

        self.type_get = getter(replace_dict={'ГОРОДА МОСКВЕ': 'ГОРОДА МОСКВЫ'},
                               to_find={
                                   'ДОГОВОР БЕЗВОЗМЕЗДНОГО ПОЛЬЗОВАНИЯ ЗЕМЕЛЬНЫМ УЧАСТКОМ': 'ДОГОВОР БЕЗВОЗМЕЗДНОГО ПОЛЬЗОВАНИЯ ЗЕМЕЛЬНЫМ УЧАСТКОМ',
                                   'Пользователь': 'ДОГОВОР БЕЗВОЗМЕЗДНОГО ПОЛЬЗОВАНИЯ ЗЕМЕЛЬНЫМ УЧАСТКОМ',
                                   'ДОГОВОР АРЕНДЫ ЗЕМЕЛЬНОГО УЧАСТКА': 'ДОГОВОР АРЕНДЫ ЗЕМЕЛЬНОГО УЧАСТКА',
                                   'Арендодатель': 'ДОГОВОР АРЕНДЫ ЗЕМЕЛЬНОГО УЧАСТКА',
                                   'ДОГОВОР КУПЛИ-ПРОДАЖИ ЗЕМЕЛЬНОГО УЧАСТКА': 'ДОГОВОР КУПЛИ-ПРОДАЖИ ЗЕМЕЛЬНОГО УЧАСТКА',
                                   'Покупатель': 'ДОГОВОР КУПЛИ-ПРОДАЖИ ЗЕМЕЛЬНОГО УЧАСТКА',
                                   'договор аренды земли': 'договор аренды земли'})
        self.number_get = getter(
            replace_dict={'m+': 'm-', 'ne': '№', 'no': '№', 'nº': '№', 'nо': '№', 'N 의': '№', 'N ': '№',
                          'Москомвем No': '№', ' No удостоверительная надпись ': ' ',
                          'No. faomepsey. ': ' ', 'No 了': ' '},
            start_markers=['№'],
            stop_markers=['(номер договора', 'дги', 'Москомзем Архив', 'Департамент земельных ресурсов',
                          'ю/', 'Правительство Москвы', 'Москомзем'],
            postprocess=lambda x: (x[0].upper() + x[1:].replace(
                '+', '-'))[:10].replace(' ', '') if len(x) > 0 else '')
        self.date_get = getter(
            replace_dict={'m+': 'm-', 'ne': '№', 'no': '№', 'nº': '№', 'nо': '№', 'N 의': '№', ' N ': '№',
                          'Москомвем No': '№'},
            start_markers=['(Номер договора)', 'ю/'],
            stop_markers=['№', 'пользователь', 'арендодатель', 'покупатель', '(число)'],
            postprocess=find_year)
        self.organ_get = getter(to_find=['Департамент земельных ресурсов города Москвы',
                                         'Департамент городского имущества города Москвы',
                                         'Московский земельный комитет', 'Москомзем',
                                         'Комитет по управлению имуществом Администрации Подольского муниципального района'],
                                default='Орган не найден')

        self.square_get = getter(replace_dict={'квадратных метров': 'кв.м', 'кв. м': 'кв.м'},
                                 start_markers=['площадью', 'площадь'],
                                 stop_markers=['кв.м'], return_last=True,
                                 postprocess=lambda x: ''.join([j for j in x[-20:] if j in '0123456789.,']) + ' кв.м')

        self.purpose_get = getter(replace_dict={'дда': 'для'}, to_find=[],
                                  start_markers=['на условиях аренды для',
                                                 'на условиях аренды для',
                                                 'в аренду для', 'в безвозмездное пользование для',
                                                 'использования прилегающей территории для',
                                                 'предоставляемый в аренду под',
                                                 'установленный вид разрешенного использования участка:',
                                                 'строительства и ', 'размещения и '],
                                  stop_markers=['1.2', 'в соответствии с установленным', '.'])
        self.category_get = getter(
            to_find=['земли населенных пунктов', 'земли сельскохозяйственного назначения', 'земли запаса',
                     'земли лесного фонда',
                     'земли водного фонда', 'земли особо охраняемых территорий и объектов',
                     'земли особо охраняемых территорий',
                     'границах особо охраняемой природной территории',
                     'земли особо охраняемых объектов',
                     'земли промышленности', 'земли энергетики', 'земли транспорта', 'земли связи',
                     'земли радиовещания', 'земли телевидения', 'земли информатики',
                     'земли для обеспечения космической деятельности', 'земли обороны',
                     'земли безопасности', 'земли иного специального назначения'], default='Земли не найдены')
        self.plan_get = getter(to_find={'план земельного участка': 'есть'}, default='нет')
        self.condition_get = getter(start_markers=['особые условия договора'],
                                    stop_markers='права и обязанности арендатора')
        self.other_fromto_get = getter(replace_dict={'дейcттвия': 'действия'},
                                       start_markers=['срок действия договора аренды',
                                                      'срок действия договора.'
                                                      'срок действия договора 2.1.',
                                                      'срок действия настоящего договора',
                                                      'договор заключается сроком', 'договор заключен сроком',
                                                      'договор заключается на', 'срок аренды'],
                                       stop_markers=['размер и расчет арендной платы',
                                                     '2.2.', '2. 2.', '3.', 'и вступает',
                                                     'течение срока', 'срок', 'со дня государственной регистрации'],
                                       conditions=[lambda x: 'бессрочно' if 'покупатель' in x else None],
                                       postprocess=lambda x: x if len(x) < 100 else '')
        self.from_get = getter(conditions=[lambda x: 'бессрочно' if 'покупатель' in x else ''])
        self.cadastre_get = getter(start_markers=['кадастровый номер'],
                                   stop_markers=['площадью', 'имеющий', 'исходные данные для расчета',
                                                 'условный номер',
                                                 'правительство москвы', 'масштаб'])
        self.to_get = self.from_get
        self.share_get = getter(conditions=[lambda x: ''])
        self.address_get = getter(replace_dict={'адресные ориентиры': 'по адресу', 'адресный ориентир': 'по адресу'},
                                  start_markers=['по адресу:'], stop_markers=['предоставляемый',
                                                                              '(', 'предоставляемый', 'кадастровый',
                                                                              'предоставлаемый', 'предос- тавляемый',
                                                                              'принадлежащем', 'заключили',
                                                                              'площадью', 'принадлежащее', 'масштаб',
                                                                              'пре- доставляемый',
                                                                              'масштаб 1',
                                                                              'предоставленный в пользование',
                                                                              'предостав- ляе',
                                                                              'мосuтоб', 'моcumоб', 'мacumаб',
                                                                              'срок', 'именуемый', 'dem.cad',
                                                                              ' предоставляег^ый',
                                                                              'зарегистрированный', '10 p3', 'мaсштаб'])
        self.trait_get = getter(conditions=[
            lambda x: 'земельный участок по адресу: ' + self.address_get(x)[0] + ' цель: ' + self.purpose_get(x)[0]])

        self.field_to_function = {'Тип документа': self.type_get, 'Номер': self.number_get, 'Дата': self.date_get,
                                  'Выдавший орган': self.organ_get,
                                  'Основная часть – предмет договора/его площадь': self.square_get,
                                  'Основная часть – предмет договора/категория земель': self.category_get,
                                  'Основная часть – предмет договора/адресный ориентир': self.address_get,
                                  'Основная часть – предмет договора/Целевое назначение земельного участка': self.purpose_get,
                                  'Особые условия (особые условия использования земельного участка)': self.condition_get,
                                  'План земельного участка': self.plan_get,
                                  'Основная часть – предмет договора/Хозяйствующие субъекты при наличии разделение на доли': self.share_get,
                                  'Основная часть – предмет договора/характеристики земельного участка': self.trait_get,
                                  'Срок действия договора аренды/с даты': self.from_get,
                                  'Срок действия договора аренды/до даты': self.to_get,
                                  'Срок действия договора аренды/другое': self.other_fromto_get,
                                  'Кадастровый номер': self.cadastre_get}

    def get_ids(self, dataframe, start_ind, end_ind):
        dataframe.index = [j for j in range(len(dataframe))]
        return dataframe['ocr_id'][start_ind:end_ind]

    def parse_fields(self, text):
        answer = {key: self.field_to_function[key](text)[0] for key in self.field_to_function}
        ocr_ids = [[] for x in answer]
        return answer, {}  # key: answer[key][1] for key in self.field_to_function}#tuple (start_ind, end_ind)
