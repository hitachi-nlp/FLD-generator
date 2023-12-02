from typing import List, Optional
import logging
import sys

from FLD_generator.formula import Formula, negate, eliminate_double_negation
from FLD_generator.translators import build as build_translator, TemplatedTranslator
from FLD_generator.word_banks import build_wordbank
from FLD_generator.translators.japanese.postprocess import Katsuyou, NarabaKatsuyouRule, NaiKatsuyouRule
from FLD_generator.utils import fix_seed
from FLD_generator.knowledge_banks import build_knowledge_bank
from FLD_generator.knowledge_banks.base import KnowledgeBankBase
from logger_setup import setup as setup_logger

fix_seed(0)


def _build_translator(lang,
                      knowledge_banks: Optional[List[KnowledgeBankBase]] = None):
    # word_bank = None
    word_bank = build_wordbank(lang)

    if lang == 'eng':
        # translation_config_dir = './configs/translations/eng/thing.v1/'
        translation_config_dir = './configs/translations/eng/thing_person.v0/'
    elif lang == 'jpn':
        translation_config_dir = './configs/translations/jpn/thing.v1/'
    else:
        raise ValueError()

    translator = build_translator(
        lang,
        [translation_config_dir],
        word_bank,
        use_fixed_translation=False,
        reused_object_nouns_max_factor=1.0,
        limit_vocab_size_per_type=None,
        # volume_to_weight='sqrt',
        volume_to_weight='log10',
        default_weight_factor_type='W_VOL__1.0',
        adj_verb_noun_ratio='1-1-1',
        knowledge_banks=knowledge_banks,
    )

    return translator


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
                          f'(interm={intermediate_constant_formulas})',
                          '  ->  ',
                          f'{translation:<100}  knowledge_type={str(knowledge_type)}')
            sys.stdout.flush()

    return show_translations



def test_templated_translator_lang(lang: str, knowledge_banks: Optional[List[KnowledgeBankBase]] = None):
    translator = _build_translator(lang, knowledge_banks=knowledge_banks)
    show_translations = make_show_translation_func(translator)

    if knowledge_banks is None:
        show_translations(['{A}'], trial=30)
        show_translations(['¬{A}'], trial=30)
        show_translations(['¬({A})'], trial=30)

        show_translations(['(¬{A} & {B})'], trial=30)
        show_translations(['(¬{A} v {B})'], trial=30)

        show_translations(['{A} -> {B}'], trial=30)
        show_translations(['¬{A} -> {B}'], trial=30)
        show_translations(['{A} -> ¬{B}'], trial=30)
        show_translations(['({A} & {B}) -> {C}'], trial=30)
        show_translations(['({A} v {B}) -> {C}'], trial=30)
        show_translations(['{A} -> ({B} & {C})'], trial=30)
        show_translations(['{A} -> ({B} v {C})'], trial=30)


        show_translations(['{A}{a}'], trial=30)
        show_translations(['¬{A}{a}'], trial=30)

        show_translations(['(¬{A}{a} & {B}{a})'], trial=30)
        show_translations(['(¬{A}{a} v {B}{a})'], trial=30)

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
                '{C}{c} -> {D}{d}',
                '{F}{f} -> {G}{g}',
            ],
            5,
            intermediate_constant_formulas=['{a}', '{d}'],
        )
    else:
        show_translations(['{A}{a}'], trial=100, knowledge_injection_idxs=[0], do_negation=False)
        # show_translations(['{A} -> {B}'], trial=100, knowledge_injection_idxs=[0], do_negation=False)
        # show_translations(['(x): {A}x -> {B}x'], trial=100, knowledge_injection_idxs=[0], do_negation=False)
        # show_translations(['(x): {A}x -> ¬{B}x'], trial=100, knowledge_injection_idxs=[0], do_negation=False)


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
    test_templated_translator_lang('eng')


def test_jpn_katsuyou():
    """
    青臭いでないものであって一種であるもの
    """

    wb = build_wordbank('jpn')
    katsuyou = Katsuyou([
        NarabaKatsuyouRule(wb),
        NaiKatsuyouRule(wb),
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

    _check_katsuyou('この事象は起こるない', 'この事象は起こらない')
    _check_katsuyou('この事象はきれいだない', 'この事象はきれいでない')
    _check_katsuyou('この事象は走るない', 'この事象は走らない')


if __name__ == '__main__':
    setup_logger(level=logging.DEBUG)
    # test_eng()
    # test_eng_with_knowledge()
    # test_jpn()
    test_jpn_katsuyou()
