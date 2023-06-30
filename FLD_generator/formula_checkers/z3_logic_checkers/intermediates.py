from typing import Optional, Tuple, Any, Union
import re

from FLD_generator.formula import (
    Formula,
    IMPLICATION,
    CONJUNCTION,
    DISJUNCTION,
    NEGATION,
    DERIVE,
    CONTRADICTION,
)

I_IMPLICATION = IMPLICATION
I_AND = CONJUNCTION
I_OR = DISJUNCTION
I_NEGATION = NEGATION
I_UNIVERSAL = 'ForAll'
I_EXISTS = 'Exists'

_FLD_to_interm = {
    IMPLICATION: I_IMPLICATION,
    CONJUNCTION: I_AND,
    DISJUNCTION: I_OR,
    NEGATION: I_NEGATION,
}


def _find_brace_content(rep: str) -> str:
    if not rep.startswith('('):
        raise ValueError()
    level = 1
    i_char = 1
    rep_in_braces = '('
    while level > 0:
        char = rep[i_char]

        if char == '(':
            level += 1
        if char == ')':
            level -= 1

        rep_in_braces += char
        i_char += 1
    return rep_in_braces[1:-1]


def parse(formula_rep: str,
          return_position=False,
          only_next_element=False) -> Union[str, Tuple, Tuple[str, int], Tuple[Tuple, int]]:

    if formula_rep.find(DERIVE) > 0:
        raise Exception()

    def head_is_connective(rep: str) -> bool:
        return any(tail_rep.startswith(op_rep)
                   for op_rep in [IMPLICATION, CONJUNCTION, DISJUNCTION, NEGATION])

    def head_is_quantifier(rep: str) -> bool:
        return any(rep.startswith(quantifier)
                   for quantifier in Formula(rep).quantifiers)

    def head_is_operator(rep: str) -> bool:
        return head_is_connective(rep) or head_is_quantifier(rep)

    i_char = 0
    op: Optional[Any] = None
    left: Optional[Union[str, Tuple]] = None
    right: Optional[Union[str, Tuple]] = None
    while i_char < len(formula_rep):
        tail_rep = formula_rep[i_char:]
        tail_formula = Formula(tail_rep)

        if tail_rep.startswith(' '):
            i_char += 1
            continue

        if head_is_operator(tail_rep):

            if head_is_connective(tail_rep):
                assert op is None
                op_rep = [op_rep_ for op_rep_ in [IMPLICATION, CONJUNCTION, DISJUNCTION, NEGATION]
                          if tail_rep.startswith(op_rep_)][0]
                op = _FLD_to_interm[op_rep]
                i_char += len(op_rep)

                operand_rep = formula_rep[i_char:]
                while operand_rep[0] == ' ':
                    operand_rep = operand_rep[1:]
                    i_char += 1

                operand_parsed, j_char = parse(operand_rep,
                                               return_position=True,
                                               only_next_element=True)
                i_char += j_char

            elif head_is_quantifier(tail_rep):
                univ_vars = tail_formula.universal_variables
                exist_vars = tail_formula.existential_variables

                if len(univ_vars) == 1:
                    op = (I_UNIVERSAL, univ_vars[0].rep)
                elif len(exist_vars) == 1:
                    op = (I_EXISTS, exist_vars[0].rep)
                else:
                    raise NotImplementedError()

                operand_rep = tail_formula.wo_quantifier.rep
                i_char += tail_formula.rep.find(operand_rep)

                operand_parsed, j_char = parse(operand_rep,
                                               return_position=True)
                i_char += j_char

            else:
                raise Exception()

            assert right is None
            if left is not None:
                left = (op, left, operand_parsed)
                op = None
            else:
                left = (op, operand_parsed, None)
                op = None

        else:

            if tail_rep.startswith('('):
                operand_rep = _find_brace_content(tail_rep)
                i_char += 2  # 2 for braces

                operand_parsed, j_char = parse(operand_rep,
                                               return_position=True)
                i_char += j_char

            else:
                operand_rep = tail_rep.split(' ')[0]
                operand_parsed = operand_rep
                i_char += len(operand_rep)

            if left is None:
                left = operand_parsed
            else:
                right = operand_parsed

        if only_next_element and\
                (op is None and left is not None and right is None):
            break

    if op is None:
        assert left is not None and right is None
        ret = left
    else:
        ret = (op, left, right)

    if return_position:
        return ret, i_char
    else:
        return ret
