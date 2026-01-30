from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var("x")
        
        # Loop until we get a set of numbers that doesn't produce a zero numerator
        while True:
            # 1. Define distinct integer parameters
            a = Integer(randint(1, 6))
            b_val = randint(-6, 6)
            while b_val in [0, a, -a]: 
                b_val = randint(-6, 6)
            b = Integer(b_val)

            # 2. Define solutions
            x_ext = -a
            possible_valid = [i for i in range(-9, 10) if i not in [-a, -b, 0]]
            x_valid = Integer(choice(possible_valid))

            # 3. Calculate numerators
            c = b + x_ext + x_valid
            d = c * a + (x_ext * x_valid)
            
            # CHECK: If either numerator is 0, scrap it and try again.
            if c != 0 and d != 0:
                break

        # 4. Format Equation (Manual sign handling)
        if d < 0:
            sign_d = "-"
            abs_d = -d
        else:
            sign_d = "+"
            abs_d = d

        # LaTeX Strings
        denom1 = latex(x + a)
        denom_lcd = f"({latex(x + a)})({latex(x + b)})"
        denom2 = latex(x + b)

        # Note: Triple braces }}} at the end are required! 
        # (1 for the variable, 2 for the LaTeX brace)
        lhs_part1 = f"\\frac{{x}}{{{denom1}}}"
        lhs_part2 = f"\\frac{{{latex(abs_d)}}}{{{denom_lcd}}}"
        rhs = f"\\frac{{{latex(c)}}}{{{denom2}}}"
        
        # \displaystyle ensures fractions are full-size
        equation = f"\\displaystyle {lhs_part1} {sign_d} {lhs_part2} = {rhs}"

        # 5. Construct Solution Steps
        lhs_step1 = f"x({latex(x + b)}) {sign_d} {latex(abs_d)}"
        rhs_step1 = f"{latex(c)}({latex(x + a)})"
        step1_str = f"{lhs_step1} = {rhs_step1}"

        quad_expr = x**2 + (b - c)*x + (d - c*a)
        
        factor1 = x - x_ext
        factor2 = x - x_valid
        
        factored_str = f"({latex(factor1)})({latex(factor2)}) = 0"

        return {
            "equation": equation,
            "step1": step1_str,
            "quadratic": f"{latex(quad_expr)} = 0",
            "factored": factored_str,
            "x_ext": str(x_ext),
            "x_valid": str(x_valid),
        }