from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var("x")

        # 1. Define the constant C for f(x) = cbrt(x) + C
        # We keep it between -6 and 6 to keep the cubed numbers reasonable
        c = Integer(randint(-6, 6))
        while c == 0:
            c = Integer(randint(-6, 6))

        # 2. Format the function definition
        if c < 0:
            sign_c = "-"
            abs_c = -c
            # If f(x) = cbrt(x) - 3, then inverse uses (x + 3)
            inv_sign = "+"
            inv_val = -c 
        else:
            sign_c = "+"
            abs_c = c
            # If f(x) = cbrt(x) + 3, then inverse uses (x - 3)
            inv_sign = "-"
            inv_val = c

        function_def = f"f(x) = \\sqrt[3]{{x}} {sign_c} {abs_c}"

        # 3. Setup steps strings
        # Step 1: Replace f(x) with y
        step1 = f"y = \\sqrt[3]{{x}} {sign_c} {abs_c}"
        
        # Step 2: Swap x and y
        step2 = f"x = \\sqrt[3]{{y}} {sign_c} {abs_c}"
        
        # Step 3: Isolate the radical
        step3 = f"x {inv_sign} {inv_val} = \\sqrt[3]{{y}}"
        
        # Step 4: Cube both sides
        step4 = f"(x {inv_sign} {inv_val})^3 = y"

        # 4. Expand the polynomial (x + k)^3
        # Formula: x^3 + 3k x^2 + 3k^2 x + k^3
        # Determine k based on the inverse sign
        k = inv_val if inv_sign == "+" else -inv_val
        
        coeff_x2 = 3 * k
        coeff_x1 = 3 * k**2
        coeff_x0 = k**3

        # Build the polynomial string carefully to handle signs
        poly = "x^3"
        
        # x^2 term
        if coeff_x2 < 0: poly += f" - {-coeff_x2}x^2"
        else:            poly += f" + {coeff_x2}x^2"
        
        # x term (always positive since 3*k^2)
        poly += f" + {coeff_x1}x"
        
        # Constant term
        if coeff_x0 < 0: poly += f" - {-coeff_x0}"
        else:            poly += f" + {coeff_x0}"

        step5 = f"f^{{-1}}(x) = {poly}"

        return {
            "function_def": function_def,
            "step1": step1,
            "step2": step2,
            "step3": step3,
            "step4": step4,
            "step5": step5,
            "expanded": poly,
        }