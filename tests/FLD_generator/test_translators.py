from typing import List, Optional
import logging
import sys

from FLD_generator.formula import Formula, negate, eliminate_double_negation
from FLD_generator.translators import build as build_translator, TemplatedTranslator
from FLD_generator.word_banks import build_wordbank
from FLD_generator.utils import fix_seed
from FLD_generator.knowledge_banks import build_knowledge_bank
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

    knowledge_bank = build_knowledge_bank(
        'atomic_if_then',
        './res/knowledge/knowledge-kg-completion/data/atomic/test.txt',
        max_statements=100,
    )

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
        knowledge_bank=knowledge_bank,
    )

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
                for formula, (_, translation, _, is_knowledge_injected) in zip(_formulas, translations):
                    print(formula.rep, f'(int={intermediate_constant_formulas})', '  ->  ', translation, f'is_knowledge_injected={is_knowledge_injected}')
            sys.stdout.flush()

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

    show_translations(['{A}'], trial=30, knowledge_injection_idxs=[0])

    show_translations(['{A}{a} -> {B}{a}'], trial=30, knowledge_injection_idxs=[0], do_negation=False)
    show_translations(['{A}{a} -> {B}{b}'], trial=30, knowledge_injection_idxs=[0], do_negation=False)
    show_translations(['(x): {A}x -> {B}x'], trial=30, knowledge_injection_idxs=[0], do_negation=False)


if __name__ == '__main__':
    test_templated_translator_lang('eng')
    test_templated_translator_lang('jpn')
