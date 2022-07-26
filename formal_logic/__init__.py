from .replacements import (
    generate_replacement_mappings,
    generate_replacement_mappings_from_formula,
    generate_replacement_mappings_from_terms,
    generate_replaced_formulas,
    generate_replaced_arguments,
    replace_formula,
    replace_argument,
    replace_rep,
)
from .formula import Formula, Argument, detemplatify, templatify, is_satisfiable
from .generation import generate_tree
