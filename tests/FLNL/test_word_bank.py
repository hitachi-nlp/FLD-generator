from typing import List, Optional, Iterable

from FLNL.word_banks import EnglishWordBank, JapaneseWordBank, POS, ATTR, get_form_types
import logging

from logger_setup import setup as setup_logger

setup_logger(level=logging.INFO)


def test_english_word_bank():
    wb = EnglishWordBank()
    _test_word_bank(wb)


def test_japanese_word_bank():
    wb = JapaneseWordBank()
    _test_word_bank(wb)
    # for word in wb.get_words():
    #     print(word)


def _test_word_bank(wb):

    def get_words(pos: Optional[POS] = None,
                  attrs: Optional[List[ATTR]] = None) -> Iterable[str]:
        attrs = attrs or []
        for word in wb.get_words():
            if pos is not None and pos not in wb.get_pos(word):
                continue
            if any((attr not in wb.get_attrs(word)
                    for attr in attrs
                    if attr is not None)):
                continue
            yield word

    for pos in POS:
        for attr in [None] + list(ATTR):
            for word in get_words(pos=pos, attrs=[attr]):
                if attr is None:
                    print(f'{str(pos):<10}{"None":<30}{word:<20}')
                else:
                    print(f'{str(pos):<10}{str(attr.value):<30}{word:<20}')

                form_types = get_form_types(pos)
                if form_types is not None:
                    for form_type in form_types:
                        inflated_word = wb.change_word_form(word, form_type)
                        if inflated_word is not None:
                            print(f'    {str(form_type):<40}{str(inflated_word):<40}')


if __name__ == '__main__':
    test_english_word_bank()
    # test_japanese_word_bank()
