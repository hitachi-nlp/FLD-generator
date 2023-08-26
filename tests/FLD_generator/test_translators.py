from typing import List, Optional
import logging
import sys

from FLD_generator.formula import Formula, negate, eliminate_double_negation
from FLD_generator.translators import build as build_translator
from FLD_generator.word_banks import build_wordbank
from FLD_generator.utils import fix_seed
from logger_setup import setup as setup_logger

fix_seed(0)


def test_templated_translator_lang(lang: str):
    setup_logger(level=logging.DEBUG)

    # word_bank = None
    word_bank = build_wordbank(lang)

    if lang == 'eng':
        translation_config_dir = './configs/translations/eng/thing.v1/'
    elif lang == 'jpn':
        translation_config_dir = './configs/translations/jpn/thing.v1/'
    else:
        raise ValueError()

    # translator = None
    translator = build_translator(
        lang,
        [translation_config_dir],
        word_bank,
        use_fixed_translation=False,
        reused_object_nouns_max_factor=1.0,
        limit_vocab_size_per_type=None,
        # volume_to_weight='sqrt',
        volume_to_weight='logE',
        default_weight_factor_type='W_VOL__1.0',
        adj_verb_noun_ratio='1-1-1',
    )

    def show_translations(formulas: List[Formula],
                          trial=5,
                          intermediate_constant_formulas: Optional[List[Formula]] = None) -> None:
        for type_ in ['posi', 'neg']:
            if type_ == 'posi':
                _formulas = formulas
            elif type_ == 'neg':
                _formulas = [eliminate_double_negation(negate(formula)) for formula in formulas]
            print('\n\n\n================   translation  ================')
            for i_trial in range(0, trial):
                if len(formulas) >= 2:
                    print('')
                translations, _ = translator.translate(_formulas, intermediate_constant_formulas or [])
                for formula, (_, translation, _) in zip(_formulas, translations):
                    print(formula.rep, f'(int={intermediate_constant_formulas})', '  ->  ', translation)
            sys.stdout.flush()

    show_translations([Formula('{A}')], trial=30)
    show_translations([Formula('¬{A}')], trial=30)
    show_translations([Formula('¬({A})')], trial=30)

    show_translations([Formula('(¬{A} & {B})')], trial=30)
    show_translations([Formula('(¬{A} v {B})')], trial=30)

    show_translations([Formula('{A} -> {B}')], trial=30)
    show_translations([Formula('¬{A} -> {B}')], trial=30)
    show_translations([Formula('{A} -> ¬{B}')], trial=30)
    show_translations([Formula('({A} & {B}) -> {C}')], trial=30)
    show_translations([Formula('({A} v {B}) -> {C}')], trial=30)
    show_translations([Formula('{A} -> ({B} & {C})')], trial=30)
    show_translations([Formula('{A} -> ({B} v {C})')], trial=30)


    show_translations([Formula('{A}{a}')], trial=30)
    show_translations([Formula('¬{A}{a}')], trial=30)

    show_translations([Formula('(¬{A}{a} & {B}{a})')], trial=30)
    show_translations([Formula('(¬{A}{a} v {B}{a})')], trial=30)

    show_translations([Formula('({A}{a} -> {B}{a})')], trial=30)
    show_translations([Formula('(¬{A}{a} -> {B}{a})')], trial=30)
    show_translations([Formula('({A}{a} -> ¬{B}{a})')], trial=30)
    show_translations([Formula('({A}{a} & {B}{a}) -> {C}{c}')], trial=30)
    show_translations([Formula('({A}{a} v {B}{a}) -> {C}{c}')], trial=30)
    show_translations([Formula('{A}{a} -> ({B}{b} & {C}{b})')], trial=30)
    show_translations([Formula('{A}{a} -> ({B}{b} v {C}{b})')], trial=30)


    show_translations([Formula('(Ex): {A}x')], trial=30)
    show_translations([Formula('(Ex): (¬{A}x & {B}x)')], trial=30)
    show_translations([Formula('(Ex): (¬{A}x v {B}x)')], trial=30)
    show_translations([Formula('(Ex): {A}x -> {B}x')], trial=30)
    show_translations([Formula('(Ex): (¬{A}x & {B}x) -> {C}x')], trial=30)
    show_translations([Formula('(Ex): (¬{A}x v {B}x) -> {C}x')], trial=30)

    show_translations([Formula('(x): {A}x')], trial=30)
    show_translations([Formula('(x): (¬{A}x & {B}x)')], trial=30)
    show_translations([Formula('(x): (¬{A}x v {B}x)')], trial=30)
    show_translations([Formula('(x): {A}x -> {B}x')], trial=30)
    show_translations([Formula('(x): (¬{A}x & {B}x) -> {C}x')], trial=30)
    show_translations([Formula('(x): (¬{A}x v {B}x) -> {C}x')], trial=30)




    # multiple formulas
    show_translations(
        [
            Formula('{A}{a} -> {B}{b}'),
            Formula('{B}{b} -> {C}{c}'),
            Formula('{C}{c} -> {D}{d}'),
        ],
        5
    )

    show_translations(
        [
            Formula('{A}'),
            Formula('{B}'),
            Formula('{C}'),
            Formula('{D}{d}'),
            Formula('{E}{e}'),
            Formula('{F}{f}'),
        ],
        5,
    )

    show_translations(
        [
            Formula('(x): {A}x -> {B}x'),
            Formula('(x): {B}x -> {C}x'),
            Formula('(x): {C}x -> {D}x'),
        ],
        5,
    )

    show_translations(
        [
            Formula('{A}{a} -> {B}{b}'),
            Formula('{C}{c} -> {D}{d}'),
            Formula('{F}{f} -> {G}{g}'),
        ],
        5,
        intermediate_constant_formulas=[Formula('{a}'), Formula('{d}')],
    )


if __name__ == '__main__':
    # test_templated_translator_lang('eng')
    test_templated_translator_lang('jpn')
