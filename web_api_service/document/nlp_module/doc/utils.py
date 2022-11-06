""" Utils for handling data """
import difflib
import numpy as np

from .gramma.rules import RULES

NEAR_CONST = 15
SIMILARITY_CONST = 0.9


def fix_gramma(text):

    def apply(x):
        for f in RULES:
            x = f(x)
        return x
        
    return [apply(t) for t in text]


def near(y1, y2):
    if np.abs(y1-y2) < NEAR_CONST:
        return True
    return False

def similar(seq1, seq2, const = SIMILARITY_CONST):
    return difflib.SequenceMatcher(a=seq1.lower(), b=seq2.lower()).ratio() > const


def check_text(list_of_substr, body):
    if isinstance(list_of_substr, str):
        list_of_substr = [list_of_substr.lower()]
    else:
        list_of_substr = [l.lower() for l in list_of_substr]
    for b in body:
        for substr in list_of_substr:
            if substr in b:
                return True
    for b in body:
        for substr in list_of_substr:
            if similar(substr, b):
                return True
            
    return False


def make_rows(data):
    data = data.sort_values(['upper_left_y', 'upper_left_x']).reset_index(drop=1)
    data_post = list(enumerate(data.itertuples()))
    result_rows = []
    

    for pos, d in data_post:
        _, prev_post = data_post[pos-1]
        if pos > 0 and near(prev_post.upper_left_y, d.upper_left_y):
            result_rows[-1] += [d]
        else:
            result_rows += [[d]]

    
    # let's go through
    result_text = []
    result_coords = []

    for i, r in enumerate(result_rows):
        result_rows[i] = list(sorted(r, key=lambda x: x.upper_left_x))
        result_text.append(' '.join([str(t.text) for t in result_rows[i]]))   
        lower_left_x = np.min([x.lower_left_x for x in r])
        lower_left_y = np.max([x.lower_left_y for x in r])
        upper_right_x = np.max([x.upper_right_x for x in r])
        upper_right_y = np.min([x.upper_right_y for x in r])
        result_coords.append({'lower_left_x':lower_left_x, 
                              'lower_left_y':lower_left_y, 
                              'upper_right_x':upper_right_x, 
                              'upper_right_y':upper_right_y})    
            
    return result_rows, result_text, result_coords