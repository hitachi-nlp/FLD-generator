from z3 import (
    Bools,
    Solver,
    Not,
    Or,
    Implies,
    is_true,
    sat,
)

x1, x2, x3 = Bools("x1 x2 x3")

s = Solver()

P1 = Or(x1, Not(x2))  # x1 ∨ ¬x2
P2 = x3
P3 = Or(Not(x1), Not(x2))  # ¬x1 ∨ ¬x2

s.add(P1, P2, P3)  # [x1 ∨ ¬x2, x3, ¬x1 ∨ ¬x2]

c = s.check()  # sat
if c == sat:
    m = s.model()  # [x3 = True, x2 = False, x1 = False]
else:
    m = None

for x in [x1, x2, x3]:
    print(x, is_true(x))
