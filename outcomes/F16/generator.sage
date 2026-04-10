from sage.all import *
from random import choice

class Generator(BaseGenerator):
    def data(self):
        # 1. Generate Parameters for f(x) = a(x-r1)(x-r2) / ((x-v1)(x-v2))
        v1 = choice([-4, -3, -2])
        v2 = choice([2, 3, 4])
        
        # Ensure roots don't overlap with asymptotes or 0
        r1 = choice([x for x in range(-5, 6) if x not in [v1, v2, 0]])
        r2 = choice([x for x in range(-5, 6) if x not in [v1, v2, r1, 0]])
        
        a = choice([-2, -1, 1, 2])
        
        # Ensure hole doesn't overlap with key features
        h = choice([x for x in range(-6, 7) if x not in [v1, v2, r1, r2, 0]])

        # Secret function used to generate table values accurately
        def f(x_val):
            return a * (x_val - r1) * (x_val - r2) / ((x_val - v1) * (x_val - v2))

        # Calculate exact values for Hole and Y-Intercept
        y_h = f(h)
        y_int = f(0)

        # Generate Plottable Helpful Points (ensure they fit on a 10x10 grid)
        # Point 1: Left of v1
        valid_p1 = [x for x in range(-9, v1) if x != h and abs(f(x)) <= 10]
        p1 = choice(valid_p1) if valid_p1 else v1 - 2
        y_p1 = f(p1)

        # Point 2: Between v1 and v2
        valid_p2 = [x for x in range(v1 + 1, v2) if x not in [h, r1, r2, 0] and abs(f(x)) <= 10]
        p2 = choice(valid_p2) if valid_p2 else (v1 + v2) / 2.0
        y_p2 = f(p2)

        # Point 3: Right of v2
        valid_p3 = [x for x in range(v2 + 1, 10) if x != h and abs(f(x)) <= 10]
        p3 = choice(valid_p3) if valid_p3 else v2 + 2
        y_p3 = f(p3)

        # 2. Format Table 
        def pt(x, y): 
            return f"({round(float(x), 1):g}, {round(float(y), 2):g})"

        table_latex = f"""
        \\renewcommand{{\\arraystretch}}{{1.4}}
        \\begin{{array}}{{|r|c|c|}}
            \\hline
            \\textbf{{Holes:}} & {pt(h, y_h)} & \\\\ \\hline
            \\textbf{{Asymptotes:}} & x = {v1} & x = {v2} \\\\
            & y = {a} & \\\\ \\hline
            \\textbf{{Intercepts:}} & {pt(r1, 0)} & {pt(r2, 0)} \\\\
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
        graph_sol += f"\\draw[dashed, blue, thick, <->] (-10.5, {a}) -- (10.5, {a});\n"
        
        # TikZ function evaluated using PGFMath natively
        tikz_func = f"{a} * (\\x - ({r1})) * (\\x - ({r2})) / ((\\x - ({v1})) * (\\x - ({v2})))"
        
        # Draw the curve in 3 continuous pieces to avoid asymptote infinity lines
        d1_end = v1 - 0.1
        d2_start = v1 + 0.1
        d2_end = v2 - 0.1
        d3_start = v2 + 0.1
        
        graph_sol += f"\\draw[blue, very thick, samples=80, domain=-10.5:{d1_end}, smooth] plot (\\x, {{{tikz_func}}});\n"
        graph_sol += f"\\draw[blue, very thick, samples=80, domain={d2_start}:{d2_end}, smooth] plot (\\x, {{{tikz_func}}});\n"
        graph_sol += f"\\draw[blue, very thick, samples=80, domain={d3_start}:10.5, smooth] plot (\\x, {{{tikz_func}}});\n"

        # Draw Points
        graph_sol += f"\\fill[blue] ({r1}, 0) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({r2}, 0) circle (4pt);\n"
        graph_sol += f"\\fill[blue] (0, {y_int}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({p1}, {y_p1}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({p2}, {y_p2}) circle (4pt);\n"
        graph_sol += f"\\fill[blue] ({p3}, {y_p3}) circle (4pt);\n"
        
        # Draw Hole (after the curve to "punch" out the line)
        graph_sol += f"\\draw[blue, thick, fill=white] ({h}, {y_h}) circle (4pt);\n"

        graph_sol += r"\end{tikzpicture}"

        return {
            "table_latex": table_latex,
            "graph_blank": graph_blank,
            "graph_sol": graph_sol
        }