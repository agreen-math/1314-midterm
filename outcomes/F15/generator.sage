from sage.all import *
from random import choice

class Generator(BaseGenerator):
    def data(self):
        # 1. Generate Parameters for f(x) = k(x-a)(x+b) / ((x-a)(x-b)(x+c))
        k = choice([-1, 1])
        
        # Pick b to avoid 1 (keeps the x-intercept and VA1 separated well)
        b = choice([2, 3, -2, -3])
        v_b = b      # VA from (x-b)
        
        # Pick v_c (which is -c) such that it is at least 3 units away from v_b
        valid_vc = [v for v in range(-5, 6) if abs(v - v_b) >= 3 and v != -b and v != 0]
        v_c = choice(valid_vc)
        c = -v_c     # VA from (x+c)
        
        v1 = min(v_b, v_c)
        v2 = max(v_b, v_c)
        
        # Secret reduced function used to generate values accurately
        # Reduced form: k(x+b) / ((x-b)(x+c))
        def f(x_val):
            return k * (x_val + b) / ((x_val - b) * (x_val + c))
            
        # Pick a hole that doesn't overlap with intercepts/VAs AND has a drawable y-value
        valid_holes = [x for x in range(-6, 7) if x not in [0, b, -b, -c] and abs(f(x)) <= 9.5]
        a = choice(valid_holes)
        
        h = a
        y_h = f(h)
        y_int = f(0) 
        
        # HA is strictly 0 because denominator degree > numerator degree
        ha = 0

        # --- Smart Point Picker ---
        def sign(val):
            return 1 if val > 0 else -1

        def smart_pick(valid_xs, region_known_xs):
            if not valid_xs: return None
            
            # 1. Filter for "Goldilocks" y-values (not practically zero, not off graph)
            tight_xs = [x for x in valid_xs if 0.4 <= abs(f(x)) <= 9.5]
            pool = tight_xs if tight_xs else valid_xs # Fallback if none are perfect
            
            # 2. Check for Horizontal Asymptote crossings
            known_ys = [f(kx) for kx in region_known_xs]
            known_sides = [sign(y - ha) for y in known_ys if abs(y - ha) > 0.01]
            
            target_side = None
            if known_sides:
                if all(s > 0 for s in known_sides):
                    target_side = -1 # All known points are above HA, look for one below
                elif all(s < 0 for s in known_sides):
                    target_side = 1  # All known points are below HA, look for one above
                    
            candidates = []
            if target_side is not None:
                candidates = [x for x in pool if sign(f(x) - ha) == target_side]
                
            if candidates:
                # Pick the point that dips the furthest to make the crossing obvious
                return max(candidates, key=lambda x: abs(f(x) - ha))
            else:
                # No crossing to prove. Pick a representative point in the middle of the branch.
                return pool[len(pool) // 2]

        # --- Generate Plottable Helpful Points ---
        exclude = {h, b, -c, 0, -b}
        known_xs = [-b, 0, h]
        
        # Use half-integer steps for a wider variety of "clean" y-values
        xs_pool = [x/2.0 for x in range(-19, 20)]
        
        # Region 1: Left of v1
        r1_knowns = [x for x in known_xs if x < v1]
        valid_p1 = [x for x in xs_pool if x < v1 and x not in exclude and abs(x-v1) > 0.1]
        p1 = smart_pick(valid_p1, r1_knowns) if valid_p1 else v1 - 2
        y_p1 = f(p1)

        # Region 2: Between v1 and v2
        r2_knowns = [x for x in known_xs if v1 < x < v2]
        valid_p2 = [x for x in xs_pool if v1 < x < v2 and x not in exclude and abs(x-v1) > 0.1 and abs(x-v2) > 0.1]
        p2 = smart_pick(valid_p2, r2_knowns) if valid_p2 else (v1 + v2) / 2.0
        y_p2 = f(p2)

        # Region 3: Right of v2
        r3_knowns = [x for x in known_xs if x > v2]
        valid_p3 = [x for x in xs_pool if x > v2 and x not in exclude and abs(x-v2) > 0.1]
        p3 = smart_pick(valid_p3, r3_knowns) if valid_p3 else v2 + 2
        y_p3 = f(p3)

        # 2. Format Table 
        # Explicitly convert to standard python float and round to wipe out precision trails
        def pt(x, y): 
            x_val = round(float(x), 2)
            y_val = round(float(y), 2)
            return f"({x_val:g}, {y_val:g})"

        table_latex = f"""
        \\renewcommand{{\\arraystretch}}{{1.4}}
        \\begin{{array}}{{|r|c|c|}}
            \\hline
            \\textbf{{Holes:}} & {pt(h, y_h)} & \\\\ \\hline
            \\textbf{{Asymptotes:}} & x = {v1} & x = {v2} \\\\
            & y = {ha} & \\\\ \\hline
            \\textbf{{Intercepts:}} & {pt(-b, 0)} & \\\\
            & {pt(0, y_int)} & \\\\ \\hline
            \\textbf{{Helpful Points:}} & {pt(p1, y_p1)} & {pt(p2, y_p2)} \\\\
            & {pt(p3, y_p3)} & \\\\ \\hline
        \\end{{array}}
        """

        # 3. TikZ Graphing Setup
        grid_setup = r"""
            \draw[step=1cm, gray!40, very thin] (-10,-10) grid (10,10);
            \draw[thick, <->] (-10.5,0) -- (10.5,0);
            \draw[thick, <->] (0,-10.5) -- (0,10.5);
        """
        
        # --- Blank Graph ---
        graph_blank = r"\begin{tikzpicture}[scale=0.39]" + grid_setup + r"\end{tikzpicture}"
        
        # --- Solution Graph ---
        graph_sol = r"\begin{tikzpicture}[scale=0.39]" + grid_setup
        graph_sol += r"\clip (-10.5,-10.5) rectangle (10.5,10.5);"
        
        # Draw Asymptotes
        graph_sol += f"\\draw[dashed, blue, thick, <->] ({v1}, -10.5) -- ({v1}, 10.5);\n"
        graph_sol += f"\\draw[dashed, blue, thick, <->] ({v2}, -10.5) -- ({v2}, 10.5);\n"
        graph_sol += f"\\draw[dashed, blue, thick, <->] (-10.5, {ha}) -- (10.5, {ha});\n"
        
        # TikZ function evaluated using PGFMath natively (uses reduced form)
        tikz_func = f"{k} * (\\x + ({b})) / ((\\x - ({b})) * (\\x + ({c})))"
        
        # Draw the curve in 3 continuous pieces to avoid asymptote infinity lines
        d1_end = v1 - 0.1
        d2_start = v1 + 0.1
        d2_end = v2 - 0.1
        d3_start = v2 + 0.1
        
        graph_sol += f"\\draw[blue, very thick, samples=80, domain=-10.5:{d1_end}, smooth] plot (\\x, {{{tikz_func}}});\n"
        graph_sol += f"\\draw[blue, very thick, samples=80, domain={d2_start}:{d2_end}, smooth] plot (\\x, {{{tikz_func}}});\n"
        graph_sol += f"\\draw[blue, very thick, samples=80, domain={d3_start}:10.5, smooth] plot (\\x, {{{tikz_func}}});\n"

        # Safe float parsing for TikZ coordinates
        def tkz_pt(val):
            return round(float(val), 2)

        # Draw Points
        graph_sol += f"\\fill[blue] ({-b}, 0) circle (4pt);\n"
        graph_sol += f"\\fill[blue] (0, {tkz_pt(y_int)}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({tkz_pt(p1)}, {tkz_pt(y_p1)}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({tkz_pt(p2)}, {tkz_pt(y_p2)}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({tkz_pt(p3)}, {tkz_pt(y_p3)}) circle (4pt);\n"
        
        # Draw Hole (after the curve to "punch" out the line)
        graph_sol += f"\\draw[blue, thick, fill=white] ({tkz_pt(h)}, {tkz_pt(y_h)}) circle (4pt);\n"

        graph_sol += r"\end{tikzpicture}"

        return {
            "table_latex": table_latex,
            "graph_blank": graph_blank,
            "graph_sol": graph_sol
        }