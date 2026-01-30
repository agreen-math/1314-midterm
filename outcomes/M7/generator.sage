from sage.all import *
from random import randint, choice

class Generator(BaseGenerator):
    def data(self):
        t = var("t")
        
        # 1. Pick a "nice" time for the maximum height (vertex x-coord)
        # Choosing 1, 2, 3, or 4 seconds ensures reasonable numbers
        t_vertex = Integer(randint(1, 5))
        
        # 2. Calculate initial velocity v0 to force that vertex
        # Vertex formula: t = -b / 2a
        # t = -v0 / (2 * -16)  =>  t = v0 / 32
        # So v0 = 32 * t
        v0 = 32 * t_vertex
        
        # 3. Pick initial height (h0) - "feet above the lake"
        h0 = Integer(randint(20, 120))
        
        # 4. Calculate the Maximum Height (vertex y-coord)
        max_height = -16 * (t_vertex**2) + v0 * t_vertex + h0
        
        # 5. Format the equation
        equation = f"h(t) = -16t^2 + {v0}t + {h0}"
        
        # 6. Generate Solution Steps
        
        # Part A Steps (Time)
        # t = -b / 2a
        part_a_setup = f"t = \\frac{{-{v0}}}{{2(-16)}}"
        part_a_simplify = f"\\frac{{-{v0}}}{{-32}}"
        part_a_ans = f"{t_vertex}"
        
        # Part B Steps (Height)
        # h(2) = -16(2)^2 + ...
        part_b_setup = f"h({t_vertex}) = -16({t_vertex})^2 + {v0}({t_vertex}) + {h0}"
        term1 = -16 * (t_vertex**2)
        term2 = v0 * t_vertex
        part_b_simplify = f"= {term1} + {term2} + {h0}"
        part_b_ans = f"{max_height}"
        
        # Part C Sentence
        sentence = f"The rocket will reach a maximum height of {max_height} ft {t_vertex} seconds after launch."

        return {
            "h0": str(h0),
            "equation": equation,
            "part_a_setup": part_a_setup,
            "part_a_simplify": part_a_simplify,
            "part_a_ans": part_a_ans,
            "part_b_setup": part_b_setup,
            "part_b_simplify": part_b_simplify,
            "part_b_ans": part_b_ans,
            "sentence": sentence,
        }