from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')
        h = var('h')

        # 1. Define Function parameters
        # f(x) = ax^2 + b
        # Constraint: a is positive, b is nonzero
        a = randint(1, 6)
        b = randint(-9, 9)
        while b == 0:
            b = randint(-9, 9)
            
        f_expr = a * x**2 + b
        f_tex = f"f(x) = {latex(f_expr)}"

        # 2. Step-by-Step Construction
        
        # Step 1: Find f(x+h)
        step1_sub = f"{a}(x+h)^2"
        if b > 0: step1_sub += f" + {b}"
        else:     step1_sub += f" - {abs(b)}"
        
        # Step 2: Expand the binomial
        step2_expand = f"{a}(x^2 + 2xh + h^2)"
        if b > 0: step2_expand += f" + {b}"
        else:     step2_expand += f" - {abs(b)}"
        
        # Step 3: Distribute 'a'
        dist_poly = a*x**2 + 2*a*x*h + a*h**2 + b
        step3_dist = latex(dist_poly)
        
        # Step 4: Numerator Setup (show subtraction)
        step4_num_setup = f"({step3_dist}) - ({latex(f_expr)})"
        
        # Step 5: Simplify Numerator
        num_simp_poly = 2*a*x*h + a*h**2
        step5_num_simp = latex(num_simp_poly)
        
        # Step 6: Factor out h
        inner_factor = 2*a*x + a*h
        step6_factor = f"h({latex(inner_factor)})"
        
        # Step 7: Final Answer
        final_ans = latex(inner_factor)

        return {
            "f_tex": f_tex,
            "step1_sub": step1_sub,
            "step2_expand": step2_expand,
            "step3_dist": step3_dist,
            "step4_num_setup": step4_num_setup,
            "step5_num_simp": step5_num_simp,
            "step6_factor": step6_factor,
            "final_ans": final_ans
        }