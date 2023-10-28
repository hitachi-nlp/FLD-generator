from FLD_generator.formula import Formula
from FLD_generator.knowledge_banks.formula import get_type_fml, FormulaType


def test_get_type_fml():

    def test(formula_rep: str, type_: FormulaType):
        assert get_type_fml(Formula(formula_rep), allow_others=True) == type_

    test('{F}', FormulaType.F)
    test('({F})', FormulaType.F)
    test('¬{F}', FormulaType.nF)
    test('(¬{F})', FormulaType.nF)
    test('¬({F})', FormulaType.nF)

    test('{F}{a}', FormulaType.Fa)
    test('({F}{a})', FormulaType.Fa)
    test('¬{F}{a}', FormulaType.nFa)
    test('(¬{F}{a})', FormulaType.nFa)
    test('¬({F}{a})', FormulaType.nFa)

    test('(x): {F}x', FormulaType.Fx)
    test('((x): {F}x)', FormulaType.Fx)
    test('(x): ¬{F}x', FormulaType.nFx)
    test('((x): ¬{F}x)', FormulaType.nFx)
    test('¬((x): {F}x)', FormulaType.OTHERS)

    test('{F} -> {G}', FormulaType.F_G)
    test('({F} -> {G})', FormulaType.F_G)
    test('¬{F} -> {G}', FormulaType.nF_G)
    test('{F} -> ¬{G}', FormulaType.F_nG)
    test('¬{F} -> ¬{G}', FormulaType.nF_nG)

    test('{F}{a} -> {G}{a}', FormulaType.Fa_Ga)
    test('({F}{a} -> {G}{a})', FormulaType.Fa_Ga)
    test('¬{F}{a} -> {G}{a}', FormulaType.nFa_Ga)
    test('{F}{a} -> ¬{G}{a}', FormulaType.Fa_nGa)
    test('¬{F}{a} -> ¬{G}{a}', FormulaType.nFa_nGa)

    test('{F}{a} -> {G}{b}', FormulaType.Fa_Gb)
    test('({F}{a} -> {G}{b})', FormulaType.Fa_Gb)
    test('¬{F}{a} -> {G}{b}', FormulaType.nFa_Gb)
    test('{F}{a} -> ¬{G}{b}', FormulaType.Fa_nGb)
    test('¬{F}{a} -> ¬{G}{b}', FormulaType.nFa_nGb)

    test('(x): {F}x -> {G}x', FormulaType.Fx_Gx)
    test('((x): {F}x -> {G}x)', FormulaType.Fx_Gx)
    test('(x): ¬{F}x -> {G}x', FormulaType.nFx_Gx)
    test('(x): {F}x -> ¬{G}x', FormulaType.Fx_nGx)
    test('(x): ¬{F}x -> ¬{G}x', FormulaType.nFx_nGx)

    test('(x): {F}x -> {G}y', FormulaType.Fx_Gy)
    test('((x): {F}x -> {G}y)', FormulaType.Fx_Gy)
    test('(x): ¬{F}x -> {G}y', FormulaType.nFx_Gy)
    test('(x): {F}x -> ¬{G}y', FormulaType.Fx_nGy)
    test('(x): ¬{F}x -> ¬{G}y', FormulaType.nFx_nGy)


if __name__ == '__main__':
    test_get_type_fml()
