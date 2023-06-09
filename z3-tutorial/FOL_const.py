"""
[Predicate Logic Verification using Z3](https://www.youtube.com/watch?v=jMrQWB_eSyQ)
"""
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
a = Const('a', Object)

a1 = ForAll(x, Not(B(x)))
a2 = B(x)

solver = Solver()
solver.add(a1, a2)

is_sat = solver.check() == sat
if is_sat:
    m = solver.model()
else:
    m = None

print(is_sat)
print(m)
