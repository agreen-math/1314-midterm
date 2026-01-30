from sage.all import *
from random import choice

class Generator(BaseGenerator):
    def data(self):
        x = var("x")
        
        # 1. Setup problem for discriminant = -12
        # Roots will be h +/- i*sqrt(3)
        h = choice([-5, -4, -3, -2, 2, 3, 4, 5])
        
        # Coefficients
        a = 1
        b = -2 * h
        c = h**2 + 3
        
        # 2. Prepare values for display
        neg_b = -b
        b_sq = b**2
        four_ac = 4 * a * c
        discriminant = b_sq - four_ac  # Always -12
        denom = 2 * a
        
        # 3. Build the LaTeX steps
        
        # Step 1: Substitution
        step1 = f"x = \\frac{{-({b}) \\pm \\sqrt{{({b})^2 - 4({a})({c})}}}}{{2({a})}}"
        
        # Step 2: Simplify numbers
        step2 = f"= \\frac{{{neg_b} \\pm \\sqrt{{{b_sq} - {four_ac}}}}}{{{denom}}}"
        
        # Step 3: Subtraction inside radical
        step3 = f"= \\frac{{{neg_b} \\pm \\sqrt{{{discriminant}}}}}{{{denom}}}"
        
        # Step 4: Convert negative radical to imaginary
        step4 = f"= \\frac{{{neg_b} \\pm 2i\\sqrt{{3}}}}{{{denom}}}"
        
        # Step 5: Factor out the 2
        step5 = f"= \\frac{{{2}({h} \\pm i\\sqrt{{3}})}}{{{denom}}}"
        
        # Step 6: Final Answer (reduced)
        final_ans = f"{h} \\pm i\\sqrt{{3}}"

        equation = latex(a*x**2 + b*x + c == 0)

        return {
            "equation": equation,
            "step1": step1,
            "step2": step2,
            "step3": step3,
            "step4": step4,
            "step5": step5,
            "final_ans": final_ans,
        }