from typing import List, Optional, Set, Dict
import logging
import sys
import json
from collections import defaultdict
import re

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
from FLD_generator.translators.japanese.postprocessor import (
    Postprocessor,
    WindowRulesPostprocessor,
    NarabaKatsuyouRule,
    DaKaKatuyouRule,
    DaKotoMonoKatuyouRule,
    NaiKatsuyouRule,
    NaiNaiKatsuyouRule,
    ShiKatuyouRule,
    UniqueKOSOADOPostprocessor,
    ZeroAnaphoraPostprocessor,
    HaGaUsagePostprocessor,
)
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


def test_jpn_with_user_vocab(type_: str):
    if type_ == 'punipuni':
        test_templated_translator_lang('jpn',
                                       translation_config='punipuni',
                                       no_adj_verb_as_zeroary=True,
                                       extra_vocab='punipuni')
    elif type_ == 'BCCWJ':
        test_templated_translator_lang('jpn',
                                       translation_config='thing',
                                       no_adj_verb_as_zeroary=True,
                                       extra_vocab='BCCWJ')
    else:
        raise ValueError()



@profile
def test_jpn_postprocess():

    wb = build_wordbank('jpn', extra_vocab='punipuni')

    def build_test_in_out_func(postprocessors: List[Postprocessor]):

        postprocessor_chain = build_postprocessor(wb,
                                                  postprocessors=postprocessors)

        def _test_in_out(src: str, golds: List[str], trial=1000):
            print('\n\n================ test_jpn_postprocess ===================')
            print('input      :', src)
            print()
            print('expected   :', golds)

            done: Set[str] = set([])
            for _ in range(trial):
                postprocessor_chain.reset_assets()
                pred = postprocessor_chain.apply(src)
                if pred in done:
                    continue

                print()
                print('output     :', pred)
                assert pred in golds
                done.add(pred)
                if done == set(golds):
                    break

            assert done == set(golds)

        return _test_in_out





    _test_in_out = build_test_in_out_func([
        WindowRulesPostprocessor(
            [
                NarabaKatsuyouRule(wb),
            ],
            extra_vocab=wb.extra_vocab,
        ),
    ])

    _test_in_out('この人間は走るならばつらい',
                 ['この人間は走ればつらい'])

    _test_in_out('この人間は機械だならばつらい',
                 ['この人間は機械ならばつらい'])

    _test_in_out('この人間はきれいだならばつらい',
                 ['この人間はきれいならばつらい'])

    _test_in_out('この人間は美しいならばつらい',
                 ['この人間は美しいならばつらい'])

    _test_in_out('この人間は走るならつらい',
                 ['この人間は走るならつらい'])

    _test_in_out('この人間は機械だならつらい',
                 ['この人間は機械ならつらい'])

    _test_in_out('この人間はきれいだならつらい',
                 ['この人間はきれいならつらい'])

    _test_in_out('この人間は美しいならつらい',
                 ['この人間は美しいならつらい'])

    _test_in_out('この人間はぷえぷやLv.3だならばつらい',
                 ['この人間はぷえぷやLv.3ならばつらい'])

    _test_in_out('この人間はぷえぷやLv.3だならつらい',
                 ['この人間はぷえぷやLv.3ならつらい'])




    _test_in_out = build_test_in_out_func([
        WindowRulesPostprocessor(
            [
                DaKaKatuyouRule(wb),
            ],
            extra_vocab=wb.extra_vocab,
        )
    ])

    _test_in_out('この人間はきれいだか美しい',
                 ['この人間はきれいであるか美しい'])

    _test_in_out('この人間は会議だか美しい',
                 ['この人間は会議であるか美しい'])

    _test_in_out('もしこのブローチは小館花であるか菊雄だか両方ならばあのどら猫は赤い',
                 ['もしこのブローチは小館花であるか菊雄であるか両方ならばあのどら猫は赤い'])

    _test_in_out('この人間はぷえぷやLv.3だか美しい',
                 ['この人間はぷえぷやLv.3であるか美しい'])




    _test_in_out = build_test_in_out_func([
        WindowRulesPostprocessor(
            [
                DaKotoMonoKatuyouRule(wb),
            ],
            extra_vocab=wb.extra_vocab,
        )
    ])

    _test_in_out('きれいだものはある',
                 ['きれいなものはある'])

    _test_in_out('きれいだことはある',
                 ['きれいなことはある'])

    _test_in_out('「きれいだ」ものはある',
                 ['「きれいな」ものはある'])

    _test_in_out('「きれいだ」物はある',
                 ['「きれいな」物はある'])

    _test_in_out('ぷえぷやLv.3だものはある',
                 ['ぷえぷやLv.3なものはある'])

    _test_in_out('「ぷえぷやLv.3だ」モンスターはある．',
                 ['「ぷえぷやLv.3な」モンスターはある．'])



    _test_in_out = build_test_in_out_func([
        WindowRulesPostprocessor(
            [
                NaiKatsuyouRule(wb)
            ],
            extra_vocab=wb.extra_vocab,
        )
    ])

    _test_in_out('この人間は走るない',
                 ['この人間は走らない'])

    _test_in_out('この人間は美しいない',
                 ['この人間は美しくない'])

    _test_in_out('夫婦らしいない物は分厚いかあるいは忌まわしい',
                 ['夫婦らしくない物は分厚いかあるいは忌まわしい'])

    _test_in_out('剥がれ落ちるない',
                 ['剥がれ落ちない'])

    _test_in_out('この人間は機械だない',
                 ['この人間は機械でない'])

    _test_in_out('この人間は機械だないし，あの熊も機械だない',
                 ['この人間は機械でないし，あの熊も機械でない'])

    _test_in_out('Xということは成り立つない',
                 ['Xということは成り立たない'])

    _test_in_out('仕組むない',
                 ['仕組まない'])

    _test_in_out('取り扱い易いものは仕組むないし熱苦しい',
                 ['取り扱い易いものは仕組まないし熱苦しい'])

    _test_in_out('あのみやみやLv.2は聞き辛いがそれは志願するない',
                 ['あのみやみやLv.2は聞き辛いがそれは志願しない'])

    _test_in_out('何もかもは和大であるないかまたは与太る',
                 ['何もかもは和大でないかまたは与太る'])

    _test_in_out('この人間はぷえぷやLv.3だない',
                 ['この人間はぷえぷやLv.3でない'])

    _test_in_out('この人間はきれいだない',
                 ['この人間はきれいでない'])

    _test_in_out('この人間は美しいない',
                 ['この人間は美しくない'])

    _test_in_out('この人間は会議するない',
                 ['この人間は会議しない'])

    _test_in_out('「黒いということは起こらない」ということは事実と異なるない',
                 ['「黒いということは起こらない」ということは事実と異ならない'])

    _test_in_out('あのまわまちょLv.3は規定するない',
                 ['あのまわまちょLv.3は規定しない'])

    # "規定す" という動詞の活用らしい．
    _test_in_out('あのまわまちょLv.3は規定すない',
                 ['あのまわまちょLv.3は規定すらない'])


    _test_in_out = build_test_in_out_func([
        WindowRulesPostprocessor(
            [
                NaiNaiKatsuyouRule(wb),
            ],
            extra_vocab=wb.extra_vocab,
        )
    ])

    _test_in_out('この人間は走らないない',
                 ['この人間は走らなくない'])

    _test_in_out('この人間は機械でないない',
                 ['この人間は機械でなくない'])

    _test_in_out('この人間はきれいでないない',
                 ['この人間はきれいでなくない'])

    _test_in_out('この人間は美しくないない',
                 ['この人間は美しくなくない'])

    _test_in_out('この人間はぷえぷやLv.3でないない',
                 ['この人間はぷえぷやLv.3でなくない'])




    _test_in_out = build_test_in_out_func([
        WindowRulesPostprocessor(
            [
                ShiKatuyouRule(wb),
            ],
            extra_vocab=wb.extra_vocab,
        )
    ])

    _test_in_out('この人間は美しいし赤い',
                 ['この人間は美しいし赤い', 'この人間は美しくて赤い'])

    _test_in_out('この人間はきれいだし赤い',
                 ['この人間はきれいだし赤い', 'この人間はきれいで赤い'])

    _test_in_out('この人間はぷえぷやLv.3だし赤い',
                 ['この人間はぷえぷやLv.3だし赤い', 'この人間はぷえぷやLv.3で赤い'])

    _test_in_out('あのぷちゃぷにLv.66は切除するしかつ思い付く',
                 ['あのぷちゃぷにLv.66は切除するしかつ思い付く'])

    



    _test_in_out = build_test_in_out_func([
        UniqueKOSOADOPostprocessor(extra_vocab=wb.extra_vocab),
    ])

    _test_in_out(
        'この人間とあの人間とその人間とこの熊とあの熊とその熊',
        [f'{ningen_kosoado}人間と{ningen_kosoado}人間と{ningen_kosoado}人間と{kuma_kosoado}熊と{kuma_kosoado}熊と{kuma_kosoado}熊'
         for ningen_kosoado in ['この', 'あの', 'その']
         for kuma_kosoado in ['この', 'あの', 'その']]
    )




    _test_in_out = build_test_in_out_func([
        ZeroAnaphoraPostprocessor(extra_vocab=wb.extra_vocab),
    ])

    _test_in_out('きつねが赤ければそれは走る',
                 ['きつねが赤ければそれは走る', 'きつねが赤ければ走る'])




    _test_in_out = build_test_in_out_func([
      HaGaUsagePostprocessor(extra_vocab=wb.extra_vocab),
    ])

    _test_in_out('きつねが赤ければそれが走る',
                 ['きつねが赤ければそれは走る'])

    _test_in_out('きつねが赤ければそれは走る',
                 ['きつねが赤ければそれは走る'])

    _test_in_out('きつねは赤ければそれが走る',
                 ['きつねが赤ければそれは走る'])

    _test_in_out('きつねは赤ければそれは走る',
                 ['きつねが赤ければそれは走る'])

    _test_in_out('「きつねが赤ければそれが走る」が成り立つが，「たぬきが赤ければそれが走る」が成り立たない',
                 ['「きつねが赤ければそれは走る」が成り立つが，「たぬきが赤ければそれは走る」は成り立たない'])

    # ------------- same 「は/が」 before and after "&" ----------
    _test_in_out('あのぷやぷやLv.3が歩くしそれが走る',
                 ['あのぷやぷやLv.3は歩くしそれは走る'])

    _test_in_out('あのぷやぷやLv.3が赤いしそれが走る',
                 ['あのぷやぷやLv.3は赤いしそれは走る'])

    _test_in_out('あのぷやぷやLv.3が電撃でそれが走る',
                 ['あのぷやぷやLv.3は電撃でそれは走る'])

    _test_in_out('あのぷやぷやLv.3が歩いてそれが走る',
                 ['あのぷやぷやLv.3は歩いてそれは走る'])

    _test_in_out('あのぷやぷやLv.3が赤くてそれが走る',
                 ['あのぷやぷやLv.3は赤くてそれは走る'])

    _test_in_out('あのぷやぷやLv.3が電撃でそれが走る',
                 ['あのぷやぷやLv.3は電撃でそれは走る'])

    _test_in_out('あのぷやぷやLv.3が歩かないしそれが走る',
                 ['あのぷやぷやLv.3は歩かないしそれは走る'])

    _test_in_out('あのぷやぷやLv.3が赤くないしそれが走る',
                 ['あのぷやぷやLv.3は赤くないしそれは走る'])

    _test_in_out('あのぷやぷやLv.3が電撃でないしそれが走る',
                 ['あのぷやぷやLv.3は電撃でないしそれは走る'])

    _test_in_out('あのぷやぷやLv.3が歩かなくてそれが走る',
                 ['あのぷやぷやLv.3は歩かなくてそれは走る'])

    _test_in_out('あのぷやぷやLv.3が赤くなくてそれが走る',
                 ['あのぷやぷやLv.3は赤くなくてそれは走る'])

    _test_in_out('あのぷやぷやLv.3が電撃でなくてそれが走る',
                 ['あのぷやぷやLv.3は電撃でなくてそれは走る'])

    _test_in_out('狸が踊るし猫が走る',
                 ['狸は踊るし猫は走る'])

    _test_in_out('もしこのブローチは小館花であるか菊雄であるか両方ならばあのどら猫は赤い',
                 ['もしこのブローチが小館花であるか菊雄であるか両方ならばあのどら猫は赤い'])

    _test_in_out('このみわみのLv.15がむず痒くないがそれは取り辛い',
                 ['このみわみのLv.15はむず痒くないがそれは取り辛い'])
    
    _test_in_out('もし仮にこのぽえぽのLv.92は変わり易いとすれば散る',
                 ['もし仮にこのぽえぽのLv.92は変わり易いとすれば散る'])

    _test_in_out('このぽちゃぽえLv.80が渋くないけれどそれは赤っぽい',
                 ['このぽちゃぽえLv.80は渋くないけれどそれは赤っぽい'])

    _test_in_out('このぽちゃぽえLv.80が渋くないけどそれは赤っぽい',
                 ['このぽちゃぽえLv.80は渋くないけどそれは赤っぽい'])

    _test_in_out('このぽちゃぽえLv.80がモンスターでありそれは赤い',
                 ['このぽちゃぽえLv.80はモンスターでありそれは赤い'])

    _test_in_out('あのみなみちゅLv.62は上がり難いということはないしかつ腹黒い',
                 ['あのみなみちゅLv.62は上がり難いということはないしかつ腹黒い'])

    _test_in_out('ぴのぴちゅLv.10事件かまたは両方ともは生じる',
                 ['ぴのぴちゅLv.10事件かまたは両方ともは生じる'])

    _test_in_out('もにゃもちょLv.30事件が起きるかまたはみゆみよLv.38事件は起こる',
                 ['もにゃもちょLv.30事件が起きるかまたはみゆみよLv.38事件は起こる'])

    _test_in_out('みわみちゃLv.46事件が起こるししかもまえまにゅLv.2事件は起きる',
                 ['みわみちゃLv.46事件が起こるししかもまえまにゅLv.2事件は起きる'])
   
    _test_in_out('もし仮にあのみわみちょLv.49は掲載するし言い難いとすればそのみやみいLv.94は思い出深い',
                 ['もし仮にあのみわみちょLv.49が掲載するし言い難いとすればそのみやみいLv.94は思い出深い'])

    _test_in_out('もしもそのまのまゆLv.85が作り易いとしたらそれは喋り捲る',
                 ['もしもそのまのまゆLv.85が作り易いとしたらそれは喋り捲る'])

    _test_in_out('もし仮になにがしかのモンスターは恐怖すればそれは感染し易い',
                 ['もし仮になにがしかのモンスターが恐怖すればそれは感染し易い'])

    _test_in_out('もし私らしくないモンスターは付き易いとしたらそれは読み出せる',
                 ['もし私らしくないモンスターが付き易いとしたらそれは読み出せる'])

    _test_in_out('仮にど偉いか書き難いかまたは両方であるモンスターはいるならそのぴくぴいLv.78は伸び易くない',
                 ['仮にど偉いか書き難いかまたは両方であるモンスターがいるならそのぴくぴいLv.78は伸び易くない'])


if __name__ == '__main__':
    setup_logger(level=logging.DEBUG)

    # test_eng()
    # test_eng_with_knowledge()

    # test_jpn()
    # test_jpn_with_user_vocab('punipuni')
    # test_jpn_with_user_vocab('BCCWJ')

    test_jpn_postprocess()
