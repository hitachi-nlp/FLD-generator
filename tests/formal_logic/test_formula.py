from typing import List
from formal_logic.formula import Formula


def test_formula():
    assert {f.rep for f in Formula('{A}{a} -> {B}{b} v {C}x v {D}').predicates} == {'{A}', '{B}', '{C}', '{D}'}
    assert {f.rep for f in Formula('{A}{a} -> {B}{b} v {C}x v {D}').constants} == {'{a}', '{b}'}
    assert {f.rep for f in Formula('{A}{a} -> {B}{b} v {C}x v {D}').variables} == {'x'}
    assert {f.rep for f in Formula('{A}{a} -> {B}{b} v {C}x v {D}').PASs} == {'{A}{a}', '{B}{b}', '{C}x', '{D}'}

    assert {f.rep for f in Formula('(x): {A}x -> {B}x').universal_variables} == {'x'}
    assert {f.rep for f in Formula('(Ex): {A}x -> {B}x').existential_variables} == {'x'}


if __name__ == '__main__':
    test_formula()
