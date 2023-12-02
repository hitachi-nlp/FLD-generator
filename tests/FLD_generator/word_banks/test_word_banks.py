from typing import List, Optional, Iterable, Dict

from FLD_generator.word_banks import build_wordbank, POS, ATTR
from FLD_generator.word_banks.japanese import Katsuyou, NarabaRule
import logging
from logger_setup import setup as setup_logger

import line_profiling

setup_logger(level=logging.INFO)


def test_word_bank(lang: str,
                   vocab_restrictions: Optional[Dict[POS, List[str]]] = None):
    wb = build_wordbank(lang, vocab_restrictions=vocab_restrictions)
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
            for i_word, word in enumerate(get_words(pos=pos, attrs=[attr])):
                # print(i_word)
                if attr is None:
                    print(f'{str(pos):<20}{"None":<30}{word:<20}')
                else:
                    print(f'{str(pos):<20}{str(attr.value):<30}{word:<20}')

                try:
                    # forms = get_form_types(pos)
                    forms = wb.get_forms(pos)
                except NotImplementedError as e:
                    continue

                if forms is not None:
                    for form in forms:
                        try:
                            inflated_word = wb.change_word_form(word, pos, form)
                        except NotImplementedError as e:
                            continue
                        if inflated_word is not None:
                            print(f'    {str(form):<40}{str(inflated_word):<40}')


def test_katsuyou():
    """
    青臭いでないものであって一種であるもの
    """

    wb = build_wordbank('jpn')
    katsuyou = Katsuyou([
        NarabaRule(wb),
    ])

    def _check_katsuyou(src: str, expected: str):
        applied = katsuyou.apply(src)

        print('\n\n================ _check_katsuyou ===================')
        print('str      :', src)
        print('applied  :', applied)
        print('expected :', expected)
        assert applied == expected

    _check_katsuyou('もしこの人間が起こるならばつらい', 'もしこの人間が起こればつらい')
    _check_katsuyou('もしこの人間がきれいだならばつらい', 'もしこの人間がきれいならばつらい')
    _check_katsuyou('もしこの人間が美しいならばつらい', 'もしこの人間が美しいならばつらい')

    # _check_katsuyou('この人間は美しいでない', 'この人間は美しいでない')


if __name__ == '__main__':
    # test_word_bank('eng')

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

    test_katsuyou()
