from formal_logic.formula import is_consistent, Formula


def test_is_consistent():
    assert is_consistent(Formula('{F}{a}'))
    assert is_consistent(Formula('{F}{a} -> {G}{a}'))
    assert is_consistent(Formula('(x): {F}x -> {G}x'))

    assert not is_consistent(Formula('{F}{a} -> ¬{F}{a}'))
    assert not is_consistent(Formula('(x): {F}x -> ¬{F}x'))

    assert is_consistent(Formula('({F} & {G}){a}'))
    assert is_consistent(Formula('({F} & {G}){a} -> {H}{a}'))
    assert is_consistent(Formula('{F}{a} -> ({G} & {H}){a}'))
    assert is_consistent(Formula('(x): ({F} & {G})x -> {H}x'))
    assert is_consistent(Formula('(x): {F}x -> ({G} & {H})x'))

    assert not is_consistent(Formula('({F} & ¬{F}){a}'))
    assert not is_consistent(Formula('({F} & {G}){a} -> ¬{F}{a}'))
    assert not is_consistent(Formula('(¬{F} & {G}){a} -> {F}{a}'))
    assert not is_consistent(Formula('({F} & ¬{F}){a} -> {G}{a}'))
    assert not is_consistent(Formula('¬{F}{a} -> ({F} & {H}){a}'))
    assert not is_consistent(Formula('{F}{a} -> (¬{F} & {H}){a}'))
    assert not is_consistent(Formula('(x): (¬{F} & {G})x -> {F}x'))
    assert not is_consistent(Formula('(x): ¬{F}x -> ({F} & {H})x'))

    assert is_consistent(Formula('({F} v {G}){a}'))
    assert is_consistent(Formula('({F} v {G}){a} -> {H}{a}'))
    assert is_consistent(Formula('{F}{a} -> ({G} v {H}){a}'))
    assert is_consistent(Formula('(x): ({F} v {G})x -> {H}x'))
    assert is_consistent(Formula('(x): {F}x -> ({G} v {H})x'))

    assert is_consistent(Formula('({F} v ¬{F}){a}'))
    assert is_consistent(Formula('(¬{F} v {G}){a} -> {F}{a}'))
    assert is_consistent(Formula('¬{F}{a} -> ({F} v {H}){a}'))
    assert is_consistent(Formula('(x): (¬{F} v {G})x -> {F}x'))
    assert is_consistent(Formula('(x): {F}x -> (¬{F} v {H})x'))


if __name__ == '__main__':
    test_is_consistent()
