from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        x = var('x')
        
        # Base Function Points (Zigzag shape)
        base_points = [(-2, 1), (-1, 2), (0, 0), (1, 4), (3, 4)]
        
        while True:
            # 1. Randomize Parameters
            a_mag = choice([1, 1, 2]) 
            a_sign = choice([1, -1])
            A = a_mag * a_sign
            
            B = choice([1, -1])
            
            H = randint(-5, 5)
            K = randint(-5, 5)
            
            # 2. Calculate New Points & Check Bounds
            new_points = []
            valid = True
            
            for (px, py) in base_points:
                nx = (px / B) + H
                ny = A * py + K
                
                # Check 10x10 grid bounds
                if abs(nx) > 10 or abs(ny) > 10:
                    valid = False
                    break
                new_points.append((nx, ny))
            
            if valid:
                break
                
        # 3. Format Expression
        if H == 0:
            shift_str = "x"
        elif H > 0:
            shift_str = f"x - {H}"
        else:
            shift_str = f"x + {abs(H)}"
            
        if B == -1:
            if H == 0:
                inner = "-x"
            else:
                inner = f"-({shift_str})"
        else:
            inner = shift_str
            
        if A == 1:
            a_str = ""
        elif A == -1:
            a_str = "-"
        else:
            a_str = f"{A}"
            
        if K == 0:
            k_str = ""
        elif K > 0:
            k_str = f" + {K}"
        else:
            k_str = f" - {abs(K)}"
            
        expr = f"{a_str}f({inner}){k_str}"
        
        # 4. Answer Keys
        h_ref_ans = "YES" if B == -1 else "NO"
        h_dil_ans = "1"
        if H == 0:
            h_trans_dist = "0"
            h_trans_dir = "NONE"
        elif H > 0:
            h_trans_dist = f"{H}"
            h_trans_dir = "RIGHT"
        else:
            h_trans_dist = f"{abs(H)}"
            h_trans_dir = "LEFT"
            
        v_ref_ans = "YES" if A < 0 else "NO"
        v_dil_ans = f"{a_mag}"
        if K == 0:
            v_trans_dist = "0"
            v_trans_dir = "NONE"
        elif K > 0:
            v_trans_dist = f"{K}"
            v_trans_dir = "UP"
        else:
            v_trans_dist = f"{abs(K)}"
            v_trans_dir = "DOWN"
            
        # 5. TikZ Generation
        def plot_coords(points, color):
            coords = " -- ".join([f"({x},{y})" for x,y in points])
            return f"\\draw[line width=1.5pt, {color}] {coords};"
            
        def plot_dots(points, color):
            dots = ""
            for x,y in points:
                dots += f"\\fill[{color}] ({x},{y}) circle (5pt);\n"
            return dots

        grid_setup = r"""
            \draw[step=1cm, gray!40, very thin] (-10,-10) grid (10,10);
            \draw[thick, <->] (-10.5,0) -- (10.5,0);
            \draw[thick, <->] (0,-10.5) -- (0,10.5);
        """

        # Set scale to 0.39 per user request
        graph_orig = r"\begin{tikzpicture}[scale=0.39]" + grid_setup
        graph_orig += plot_coords(base_points, "black")
        graph_orig += plot_dots(base_points, "black")
        graph_orig += r"\end{tikzpicture}"
        
        graph_blank = r"\begin{tikzpicture}[scale=0.39]" + grid_setup + r"\end{tikzpicture}"
        
        graph_sol = r"\begin{tikzpicture}[scale=0.39]" + grid_setup
        graph_sol += plot_coords(new_points, "blue")
        graph_sol += plot_dots(new_points, "blue")
        graph_sol += r"\end{tikzpicture}"

        return {
            "expr": expr,
            "h_ref": h_ref_ans,
            "h_dil": h_dil_ans,
            "h_dist": h_trans_dist,
            "h_dir": h_trans_dir,
            "v_ref": v_ref_ans,
            "v_dil": v_dil_ans,
            "v_dist": v_trans_dist,
            "v_dir": v_trans_dir,
            "graph_orig": graph_orig,
            "graph_blank": graph_blank,
            "graph_sol": graph_sol
        }