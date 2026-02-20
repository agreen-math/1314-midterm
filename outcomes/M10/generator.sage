from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')

        # 1. Setup "Nice" Fraction Arithmetic
        denom = choice([2, 2, 4])
        sign = choice([-1, 1])
        
        a = sign * Rational(1) / denom
        
        # 2. Pick Integer Parameters
        if denom == 4:
            step = 2
        else:
            step = denom
            
        # Ensure h is non-zero
        h = 0
        while h == 0:
            h = randint(-3, 3) * step
            
        # d determines the horizontal distance from the vertex to the x-intercepts.
        # Since d >= 1 * step, d is never 0.
        d = randint(1, 3) * step 
        
        # Calculate k. Since 'a' and 'd' are non-zero, 'k' is guaranteed to be non-zero.
        k_val = -a * (d**2)
        k = Integer(k_val)
        
        # 3. Define Function
        f_expr = a * (x - h)**2 + k
        
        # Format "a" string
        a_tex = f"\\frac{{1}}{{{denom}}}" if sign == 1 else f"-\\frac{{1}}{{{denom}}}"
            
        # Format Vertex Form LaTeX
        # (The h == 0 check will technically never trigger now, but left intact for safety)
        if h == 0:
            term_inner = "x"
            term_sq = "x^2"
            f_tex = f"f(x) = {a_tex}x^2 {k:+d}"
        else:
            op = "+" if h < 0 else "-"
            term_inner = f"x {op} {abs(h)}"
            term_sq = f"({term_inner})^2"
            f_tex = f"f(x) = {a_tex}{term_sq} {k:+d}"

        # 4. Answers & Steps
        
        # --- x-intercept Steps ---
        # Step 1: Set to 0
        x_step1 = f"{a_tex}{term_sq} {k:+d} = 0"
        
        # Step 2: Isolate the squared term
        # a(sq) = -k  =>  (sq) = -k/a
        # We know -k/a is exactly d^2 (positive integer)
        rhs_sq = d**2
        x_step2 = f"{term_sq} = {rhs_sq}"
        
        # Step 3: Square Root
        x_step3 = f"{term_inner} = \\pm {d}"
        
        # Step 4: Solve for x
        # x = h +/- d
        x_step4 = f"x = {h} \\pm {d}"
        
        x1 = h - d
        x2 = h + d
        if x1 < x2:
            x_ints = f"{x1}, {x2}"
        else:
            x_ints = f"{x2}, {x1}"
            
        # --- y-intercept Steps ---
        # Step 1: Plug in 0
        if h == 0:
            y_step1 = f"{a_tex}(0)^2 {k:+d}"
            sq_val = 0
        else:
            y_step1 = f"{a_tex}(0 {op} {abs(h)})^2 {k:+d}"
            sq_val = h**2
            
        # Step 2: Evaluate Square
        # (1/2)(16) - 2
        y_step2 = f"{a_tex}({sq_val}) {k:+d}"
        
        # Step 3: Multiply
        # 8 - 2
        mult_val = a * sq_val
        y_step3 = f"{mult_val} {k:+d}"
        
        y_val = f_expr.subs(x=0)
        y_int = f"{y_val}"
        
        # --- Other Properties ---
        vertex = f"({h}, {k})"
        axis = f"x = {h}"
        
        if a > 0:
            opens = "Up"
        else:
            opens = "Down"
        
        # Linter Fixes
        LP = "("
        RP = ")"
        LB = "["
        RB = "]"
        
        domain = LP + r"-\infty, \infty" + RP
        
        if a > 0:
            range_val = LB + f"{k}, \\infty" + RP
        else:
            range_val = LP + f"-\\infty, {k}" + RB

        return {
            "f_tex": f_tex,
            "vertex": vertex,
            "axis": axis,
            "x_ints": x_ints,
            "y_int": y_int,
            "domain": domain,
            "range": range_val,
            "opens": opens,
            # New Step Variables
            "x_step1": x_step1,
            "x_step2": x_step2,
            "x_step3": x_step3,
            "x_step4": x_step4,
            "y_step1": y_step1,
            "y_step2": y_step2,
            "y_step3": y_step3
        }