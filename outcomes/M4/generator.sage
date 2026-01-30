from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var("x")

        # 1. Force a negative solution for x (e.g., -5)
        x_sol = Integer(randint(-12, -1))
        
        # 2. Pick the value the radical equals (must be positive)
        # k = sqrt(A - x)
        k = Integer(randint(2, 9))
        
        # 3. Calculate the constant inside the radical (A)
        # k^2 = A - x  =>  A = k^2 + x
        A = k**2 + x_sol
        
        # 4. Define external constant C and result D
        # sqrt(...) + C = D
        C = Integer(randint(-10, 10))
        while C == 0:
            C = Integer(randint(-10, 10))
            
        D = k + C

        # 5. Format the equation display
        # Handle sign of C: \sqrt{11 - x} - 3 = 5
        if C < 0:
            sign_C = "-"
            abs_C = -C
        else:
            sign_C = "+"
            abs_C = C

        equation = f"\\sqrt{{{A} - x}} {sign_C} {abs_C} = {D}"

        # 6. Generate Plain Solution Steps
        # Step 1: Isolate Radical
        step1 = f"\\sqrt{{{A} - x}} = {k}"
        
        # Step 2: Square both sides
        step2 = f"{A} - x = {k**2}"
        
        # Step 3: Subtract A
        rhs_isolated = k**2 - A
        step3 = f"-x = {rhs_isolated}"
        
        # Step 4: Final Answer
        step4 = f"x = {x_sol}"

        return {
            "equation": equation,
            "step1": step1,
            "step2": step2,
            "step3": step3,
            "step4": step4,
            "x": str(x_sol),
        }