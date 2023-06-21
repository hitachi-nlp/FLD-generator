"""
[Predicate Logic Verification using Z3](https://www.youtube.com/watch?v=jMrQWB_eSyQ)
"""
from collections import defaultdict

from z3 import (
    DeclareSort,
    Function,
    BoolSort,
    Const,
    sat,
    is_true,

    Implies,
    And,
    Or,
    Not,
    ForAll,
    Exists,
    Solver,
)

Object = DeclareSort('Object')

B = Function('Book', Object, BoolSort())
G = Function('Gaseous', Object, BoolSort())
D = Function('Dictionary', Object, BoolSort())

x = Const('x', Object)

a1 = Not(Exists(x, And(B(x), G(x))))
a2 = ForAll(x, Implies(D(x), B(x)))
concl = Exists(x, And(D(x), G(x)))
neg_concl = Not(concl)

solver = Solver()
solver.add(a1, a2, neg_concl)

is_sat = solver.check() == sat
if is_sat:
    m = solver.model()
else:
    m = None

print(is_sat)
print(m)
