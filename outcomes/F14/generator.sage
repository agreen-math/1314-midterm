from sage.all import *
from random import choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')
        
        # Determine number of distinct roots and their multiplicities
        scenarios = [
            (1, 1, 1),
            (2, 1, 1),
            (3, 1, 1),
            (1, 2, 0),
            (2, 2, 0)
        ]
        m1, m2, m3 = choice(scenarios)
        
        # Generate clean factors
        d = choice([1, 2])
        e = choice([-4, -3, -2, -1, 1, 2, 3, 4])
        
        if m3 == 0:
            f_coeff = d
            g = e
        else:
            f_coeff = choice([1, 2, 3])
            g = choice([-4, -3, -2, -1, 1, 2, 3, 4])
            # Ensure roots are distinct
            while e * f_coeff == g * d:
                g = choice([-4, -3, -2, -1, 1, 2, 3, 4])
                
        p1 = x**m1
        p2 = (d*x - e)**m2 if m2 > 0 else 1
        p3 = (f_coeff*x - g)**m3 if m3 > 0 else 1
        
        poly = expand(p1 * p2 * p3)
        
        # Build zeros data
        roots_info = []
        def add_root(val, m):
            if m > 0:
                behavior = "bounce" if m % 2 == 0 else "cross"
                roots_info.append({
                    "zero": latex(val),
                    "mult": str(m),
                    "behavior": behavior,
                    "val": float(val)
                })

        add_root(0, m1)
        if m3 == 0:
            add_root(Rational(e, d), m2)
        else:
            add_root(Rational(e, d), m2)
            add_root(Rational(g, f_coeff), m3)
            
        roots_info.sort(key=lambda item: item["val"])
        
        # Format table rows
        blank_rows = ""
        for _ in range(5):
            blank_rows += "                    \\rule[-1.2em]{0pt}{3em} & & \\\\ \\hline\n"
            
        sol_rows = ""
        for info in roots_info:
            # Fixed f-string: doubled the braces around 0pt and 3em
            sol_rows += f"                    \\rule[-1.2em]{{0pt}}{{3em}} {info['zero']} & {info['mult']} & \\text{{{info['behavior']}}} \\\\ \\hline\n"
        for _ in range(5 - len(roots_info)):
            sol_rows += "                    \\rule[-1.2em]{0pt}{3em} & & \\\\ \\hline\n"
            
        # Format factorization steps for the solution
        def format_factor(coeff, const, power):
            if power == 0: return ""
            term = ""
            if coeff == 1: term = "x"
            elif coeff == -1: term = "-x"
            else: term = f"{coeff}x"
            
            if const > 0: term += f" - {const}"
            elif const < 0: term += f" + {-const}"
            
            if power == 1: return f"({term})"
            else: return f"({term})^{power}"
            
        f2_str = format_factor(d, e, m2)
        f3_str = format_factor(f_coeff, g, m3)
        f1_str = "x" if m1 == 1 else f"x^{m1}"
        
        step2_str = f"{f1_str}{f2_str}{f3_str}"
        quad_expr = expand((d*x - e)**m2 * (f_coeff*x - g)**m3)
        step1_str = f"{f1_str}({latex(quad_expr)})"
        
        steps = f"\\begin{{aligned}}\nf(x) &= {latex(poly)} \\\\\n&= {step1_str} \\\\\n&= {step2_str}\n\\end{{aligned}}"
        
        return {
            "poly": latex(poly),
            "blank_rows": blank_rows,
            "sol_rows": sol_rows,
            "steps": steps
        }