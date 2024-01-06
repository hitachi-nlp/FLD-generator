from typing import List, Optional, Iterable, Dict
import json

from FLD_generator.word_banks import build_wordbank, POS, ATTR, UserWord
from FLD_generator.word_banks.japanese import load_jp_extra_vocab
import logging
from logger_setup import setup as setup_logger

setup_logger(level=logging.INFO)


def test_word_bank(lang: str,
                   vocab: Optional[Dict[POS, List[str]]] = None):
    print('================================ testing word bank ================================')
    wb = build_wordbank(lang, vocab=vocab)
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


if __name__ == '__main__':
    # test_word_bank('eng')
    # test_word_bank(
    #     'eng',
    #     vocab=[

    #         UserWord(lemma='apple', pos=POS.NOUN, can_be_event_noun=False, can_be_entity_noun=True),
    #         UserWord(lemma='banana', pos=POS.NOUN, can_be_event_noun=False, can_be_entity_noun=True),

    #         UserWord(lemma='walk', pos=POS.VERB, can_be_transitive_verb=False, can_be_intransitive_verb=True),
    #         UserWord(lemma='run', pos=POS.VERB, can_be_transitive_vers=False, can_be_intransitive_verb=True),

    #         UserWord(lemma='tasty', pos=POS.ADJ),
    #         UserWord(lemma='beautiful', pos=POS.ADJ),
    #     ]
    # )

    # test_word_bank('jpn')

    test_word_bank(
        'jpn',
        # vocab=[
        #     UserWord(lemma='ぷにぷに', pos=POS.NOUN, can_be_event_noun=False, can_be_entity_noun=True),
        #     UserWord(lemma='ぴよぴよ', pos=POS.NOUN, can_be_event_noun=False, can_be_entity_noun=True),

        #     UserWord(lemma='歩く', pos=POS.VERB, can_be_transitive_verb=False, can_be_intransitive_verb=True),
        #     UserWord(lemma='走る', pos=POS.VERB, can_be_transitive_verb=False, can_be_intransitive_verb=True),

        #     UserWord(lemma='赤い', pos=POS.ADJ),
        #     UserWord(lemma='青い', pos=POS.ADJ),
        # ],
        vocab=load_jp_extra_vocab('./res/word_banks/japanese/punipuni_vocab.json'),
    )
