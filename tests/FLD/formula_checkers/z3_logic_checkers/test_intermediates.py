from FLD_generator.formula_checkers.z3_logic_checkers.intermediates import (
    _find_brace_content,
    parse,
)


def test_find_brace_content():
    assert _find_brace_content('(hoge)piyo') == 'hoge'
    assert _find_brace_content('(hoge(fuga)piyo)tau') == 'hoge(fuga)piyo'


def test_parse():

    def _test_parse(rep: str, gold):
        print('\n\n============ _test_parse() ============')
        parsed = parse(rep)

        print('\n------------ rep ------------')
        print(rep)

        print('\n------------ gold ------------')
        print(gold)

        print('\n------------ parsed ------------')
        print(parsed)

        assert parsed == gold

    _test_parse(
        '{A}{a}',
        '{A}{a}',
    )

    _test_parse(
        '¬¬{A}{a}',
        ('¬', ('¬', '{A}{a}', None), None),
    )

    _test_parse(
        '{A}{a} v {B}{b}',
        ('v', '{A}{a}', '{B}{b}'),
    )

    _test_parse(
        '¬({A}{a} v {B}{b})',
        ('¬', ('v', '{A}{a}', '{B}{b}'), None),
    )

    _test_parse(
        '({A}{a} v {B}{b}) -> {C}{c}',
        ('->', ('v', '{A}{a}', '{B}{b}'), '{C}{c}'),
    )

    _test_parse(
        '({A}{a} v ({B}{b} v {C}{c})) -> {D}{d}',
        ('->', ('v', '{A}{a}', ('v', '{B}{b}', '{C}{c}')), '{D}{d}'),
    )

    _test_parse(
        '(x): ({A}x v {B}x) -> {C}x',
        (('ForAll', 'x'), ('->', ('v', '{A}x', '{B}x'), '{C}x'), None),
    )

    _test_parse(
        '¬((x): ({A}x v {B}x) -> {C}x)',
        ('¬', (('ForAll', 'x'), ('->', ('v', '{A}x', '{B}x'), '{C}x'), None), None),
    )

    _test_parse(
        '{A} & {B} v {C}',
        ('v', ('&', '{A}', '{B}'), '{C}'),
    )

    _test_parse(
        '{A} & ({B} v {C})',
        ('&', '{A}', ('v', '{B}', '{C}')),
    )

    _test_parse(
        '{A} & ¬({B} v {C})',
        ('&', '{A}', ('¬', ('v', '{B}', '{C}'), None)),
    )

    _test_parse(
        '{A} & ¬(¬({B} & {D}) v {C})',
        ('&', '{A}', ('¬', ('v', ('¬', ('&', '{B}', '{D}'), None), '{C}'), None)),
    )

    _test_parse(
        '{A} & ¬({B} & {D}) v {C}',
        ('v', ('&', '{A}', ('¬', ('&', '{B}', '{D}'), None)), '{C}'),
    )

    _test_parse(
        '{A} & ({B} v {C}) & {D}',
        ('&', ('&', '{A}', ('v', '{B}', '{C}')), '{D}'),
    )

    _test_parse(
        '(¬{A} & ¬{B}) -> ¬{FR}',
        ('->', ('&', ('¬', '{A}', None), ('¬', '{B}', None)), ('¬', '{FR}', None)),
    )

    _test_parse(
        '({A} v ({B} v {C})) -> {D}',
        ('->', ('v', '{A}', ('v', '{B}', '{C}')), '{D}'),
    )

    _test_parse(
        '¬{FR} -> ¬({GP} & {CT})',
        ('->', ('¬', '{FR}', None), ('¬', ('&', '{GP}', '{CT}'), None)),
    )

    _test_parse(
        ' ( {A} & {B} ) ',
        ('&', '{A}', '{B}'),
    )


if __name__ == '__main__':
    test_find_brace_content()
    test_parse()
