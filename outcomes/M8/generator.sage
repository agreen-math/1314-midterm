from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')

        # 1. Define Functions
        # f(x) = ax (Linear monomial)
        # g(x) = cx^2 + d (Quadratic binomial)
        
        a = randint(2, 6) * choice([-1, 1])
        c = randint(2, 5) * choice([-1, 1])
        d = randint(1, 9) * choice([-1, 1])
        
        f_expr = a * x
        g_expr = c * x**2 + d
        
        f_tex = f"f(x) = {latex(f_expr)}"
        g_tex = f"g(x) = {latex(g_expr)}"

        # --- Part A Logic ---
        # Correct: f(g(x))
        fog_sub = f"{a}({latex(g_expr)})"
        fog_final = expand(f_expr.subs(x=g_expr))
        
        # Error 1: g(f(x)) - Switched
        gof_sub = f"{c}({latex(f_expr)})^2"
        if d > 0: gof_sub += f" + {d}"
        else:     gof_sub += f" - {abs(d)}"
        
        sq_term = (a*x)**2
        gof_inter = f"{c}({latex(sq_term)})"
        if d > 0: gof_inter += f" + {d}"
        else:     gof_inter += f" - {abs(d)}"
        
        gof_final = expand(g_expr.subs(x=f_expr))
        
        # Error 2: Multiplication f(x)*g(x)
        mult_sub = f"({latex(f_expr)})({latex(g_expr)})"
        mult_final = expand(f_expr * g_expr)

        # --- Part B Logic ---
        # Correct: f(f(x))
        fof_sub = f"{a}({latex(f_expr)})"
        fof_final = expand(f_expr.subs(x=f_expr))

        return {
            "f_tex": f_tex,
            "g_tex": g_tex,
            # Part A
            "fog_sub": fog_sub,
            "fog_final": latex(fog_final),
            "gof_sub": gof_sub,
            "gof_inter": gof_inter,
            "gof_final": latex(gof_final),
            "mult_sub": mult_sub,
            "mult_final": latex(mult_final),
            # Part B
            "fof_sub": fof_sub,
            "fof_final": latex(fof_final),
        }