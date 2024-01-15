from typing import List, Optional, Set, Dict
import logging
import sys
import json
from collections import defaultdict

from FLD_generator.formula import Formula, negate, eliminate_double_negation
from FLD_generator.translators import build as build_translator, TemplatedTranslator
from FLD_generator.translators.japanese import JapaneseTranslator
from FLD_generator.word_banks import build_wordbank
from FLD_generator.word_banks.base import POS, UserWord
from FLD_generator.word_banks.japanese import load_jp_extra_vocab
from FLD_generator.translators.japanese.postprocessor import build_postprocessor
from FLD_generator.utils import fix_seed
from FLD_generator.knowledge_banks import build_knowledge_bank
from FLD_generator.knowledge_banks.base import KnowledgeBankBase
from logger_setup import setup as setup_logger

import line_profiling

fix_seed(0)


def _build_translator(lang,
                      translation_config='thing',
                      no_adj_verb_as_zeroary=False,
                      extra_vocab: Optional[Dict[POS, List[UserWord]]] = None,
                      knowledge_banks: Optional[List[KnowledgeBankBase]] = None,
                      **kwargs) -> TemplatedTranslator:
    word_bank = build_wordbank(lang, extra_vocab=extra_vocab)
    return build_translator(
        lang,
        translation_config,
        word_bank,
        use_fixed_translation=False,
        reused_object_nouns_max_factor=1.0,
        limit_vocab_size_per_type=None,
        # volume_to_weight='sqrt',
        volume_to_weight='log10',
        default_weight_factor_type='W_VOL__1.0',
        adj_verb_noun_ratio='1-1-1',
        no_adj_verb_as_zeroary=no_adj_verb_as_zeroary,
        knowledge_banks=knowledge_banks,
    )


def make_show_translation_func(translator):

    def show_translations(formula_reps: List[str],
                          trial=5,
                          intermediate_constant_formula_reps: Optional[List[str]] = None,
                          do_negation=True,
                          **kwargs) -> None:
        formulas = [Formula(rep) for rep in formula_reps]
        intermediate_constant_formulas = [Formula(rep)
                                          for rep in intermediate_constant_formula_reps or []]
        if do_negation:
            types = ['posi', 'neg']
        else:
            types = ['posi']

        for type_ in types:
            if type_ == 'posi':
                _formulas = formulas
            elif type_ == 'neg':
                _formulas = [eliminate_double_negation(negate(formula)) for formula in formulas]
            print('\n\n\n================   translation  ================')
            for i_trial in range(0, trial):
                if len(formulas) >= 2:
                    print('')
                translations, _ = translator.translate(_formulas, intermediate_constant_formulas or [], **kwargs)
                for formula, (_, translation, _, knowledge_type) in zip(_formulas, translations):
                    print(formula.rep,
                          f'(interm={intermediate_constant_formulas}, knowledge_type={knowledge_type})',
                          '  ->  ',
                          f'{translation:<100}')
            sys.stdout.flush()

    return show_translations


def test_templated_translator_lang(lang: str,
                                   translation_config='thing',
                                   no_adj_verb_as_zeroary=False,
                                   extra_vocab: Optional[Dict[POS, List[UserWord]]] = None,
                                   knowledge_banks: Optional[List[KnowledgeBankBase]] = None):
    translator = _build_translator(lang,
                                   translation_config=translation_config,
                                   no_adj_verb_as_zeroary=no_adj_verb_as_zeroary,
                                   extra_vocab=extra_vocab,
                                   knowledge_banks=knowledge_banks)
    show_translations = make_show_translation_func(translator)

    if knowledge_banks is None:
        show_translations(['{A}'], trial=30)
        show_translations(['¬({A})'], trial=30)

        show_translations(['({A} & {B})'], trial=30)
        show_translations(['(¬{A} & {B})'], trial=30)
        show_translations(['({A} & ¬{B})'], trial=30)
        show_translations(['(¬{A} & ¬{B})'], trial=30)

        show_translations(['({A} v {B})'], trial=30)
        show_translations(['(¬{A} v {B})'], trial=30)
        show_translations(['({A} v ¬{B})'], trial=30)
        show_translations(['(¬{A} v ¬{B})'], trial=30)

        show_translations(['{A} -> {B}'], trial=30)
        show_translations(['¬{A} -> {B}'], trial=30)
        show_translations(['{A} -> ¬{B}'], trial=30)
        show_translations(['({A} & {B}) -> {C}'], trial=30)
        show_translations(['({A} v {B}) -> {C}'], trial=30)
        show_translations(['{A} -> ({B} & {C})'], trial=30)
        show_translations(['{A} -> ({B} v {C})'], trial=30)


        show_translations(['{A}{a}'], trial=30)

        show_translations(['({A}{a} & {B}{a})'], trial=30)
        show_translations(['(¬{A}{a} & {B}{a})'], trial=30)
        show_translations(['({A}{a} & ¬{B}{a})'], trial=30)
        show_translations(['(¬{A}{a} & ¬{B}{a})'], trial=30)

        show_translations(['({A}{a} v {B}{a})'], trial=30)
        show_translations(['(¬{A}{a} v {B}{a})'], trial=30)
        show_translations(['({A}{a} v ¬{B}{a})'], trial=30)
        show_translations(['(¬{A}{a} v ¬{B}{a})'], trial=30)

        show_translations(['({A}{a} -> {B}{a})'], trial=30)
        show_translations(['(¬{A}{a} -> {B}{a})'], trial=30)
        show_translations(['({A}{a} -> ¬{B}{a})'], trial=30)
        show_translations(['({A}{a} & {B}{a}) -> {C}{c}'], trial=30)
        show_translations(['({A}{a} v {B}{a}) -> {C}{c}'], trial=30)
        show_translations(['{A}{a} -> ({B}{b} & {C}{b})'], trial=30)
        show_translations(['{A}{a} -> ({B}{b} v {C}{b})'], trial=30)


        show_translations(['(Ex): {A}x'], trial=30)
        show_translations(['(Ex): (¬{A}x & {B}x)'], trial=30)
        show_translations(['(Ex): (¬{A}x v {B}x)'], trial=30)
        show_translations(['(Ex): {A}x -> {B}x'], trial=30)
        show_translations(['(Ex): (¬{A}x & {B}x) -> {C}x'], trial=30)
        show_translations(['(Ex): (¬{A}x v {B}x) -> {C}x'], trial=30)

        show_translations(['(x): {A}x'], trial=30)
        show_translations(['(x): (¬{A}x & {B}x)'], trial=30)
        show_translations(['(x): (¬{A}x v {B}x)'], trial=30)
        show_translations(['(x): {A}x -> {B}x'], trial=30)
        show_translations(['(x): (¬{A}x & {B}x) -> {C}x'], trial=30)
        show_translations(['(x): (¬{A}x v {B}x) -> {C}x'], trial=30)

        # # multiple formulas
        show_translations(
            [
                '{A}{a} -> {B}{b}',
                '{B}{b} -> {C}{c}',
                '{C}{c} -> {D}{d}',
            ],
            5
        )

        show_translations(
            [
                '{A}',
                '{B}',
                '{C}',
                '{D}{d}',
                '{E}{e}',
                '{F}{f}',
            ],
            5,
        )

        show_translations(
            [
                '(x): {A}x -> {B}x',
                '(x): {B}x -> {C}x',
                '(x): {C}x -> {D}x',
            ],
            5,
        )

        show_translations(
            [
                '{A}{a} -> {B}{b}',
                '{C}{b} -> {D}{d}',
            ],
            5,
            intermediate_constant_formula_reps=['{b}', '{d}'],
        )

        show_translations(
            [
                '{A}{a} -> {B}{b}',
                '{C}{c} -> {D}{d}',
                '{F}{f} -> {G}{g}',
            ],
            5,
            intermediate_constant_formula_reps=['{a}', '{d}'],
        )
    else:
        show_translations(['{A}{a}'], trial=100, knowledge_injection_idxs=[0], do_negation=False)
        show_translations(['{A} -> {B}'], trial=100, knowledge_injection_idxs=[0], do_negation=False)
        show_translations(['(x): {A}x -> {B}x'], trial=100, knowledge_injection_idxs=[0], do_negation=False)
        show_translations(['(x): {A}x -> ¬{B}x'], trial=100, knowledge_injection_idxs=[0], do_negation=False)


def test_eng():
    test_templated_translator_lang('eng')


def test_eng_with_knowledge():
    knowledge_banks = [
        # build_knowledge_bank(
        #     'atomic',
        #     './res/knowledge_banks/commonsense-kg-completion/data/atomic/train.txt',
        # ),
        # build_knowledge_bank(
        #     'concept_net_100k',
        #     './res/knowledge_banks/commonsense-kg-completion/data/ConceptNet/train.txt',
        # ),
        build_knowledge_bank(
            'dbpedia',
            './res/knowledge_banks/DBpedia500/train1.txt',
        ),
    ]

    test_templated_translator_lang('eng', knowledge_banks=knowledge_banks)


def test_jpn():
    test_templated_translator_lang('jpn')
    

def test_jpn_with_vocab(vocab_name_or_path='./res/word_banks/japanese/punipuni_vocab.json'):
    test_templated_translator_lang('jpn',
                                   translation_config='thing.v1.pretty',
                                   no_adj_verb_as_zeroary=True,
                                   extra_vocab=vocab_name_or_path)


@profile
def test_jpn_postprocess():
    wb = build_wordbank('jpn', extra_vocab='punipuni')
    # wb = build_wordbank('jpn')
    postprocessor = build_postprocessor(wb)

    def _check_katsuyou(src: str, golds: List[str], trial=1000):
        print('\n\n================ _check_katsuyou ===================')
        print('input      :', src)
        print()
        print('expected   :', golds)

        done: Set[str] = set([])
        for _ in range(trial):
            postprocessor.reset_assets()
            pred = postprocessor.apply(src)
            if pred in done:
                continue

            print()
            print('output     :', pred)
            assert pred in golds
            done.add(pred)
            if done == set(golds):
                break

        assert done == set(golds)

    _check_katsuyou('この人間が走るならばつらい', ['この人間が走ればつらい'])
    _check_katsuyou('この人間が機械だならばつらい', ['この人間が機械ならばつらい'])
    _check_katsuyou('この人間がきれいだならばつらい', ['この人間がきれいならばつらい'])
    _check_katsuyou('この人間が美しいならばつらい', ['この人間が美しいならばつらい'])

    _check_katsuyou('この人間が走るならつらい', ['この人間が走るならつらい'])
    _check_katsuyou('この人間が機械だならつらい', ['この人間が機械ならつらい'])
    _check_katsuyou('この人間がきれいだならつらい', ['この人間がきれいならつらい'])
    _check_katsuyou('この人間が美しいならつらい', ['この人間が美しいならつらい'])

    _check_katsuyou('この人間がぷえぷやだならばつらい', ['この人間がぷえぷやならばつらい'])

    _check_katsuyou('この人間がぷえぷやだならつらい', ['この人間がぷえぷやならつらい'])




    _check_katsuyou('この人間がきれいだか美しい', ['この人間がきれいであるか美しい'])
    _check_katsuyou('この人間が会議だか美しい', ['この人間が会議であるか美しい'])
    _check_katsuyou('もしこのブローチは小館花であるか菊雄だか両方ならばあのどら猫はいする', ['もしこのブローチは小館花であるか菊雄であるか両方ならばあのどら猫はいする'])

    _check_katsuyou('この人間がぷえぷやだか美しい', ['この人間がぷえぷやであるか美しい'])



    _check_katsuyou('きれいだものはある', ['きれいなものはある'])
    _check_katsuyou('きれいだことはある', ['きれいなことはある'])
    _check_katsuyou('「きれいだ」ものはある', ['「きれいな」ものはある'])

    _check_katsuyou('ぷえぷやだものはある', ['ぷえぷやなものはある'])



    _check_katsuyou('この人間は美しいし赤い', ['この人間は美しいし赤い', 'この人間は美しくて赤い'])
    _check_katsuyou('この人間はきれいだし赤い', ['この人間はきれいだし赤い', 'この人間はきれいで赤い'])

    _check_katsuyou('この人間はぷえぷやだし赤い', ['この人間はぷえぷやだし赤い', 'この人間はぷえぷやで赤い'])



    _check_katsuyou('この人間は走るない', ['この人間は走らない'])
    _check_katsuyou('この人間は美しいない', ['この人間は美しくない'])
    _check_katsuyou('夫婦らしいない物は分厚いかあるいは忌まわしい', ['夫婦らしくない物は分厚いかあるいは忌まわしい'])
    _check_katsuyou('剥がれ落ちるない', ['剥がれ落ちない'])
    _check_katsuyou('この人間は機械だない', ['この人間は機械でない'])
    _check_katsuyou('この人間は機械だないし，あの熊も機械だない', ['この人間は機械でないし，あの熊も機械でない', 'この人間は機械でなくて，あの熊も機械でない'])
    _check_katsuyou('Xということが成り立つない', ['Xということが成り立たない'])


    _check_katsuyou('この人間はぷえぷやだない', ['この人間はぷえぷやでない'])



    _check_katsuyou('この人間はきれいだない', ['この人間はきれいでない'])
    _check_katsuyou('この人間が美しいない', ['この人間が美しくない'])
    _check_katsuyou('この人間は会議するない', ['この人間は会議しない'])
    _check_katsuyou('「黒いということは起こらない」ということは事実と異なるない', ['「黒いということは起こらない」ということは事実と異ならない'])


    _check_katsuyou('この人間は走るないない', ['この人間は走らなくない'])
    _check_katsuyou('この人間は機械だないない', ['この人間は機械でなくない'])
    _check_katsuyou('この人間はきれいだないない', ['この人間はきれいでなくない'])
    _check_katsuyou('この人間が美しいないない', ['この人間が美しくなくない'])

    _check_katsuyou('この人間はぷえぷやだないない', ['この人間はぷえぷやでなくない'])



    _check_katsuyou(
        'この人間とあの人間とその人間とこの熊とあの熊とその熊',
        [f'{ningen_kosoado}人間と{ningen_kosoado}人間と{ningen_kosoado}人間と{kuma_kosoado}熊と{kuma_kosoado}熊と{kuma_kosoado}熊'
         for ningen_kosoado in ['この', 'あの', 'その']
         for kuma_kosoado in ['この', 'あの', 'その']]
    )

if __name__ == '__main__':
    setup_logger(level=logging.DEBUG)

    # test_eng()
    # test_eng_with_knowledge()

    test_jpn_postprocess()

    # test_jpn()
    # test_jpn_with_vocab(vocab_name_or_path='./res/word_banks/japanese/punipuni_vocab.json')
    # test_jpn_with_vocab(vocab_name_or_path='./res/word_banks/japanese/BCCWJ_vocab/BCCWJ.all.json')
