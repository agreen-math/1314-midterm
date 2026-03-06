from sage.all import *

class Generator(BaseGenerator):
    def data(self):
        # Define symbolic variables
        x, a_var = var('x a')
        
        # Generate random coefficients all larger than 1
        a_coeff = choice([2..9])
        b_coeff = choice([2..9])
        c_coeff = choice([2..9])
        
        # Build the quadratic function: ax^2 - bx + c
        f(x) = a_coeff*x^2 - b_coeff*x + c_coeff
        
        # (a) Evaluate at a negative integer ONLY
        val_a = choice([-10..-1])
        
        # Intermediate: a(val)^2 - b(val) + c
        step_a = f"{a_coeff}({val_a})^2 - {b_coeff}({val_a}) + {c_coeff}"
        ans_a = f(val_a)
        
        # (b) Evaluate f(-x)
        # Intermediate: a(-x)^2 - b(-x) + c
        step_b = f"{a_coeff}(-x)^2 - {b_coeff}(-x) + {c_coeff}"
        ans_b = f(-x).expand()
        
        # (c) Evaluate f(x + a)
        # Intermediate: a(x+a)^2 - b(x+a) + c
        step_c = f"{a_coeff}(x+a)^2 - {b_coeff}(x+a) + {c_coeff}"
        ans_c = f(x + a_var).expand()

        return {
            "f": f(x),
            "val_a": val_a,
            "step_a": step_a,
            "ans_a": ans_a,
            "step_b": step_b,
            "ans_b": ans_b,
            "step_c": step_c,
            "ans_c": ans_c,
        }