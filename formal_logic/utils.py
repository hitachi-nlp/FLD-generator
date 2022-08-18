from typing import Dict, Any
from nltk.corpus import cmudict


def starts_with_vowel_sound(word, pronunciations=cmudict.dict()):
    for syllables in pronunciations.get(word, []):
        return syllables[0][-1].isdigit()  # use only the first one


def flatten_dict(dic: Dict[str, Any]) -> Dict[str, Any]:
    flat_dic = {}
    for key, val in dic.items():
        if isinstance(val, dict):
            for child_key, child_val in flatten_dict(val).items():
                flat_key = '.'.join([key, child_key])
                flat_dic[flat_key] = child_val
        else:
            flat_dic[key] = val
    return flat_dic

