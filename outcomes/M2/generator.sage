from sage.all import *

class Generator(BaseGenerator):
    def data(self):
        x = var('x')
        
        # Define coefficients
        # a is non-zero to ensure the equation remains quadratic
        a = choice([-5..-1] + [1..5])
        b = choice([-9..9])
        c = choice([-9..9])
        
        # d is chosen so that b-d is non-zero
        d = b
        while d == b:
            d = choice([-9..9])
            
        # Creating symbolic expressions ensures juxtaposition in LaTeX
        lhs = a*x^2 + b*x + c
        rhs = d*x
        
        # Intermediate grading values
        b_eff = b - d
        discriminant = b_eff^2 - 4*a*c
        
        # Determine solution type
        if discriminant > 0:
            num_sol = "two"
            type_sol = "unequal real roots"
        elif discriminant == 0:
            num_sol = "one"
            type_sol = "repeated real root"
        else:
            num_sol = "two"
            type_sol = "complex conjugate roots"

        return {
            "equation": f"{latex(lhs)} = {latex(rhs)}",
            "a": a,
            "b_eff": b_eff,
            "c": c,
            "disc": discriminant,
            "num": num_sol,
            "type": type_sol,
        }