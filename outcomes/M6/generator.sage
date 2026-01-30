from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')
        y = var('y')

        # 1. Define Random Parameters
        # Function: f(x) = cbrt(x + A) + B
        
        # A = Inside shift (horizontal)
        A = choice([0, 0, 0, 1, -1, 2, -2])
        
        # B = Outside shift (vertical)
        B = randint(-5, 5)
        while B == 0:
            B = randint(-5, 5)

        # 2. Build the Original Function LaTeX
        # Handle A inside the radical
        if A == 0:
            radicand = "x"
        elif A > 0:
            radicand = f"x + {A}"
        else:
            radicand = f"x - {abs(A)}"
            
        # Handle B outside
        if B > 0:
            const_B = f"+ {B}"
        else:
            const_B = f"- {abs(B)}"
            
        equation = f"f(x) = \\sqrt[3]{{{radicand}}} {const_B}"

        # 3. Steps for Inverse
        
        # Step 1: Swap x and y
        step_swap = f"x = \\sqrt[3]{{{radicand.replace('x', 'y')}}} {const_B}"
        
        # Step 2: Isolate Radical
        # x - B = cbrt(y+A)
        K = -B
        if K > 0:
            lhs_iso = f"x + {K}"
        else:
            lhs_iso = f"x - {abs(K)}"
            
        step_isolate = f"{lhs_iso} = \\sqrt[3]{{{radicand.replace('x', 'y')}}}"
        
        # Step 3: Cube both sides
        step_cube = f"({lhs_iso})^3 = {radicand.replace('x', 'y')}"
        
        # Step 4: Solve for y (Factored)
        if A == 0:
            factored_rhs = f"({lhs_iso})^3"
        elif A > 0:
            factored_rhs = f"({lhs_iso})^3 - {A}"
        else:
            factored_rhs = f"({lhs_iso})^3 + {abs(A)}"
            
        factored_ans = f"f^{{-1}}(x) = {factored_rhs}"
        
        # 4. Expansion Steps (The "Extra" credit part)
        
        # Expansion 1: Square the binomial (x+K)^2
        k_sq = K**2
        two_k = 2*K
        
        if two_k == 0:
            quad_term = "x^2"
        elif two_k > 0:
            quad_term = f"x^2 + {two_k}x + {k_sq}"
        else:
            quad_term = f"x^2 - {abs(two_k)}x + {k_sq}"
            
        exp_step1 = f"({lhs_iso})({quad_term})"
        if A != 0:
            if A > 0: exp_step1 += f" - {A}"
            else:     exp_step1 += f" + {abs(A)}"
            
        # Expansion 2: Final Expanded Polynomial
        poly_expr = expand((x + K)**3 - A)
        expanded_ans = f"f^{{-1}}(x) = {latex(poly_expr)}"

        return {
            "equation": equation,
            "step_swap": step_swap,
            "step_isolate": step_isolate,
            "step_cube": step_cube,
            "step_solve": f"y = {factored_rhs}",
            "factored_ans": factored_ans,
            "exp_step1": exp_step1,
            "expanded_ans": expanded_ans
        }