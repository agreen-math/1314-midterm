from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')

        # 1. Setup - Simple Linear Radical
        # Structure: sqrt(x + B) + C = D
        
        # 'k' is the isolated value (must be positive)
        k = randint(2, 9)
        
        # Pick the solution first to guarantee integers
        sol = randint(-10, 10)
        
        # Calculate B
        # x + B = k^2  ->  B = k^2 - sol
        B = k**2 - sol
        
        # Constraint: B cannot be zero
        while B == 0:
            sol = randint(-10, 10)
            B = k**2 - sol
        
        # Pick outside constant C
        C = randint(-9, 9)
        while C == 0:
            C = randint(-9, 9)
            
        # Calculate D
        D = k + C
        
        # 2. Build Equation String
        # Handle sign of B cleanly
        if B > 0:
            radicand = f"x + {B}"
        else:
            radicand = f"x - {abs(B)}"
            
        # Handle sign of C cleanly
        if C > 0:
            sign_C = f"+ {C}"
        else:
            sign_C = f"- {abs(C)}"
            
        equation = f"\\sqrt{{{radicand}}} {sign_C} = {D}"
        
        # 3. Steps
        
        # Step 1: Isolate
        step1 = f"\\sqrt{{{radicand}}} = {k}"
        
        # Step 2: Square
        step2 = f"{radicand} = {k**2}"
        
        # Step 3: Solve (Simple subtraction)
        # Formatted so we don't end up with something like "x = 25 - -4"
        if B > 0:
            step3 = f"x = {k**2} - {B}"
        else:
            step3 = f"x = {k**2} + {abs(B)}"
        
        return {
            "equation": equation,
            "step1": step1,
            "step2": step2,
            "step3": step3,
            "final_ans": f"{sol}"
        }