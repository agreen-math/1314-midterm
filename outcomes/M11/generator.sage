from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')
        
        while True:
            # 1. Pick 'a' (stretch factor)
            denom = choice([1, 1, 2])
            sign = choice([1, -1])
            a = sign * Rational(1) / denom
            
            # 2. Pick distance 'd' (distance from axis of symmetry to x-intercepts)
            if denom == 1:
                d = randint(1, 5)
            else:
                d = choice([2, 4, 6])
            
            # 3. Calculate k
            k_val = -a * (d**2)
            k = Integer(k_val)
            
            # Constraint: Vertex cannot be on the x-axis, must fit on graph
            if k == 0 or abs(k) > 10: 
                continue
            
            # 4. Pick h (Axis)
            # Constraint: Vertex cannot be on the y-axis (h != 0).
            # Constraint: Reflected y-intercept x-coord is 2h. So abs(2h) <= 10  =>  abs(h) <= 5.
            if denom == 2:
                # To keep y-intercept an integer when a = +/- 1/2, h must be even.
                h_opts = [-4, -2, 2, 4]
            else:
                h_opts = [-5, -4, -3, -2, -1, 1, 2, 3, 4, 5]
                
            h = choice(h_opts)
            
            # Constraint: Prevent the reflected y-int from overlapping with the given x-int.
            if d == abs(h):
                continue
            
            # 5. Check y-intercept
            y_int_val = a*(h**2) + k
            if not y_int_val in ZZ: 
                continue
            y_int = Integer(y_int_val)
            
            # Constraint: y-intercept cannot be the origin, must fit on graph
            if y_int == 0 or abs(y_int) > 10: 
                continue
            
            # 6. Check roots (x-intercepts)
            x1 = h - d
            x2 = h + d
            
            # Constraint: x-intercepts must fit on graph
            if abs(x1) > 10 or abs(x2) > 10: 
                continue
            
            # 7. Check Reflected Point (redundant because of abs(h) <= 5, but good for safety)
            x_ref = 2*h
            if abs(x_ref) > 10: 
                continue
            
            # If all constraints pass, we have a perfect problem
            break

        # --- Format Data for Question ---
        vertex_q = f"({h}, {k})"
        y_int_val = f"{y_int}"
        given_root = choice([x1, x2])
        x_int_val = f"{given_root}"

        # --- Format Data for Solution ---
        # We wrap labels in \text{} but keep coords outside so minus signs render as math.
        
        p1 = f"\\text{{Vertex: }} ({h}, {k})"
        p2 = f"y\\text{{-intercept: }} (0, {y_int})"
        p3 = f"\\text{{Reflected }} y\\text{{-int: }} ({x_ref}, {y_int})"
        p4 = f"\\text{{Given Root: }} ({given_root}, 0)"
        
        other_root = x2 if given_root == x1 else x1
        p5 = f"\\text{{Reflected Root: }} ({other_root}, 0)"
        
        if a > 0:
            opens = "Up"
        else:
            opens = "Down"

        # --- Generate TikZ Code ---
        grid_color = "gray!40"
        curve_color = "blue!80!black"
        point_color = "blue"
        
        tikz = r"""
        \begin{tikzpicture}[scale=0.35]
            \draw[step=1cm, """ + grid_color + r""", very thin] (-10,-10) grid (10,10);
            \draw[thick, <->] (-10.5,0) -- (10.5,0);
            \draw[thick, <->] (0,-10.5) -- (0,10.5);
            \clip (-10,-10) rectangle (10,10);
            \draw[line width=1.5pt, """ + curve_color + r""", samples=100, domain=-10:10, <->] 
                plot (\x, {""" + f"{float(a)}*(\\x - {h})^2 + {k}" + r"""});
            \fill[""" + point_color + r"""] (""" + f"{h},{k}" + r""") circle (7pt);
            \fill[""" + point_color + r"""] (""" + f"{x1},0" + r""") circle (7pt);
            \fill[""" + point_color + r"""] (""" + f"{x2},0" + r""") circle (7pt);
            \fill[""" + point_color + r"""] (""" + f"0,{y_int}" + r""") circle (7pt);
            \fill[""" + point_color + r"""] (""" + f"{x_ref},{y_int}" + r""") circle (7pt);
        \end{tikzpicture}
        """

        blank_grid = r"""
        \begin{tikzpicture}[scale=0.35]
            \draw[step=1cm, gray!40, very thin] (-10,-10) grid (10,10);
            \draw[thick, <->] (-10.5,0) -- (10.5,0);
            \draw[thick, <->] (0,-10.5) -- (0,10.5);
        \end{tikzpicture}
        """

        return {
            "vertex": vertex_q,
            "x_val": x_int_val,
            "y_val": y_int_val,
            "sol_p1": p1,
            "sol_p2": p2,
            "sol_p3": p3,
            "sol_p4": p4,
            "sol_p5": p5,
            "opens": opens,
            "sol_graph": tikz,
            "blank_grid": blank_grid
        }