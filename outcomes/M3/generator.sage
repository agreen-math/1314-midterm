from sage.all import *

class Generator(BaseGenerator):
    def data(self):
        # Define the symbolic variable for SageMath
        x = var("x")
        
        # Select h and k to ensure complex roots of the form h +/- ki*sqrt(3)
        # Choosing k=1 specifically yields the +/- i*sqrt(3) structure
        h = choice([-5, -4, -3, -2, 2, 3, 4, 5])
        k = 1 
        
        # Coefficients for x^2 + bx + c = 0
        a = 1
        b = -2 * h
        c = h**2 + 3 * (k**2)
        
        # Define the symbolic equation and discriminant
        equation = a*x**2 + b*x + c == 0
        discriminant = b**2 - 4*a*c
        
        # Solve exactly using SageMath's symbolic engine
        solutions = solve(equation, x)

        return {
            "equation": latex(equation),
            "a": a,
            "b": b,
            "c": c,
            "discriminant": discriminant,
            "solutions": latex(solutions),
        }