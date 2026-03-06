from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')
        y = var('y')

        # 1. Define Random Parameters
        A = randint(-5, 5)
        while A == 0:
            A = randint(-5, 5)
        
        B = randint(-5, 5)
        while B == 0:
            B = randint(-5, 5)

        # 2. Build the Original Function LaTeX
        if A > 0:
            radicand = f"x + {A}"
        else:
            radicand = f"x - {abs(A)}"
            
        if B > 0:
            const_B = f"+ {B}"
        else:
            const_B = f"- {abs(B)}"
            
        equation_rhs = f"\\sqrt[3]{{{radicand}}} {const_B}"
        equation = f"f(x) = {equation_rhs}"

        # 3. Steps for Inverse
        step_swap = f"x = \\sqrt[3]{{{radicand.replace('x', 'y')}}} {const_B}"
        
        K = -B
        if K > 0:
            lhs_iso = f"x + {K}"
        else:
            lhs_iso = f"x - {abs(K)}"
            
        step_isolate = f"{lhs_iso} = \\sqrt[3]{{{radicand.replace('x', 'y')}}}"
        step_cube = f"({lhs_iso})^3 = {radicand.replace('x', 'y')}"
        
        if A > 0:
            factored_rhs = f"({lhs_iso})^3 - {A}"
        else:
            factored_rhs = f"({lhs_iso})^3 + {abs(A)}"
            
        factored_ans = f"f^{{-1}}(x) = {factored_rhs}"
        
        # 4. Expansion Steps
        k_sq = K**2
        two_k = 2*K
        
        if two_k > 0:
            quad_term = f"x^2 + {two_k}x + {k_sq}"
        else:
            quad_term = f"x^2 - {abs(two_k)}x + {k_sq}"
            
        exp_step1 = f"({lhs_iso})({quad_term})"
        if A > 0: 
            exp_step1 += f" - {A}"
        else:     
            exp_step1 += f" + {abs(A)}"
            
        poly_expr = expand((x + K)**3 - A)
        expanded_ans = f"f^{{-1}}(x) = {latex(poly_expr)}"

        return {
            "equation": equation,
            "equation_rhs": equation_rhs,
            "step_swap": step_swap,
            "step_isolate": step_isolate,
            "step_cube": step_cube,
            "step_solve": f"y = {factored_rhs}",
            "factored_ans": factored_ans,
            "exp_step1": exp_step1,
            "expanded_ans": expanded_ans
        }