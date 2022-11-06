""" Grammar rules for kids. """

def o_rule(t):
    return t.replace('ө', 'о')
    
def lower(t):
    return t.lower()

def some_rule(t):
    return t

RULES = [o_rule, lower]
