from typing import List, Optional, Iterable, Dict

from FLNL.word_banks import build_wordnet_wordbank, POS, ATTR, get_form_types
import logging

from logger_setup import setup as setup_logger

setup_logger(level=logging.INFO)


def test_word_bank(lang: str,
                   vocab_restrictions: Optional[Dict[POS, List[str]]] = None):
    wb = build_wordnet_wordbank(lang, vocab_restrictions=vocab_restrictions)
    _test_word_bank(wb)


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
    test_word_bank('eng')

    # # restricted vocab
    # test_word_bank(
    #     'eng',
    #     vocab_restrictions={
    #         POS.VERB: ['walk', 'run'],
    #         POS.NOUN: ['apple', 'banana'],
    #         POS.ADJ: ['tasty', 'beautiful'],
    #         POS.ADJ_SAT: ['red', 'green'],
    #     }
    # )

    # test_word_bank('jpn')
