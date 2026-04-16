from sage.all import *
from random import choice

class Generator(BaseGenerator):
    def data(self):
        found = False
        while not found:
            # 1. HA value
            d = choice([-4, -3, -2, -1, 1, 2, 3, 4])
            
            # 2. Pick VAs: strictly inside [-6, 6] for "runway", at least 4 units apart
            v1 = choice([-6, -5, -4, -3, -2, -1])
            v2 = choice([1, 2, 3, 4, 5, 6])
            if v2 - v1 < 4:
                continue
                
            # 3. Pick Roots (x-intercepts)
            r1 = choice([x for x in range(-8, 9) if x not in [0, v1, v2]])
            r2 = choice([x for x in range(-8, 9) if x not in [0, v1, v2, r1]])
            
            # 4. Check for a single crossing of the HA
            v_sum = v1 + v2
            v_prod = v1 * v2
            r_sum = r1 + r2
            r_prod = r1 * r2
            
            if v_sum == r_sum:
                continue # No unique crossing
                
            x_c = (v_prod - r_prod) / float(v_sum - r_sum)
            
            # Enforce HA crossing is strictly between the VAs
            if not (v1 + 0.5 < x_c < v2 - 0.5):
                continue
                
            # Internal function for evaluation
            def func(x_val):
                if x_val == v1 or x_val == v2: return 999 # Safe fallback
                return d * (x_val - r1) * (x_val - r2) / ((x_val - v1) * (x_val - v2))
                
            # 5. Visibility Check: Ensure outer branches comfortably drop into viewing area (y <= 8)
            left_visible = any(abs(func(x)) <= 8 for x in [val/2.0 for val in range(-20, int(v1*2))])
            right_visible = any(abs(func(x)) <= 8 for x in [val/2.0 for val in range(int(v2*2)+1, 21)])
            
            if not left_visible or not right_visible:
                continue
                
            # 6. Pick a Hole
            valid_holes = [x for x in range(-8, 9) if x not in [0, v1, v2, r1, r2] and abs(func(x)) <= 9.5]
            if not valid_holes:
                continue
                
            a = choice(valid_holes)
            found = True

        ha = d
        h = a
        y_h = func(h)
        y_int = func(0)

        # --- Smart Point Picker (Scoring System for Clean Coordinates) ---
        def sign(val):
            return 1 if val > 0 else -1

        def smart_pick(valid_xs, region_known_xs, is_middle=False):
            if not valid_xs: return None
            
            target_side = None
            if is_middle:
                known_ys = [func(kx) for kx in region_known_xs]
                known_sides = [sign(y - ha) for y in known_ys if abs(y - ha) > 0.01]
                if known_sides:
                    if all(s > 0 for s in known_sides): target_side = -1
                    elif all(s < 0 for s in known_sides): target_side = 1

            best_pt = None
            best_score = -999999

            for x in valid_xs:
                y = func(x)
                
                # Boundary safety
                if abs(y) > 9.5: continue
                if abs(y - ha) < 0.3: continue # Don't hug the HA too tight
                
                score = 0
                
                # Rule 1: Crossing Proof (Mandatory if missing)
                if is_middle and target_side is not None:
                    if sign(y - ha) == target_side:
                        score += 10000 + abs(y - ha) * 10
                    else:
                        continue 
                elif is_middle:
                    score += abs(y - ha) * 5

                # Rule 2: Integer & Clean Decimal Preference
                if x % 1 == 0: score += 500
                
                if abs(y - round(y)) < 0.05:
                    score += 1000 # Perfect integer y
                elif abs(y*2 - round(y*2)) < 0.05:
                    score += 300  # Clean .5 y
                    
                # Rule 3: Avoid hugging the Vertical Asymptotes
                min_dist_VA = min(abs(x - v1), abs(x - v2))
                if min_dist_VA < 1.0:
                    score -= 500 
                
                if score > best_score:
                    best_score = score
                    best_pt = x

            if best_pt is not None:
                return best_pt
            
            # Fallback if strict scoring failed
            fallback = [x for x in valid_xs if abs(func(x)) <= 9.5]
            return fallback[len(fallback)//2] if fallback else valid_xs[len(valid_xs)//2]

        # --- Generate Plottable Helpful Points ---
        exclude = {h, v1, v2, r1, r2, 0}
        known_xs = [r1, r2, 0, h]
        
        # Check every half integer for the best visual points
        xs_pool = [x/2.0 for x in range(-19, 20)]
        
        # Region 1: Left
        r1_knowns = [x for x in known_xs if x < v1]
        valid_p1 = [x for x in xs_pool if x < v1 and x not in exclude and abs(x-v1) > 0.1]
        p1 = smart_pick(valid_p1, r1_knowns, False) if valid_p1 else v1 - 2

        # Region 2: Middle
        r2_knowns = [x for x in known_xs if v1 < x < v2]
        valid_p2 = [x for x in xs_pool if v1 < x < v2 and x not in exclude and abs(x-v1) > 0.1 and abs(x-v2) > 0.1]
        p2 = smart_pick(valid_p2, r2_knowns, True) if valid_p2 else (v1 + v2) / 2.0

        # Region 3: Right
        r3_knowns = [x for x in known_xs if x > v2]
        valid_p3 = [x for x in xs_pool if x > v2 and x not in exclude and abs(x-v2) > 0.1]
        p3 = smart_pick(valid_p3, r3_knowns, False) if valid_p3 else v2 + 2

        # --- Format Table ---
        def pt(x, y): 
            x_val = round(float(x), 2)
            y_val = round(float(y), 2)
            return f"({x_val:g}, {y_val:g})"

        x_ints = list(set([r1, r2]))
        x_int_1 = pt(x_ints[0], 0)
        x_int_2 = pt(x_ints[1], 0) if len(x_ints) > 1 else ""

        table_latex = f"""
        \\renewcommand{{\\arraystretch}}{{1.4}}
        \\begin{{array}}{{|r|c|c|}}
            \\hline
            \\textbf{{Holes:}} & {pt(h, y_h)} & \\\\ \\hline
            \\textbf{{Asymptotes:}} & x = {v1} & x = {v2} \\\\
            & y = {ha} & \\\\ \\hline
            \\textbf{{Intercepts:}} & {x_int_1} & {x_int_2} \\\\
            & {pt(0, y_int)} & \\\\ \\hline
            \\textbf{{Helpful Points:}} & {pt(p1, func(p1))} & {pt(p2, func(p2))} \\\\
            & {pt(p3, func(p3))} & \\\\ \\hline
        \\end{{array}}
        """

        # --- Construct the Unexpanded Function String ---
        def build_poly_str(coeff, roots):
            factors = []
            has_x = False
            for r in roots:
                if r == 0:
                    has_x = True
                elif r > 0:
                    factors.append(f"(x - {r})")
                else:
                    factors.append(f"(x + {abs(r)})")
            
            res = ""
            if coeff == -1: res += "-"
            elif coeff != 1: res += str(coeff)
            if has_x: res += "x"
            res += "".join(factors)
            return res

        num_str = build_poly_str(d, [r1, r2, h])
        den_str = build_poly_str(1, [v1, v2, h])
        func_latex = f"f(x) = \\frac{{{num_str}}}{{{den_str}}}"

        # --- TikZ Graphing Setup ---
        grid_setup = r"""
            \draw[step=1cm, gray!40, very thin] (-10,-10) grid (10,10);
            \draw[thick, <->] (-10.5,0) -- (10.5,0);
            \draw[thick, <->] (0,-10.5) -- (0,10.5);
        """
        
        graph_blank = r"\begin{tikzpicture}[scale=0.39]" + grid_setup + r"\end{tikzpicture}"
        
        graph_sol = r"\begin{tikzpicture}[scale=0.39]" + grid_setup
        graph_sol += r"\clip (-10.5,-10.5) rectangle (10.5,10.5);"
        
        # Draw Asymptotes
        graph_sol += f"\\draw[dashed, blue, thick, <->] ({v1}, -10.5) -- ({v1}, 10.5);\n"
        graph_sol += f"\\draw[dashed, blue, thick, <->] ({v2}, -10.5) -- ({v2}, 10.5);\n"
        graph_sol += f"\\draw[dashed, blue, thick, <->] (-10.5, {ha}) -- (10.5, {ha});\n"
        
        # TikZ function evaluated using PGFMath natively
        tikz_func = f"{d} * (\\x - ({r1})) * (\\x - ({r2})) / ((\\x - ({v1})) * (\\x - ({v2})))"
        
        # Draw the curve in 3 continuous pieces to avoid asymptote infinity lines
        d1_end = v1 - 0.1
        d2_start = v1 + 0.1
        d2_end = v2 - 0.1
        d3_start = v2 + 0.1
        
        graph_sol += f"\\draw[blue, very thick, samples=80, domain=-10.5:{d1_end}, smooth] plot (\\x, {{{tikz_func}}});\n"
        graph_sol += f"\\draw[blue, very thick, samples=80, domain={d2_start}:{d2_end}, smooth] plot (\\x, {{{tikz_func}}});\n"
        graph_sol += f"\\draw[blue, very thick, samples=80, domain={d3_start}:10.5, smooth] plot (\\x, {{{tikz_func}}});\n"

        def tkz_pt(val):
            return round(float(val), 2)

        # Draw Points
        for px in x_ints:
            graph_sol += f"\\fill[blue] ({tkz_pt(px)}, 0) circle (4pt);\n"
            
        graph_sol += f"\\fill[blue] (0, {tkz_pt(y_int)}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({tkz_pt(p1)}, {tkz_pt(func(p1))}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({tkz_pt(p2)}, {tkz_pt(func(p2))}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({tkz_pt(p3)}, {tkz_pt(func(p3))}) circle (4pt);\n"
        
        # Draw Hole
        graph_sol += f"\\draw[blue, thick, fill=white] ({tkz_pt(h)}, {tkz_pt(y_h)}) circle (4pt);\n"

        graph_sol += r"\end{tikzpicture}"

        return {
            "table_latex": table_latex,
            "graph_blank": graph_blank,
            "graph_sol": graph_sol,
            "func_latex": func_latex
        }