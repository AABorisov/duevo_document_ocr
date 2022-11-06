from django import template


register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    print(dictionary)
    return dictionary.get(key)


@register.filter(name='equal_int_with_session')
def equal_int_with_session(session, value):
    print('Session' + str(session))
    print('Val' + str(value))
    if int(session) == int(value):
        print('SELECTED')
        return 'selected'
    return ''


@register.filter(name='equal_str_with_session')
def equal_str_with_session(session, value):
    if str(session) == str(value):
        return 'selected'
    return ''
