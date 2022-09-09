from typing import List, Optional, Iterable

from FLNL.word_banks import EnglishWordBank, POS, ATTR, get_form_types
import logging

from logger_setup import setup as setup_logger

setup_logger(level=logging.INFO)

wb = EnglishWordBank()


def get_words(pos: Optional[POS] = None,
              attrs: Optional[List[ATTR]] = None) -> Iterable[str]:
    attrs = attrs or []
    for word in wb.get_words():
        if pos is not None and pos not in wb.get_pos(word):
            continue
        if any((attr not in wb.get_attrs(word)
                for attr in attrs)):
            continue
        yield word


for pos in POS:
    for attr in [None] + list(ATTR):
        for word in get_words(pos=pos, attrs=[attr]):
            print(f'{str(pos):<10}{str(attr.value):<30}{word:<20}')
            form_types = get_form_types(pos)
            if form_types is not None:
                for form_type in form_types:
                    inflated_word = wb.change_word_form(word, form_type)
                    if inflated_word is not None:
                        print(f'    {str(form_type):<20}{str(inflated_word):<20}')
