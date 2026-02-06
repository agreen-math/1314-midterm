import re
import sys

# ==========================================
# 1. EXAM CONFIGURATION
# ==========================================
EXAM_MAP = [
    # --- Q1: Evaluate Function (Parts) ---
    {
        "id": "Q1",
        "type": "parts",
        "points": [3, 3, 4],
        "header_prefix": r"\question ", 
        # Removed Chapter Solution suffix
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline"
    },
    
    # --- Q2: Discriminant (Single) ---
    {
        "id": "Q2",
        "type": "single",
        "header": r"\question[10] \textbf{\textit{Without solving}}, use the discriminant to determine the number and the type of the solutions." + "\n",
        # Removed Chapter Solution block from start of footer
        "footer": r" \vspace{\stretch{3}}\\" + "\n" + r"number of solutions: \fillin \hspace{\stretch{1}} type of solutions: \fillin[][2.5in] \newpage"
    },
    
    # --- Q3: Quadratic (Single) ---
    {
        "id": "Q3",
        "type": "single",
        "header": r"\uplevel{For the following questions, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n" + r"\question[10] Solve: ",
        # Removed Chapter Solution
        "footer": r" \vspace{\stretch{1}}\\\,\answerline"
    },
    
    # --- Q4: Radical (Single) ---
    {
        "id": "Q4",
        "type": "single",
        "header": r"\question[10] Solve: ",
        # Removed Chapter Solution
        "footer": r" \vspace{\stretch{1}}\\\,\answerline"
    },
    
    # --- Q5: Rational (Single) ---
    {
        "id": "Q5",
        "type": "single",
        "header": r"\question[10] Solve: ",
        # Removed Chapter Solution
        "footer": r" \vspace{\stretch{1}}\\\,\answerline \newpage"
    },
    
    # --- Q6: Inverse (Single) ---
    {
        "id": "Q6",
        "type": "single",
        "header": r"\question[10] ",
        # Removed Chapter Solution
        "footer": r" \vspace{\stretch{2}}\\\,\answerline \newpage"
    },
    
    # --- Q7: Rocket (Parts) ---
    {
        "id": "Q7",
        "type": "parts",
        "points": [2, 2, 1],
        "header_prefix": r"\newpage \question ",
        "part_spacing": [
            r" \vspace{\stretch{1}} \\ \answerline", # Part a
            r" \vspace{\stretch{1}} \\ \answerline", # Part b
            r" \fillwithlines{1in}"                  # Part c
        ],
        "footer": r" \newpage"
    },
    
    # --- Q8: Composition (Parts) ---
    {
        "id": "Q8",
        "type": "parts",
        "points": [6, 4],
        "header_prefix": r"\question ", 
        # Removed Chapter Solution suffix
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline",
        "footer": r" \newpage"
    },
    
    # --- Q9: Difference Quotient (Single) ---
    {
        "id": "Q9",
        "type": "single",
        "header": r"\question[5] ",
        # Removed Chapter Solution
        "footer": r" \vspace{\stretch{1}} \\ \answerline \newpage"
    },
    
    # --- Q10: Vertex/Properties (Single) ---
    {
        "id": "Q10",
        "type": "single",
        "header": r"\question[5] ", 
        "replacements": [
            (
                r"\\begin\{itemize\}.*?\\end\{itemize\}", 
                r"\renewcommand{\arraystretch}{3}\begin{table}[h]\begin{tabular}{|l|l|}\hline vertex & \hspace{2.5in} \\ \hline axis of symmetry & \\ \hline $x$-intercepts(s) & \\ \hline $y$-intercept & \\ \hline domain & \\ \hline range & \\ \hline \end{tabular}\end{table}"
            ),
            (
                r"Find each of the properties below for the given function:",
                r"Find each of the properties below for the given function:"
            ),
            (
                r"Consider the function:",
                r""
            )
        ]
    },
    
    # --- Q11: Graphing (Single) ---
    {
        "id": "Q11",
        "type": "single",
        "header": r"\question[5] ", 
        "footer": r" \newpage"
    },
    
    # --- Q12: Transformations (Single) ---
    {
        "id": "Q12",
        "type": "single",
        "header": r"\question[10] ", 
        "footer": r" \newpage"
    }
]

# ==========================================
# 2. CONFIGURATION & HELPERS
# ==========================================

PREAMBLE = r"""\documentclass[addpoints]{exam}

\usepackage[utf8]{inputenc}
\usepackage{array}
\usepackage{graphicx}
\usepackage{multicol}
\usepackage{amsmath}
\usepackage{paracol}
\usepackage{pgf,tikz}
\usepackage{mathrsfs}
\usetikzlibrary{arrows}

\newcommand{\ci}{\textbf{Chapter 1}}
\newcommand{\cii}{\textbf{Chapter 2}}
\newcommand{\ciii}{\textbf{Chapter 3}}
\newcommand{\civ}{\textbf{Chapter 4}}
\newcommand{\cv}{\textbf{Chapters 5 and 6}}

\setlength\answerskip{2ex}
\setlength\answerlinelength{3in}

% Toggle solutions
%\printsolutions
\noprintsolutions

\pagestyle{headandfoot}
\runningheadrule
\firstpageheader{Math 1314}{Midterm Exam (WEB)}{Fall 2025}
\runningheader{Math 1314}{Midterm Exam (WEB)}{Fall 2025}
\runningheadrule
\firstpagefooter{}{}{}
\runningfooter{}{}{}

\begin{document}

\noindent{Number of Questions: \numquestions\hspace{\stretch{1}} Point Total: \numpoints}
\begin{questions}
"""

POSTAMBLE = r"""
\end{questions}
\end{document}
"""

def get_braced_content(text, start_index=0):
    balance = 1
    i = start_index + 1
    while i < len(text) and balance > 0:
        if text[i] == '{': balance += 1
        elif text[i] == '}': balance -= 1
        i += 1
    if balance == 0:
        return text[start_index+1 : i-1], i
    return "", start_index + 1

def clean_solutions(content):
    content = re.sub(r'\\stxTitle\{.*?\}', '', content)
    while True:
        match = re.search(r'\\stxOuttro\s*\{', content)
        if not match: break
        start_pos = match.start()
        open_brace_pos = match.end() - 1
        inner_text, end_pos = get_braced_content(content, open_brace_pos)
        inner_text = re.sub(r'^\s*SOLUTION\s*', '', inner_text, flags=re.IGNORECASE | re.MULTILINE).strip()
        new_block = r'\begin{solution}' + "\n" + inner_text + "\n" + r'\end{solution}'
        content = content[:start_pos] + new_block + content[end_pos:]
    return content.strip()

def parse_checkit_item(raw_block):
    match = re.search(r'\\stxKnowl\s*\{', raw_block)
    if not match: return None
    outer_content, _ = get_braced_content(raw_block, match.end() - 1)
    
    if r'\begin{enumerate}' in outer_content:
        split_parts = re.split(r'\\begin\{enumerate\}', outer_content, 1)
        intro_text = split_parts[0].strip()
        enum_body = split_parts[1].split(r'\end{enumerate}')[0]
        raw_parts = re.split(r'\\item', enum_body)
        clean_parts = []
        for p in raw_parts:
            if not p.strip(): continue
            p_match = re.search(r'\\stxKnowl\s*\{', p)
            if p_match:
                part_content, _ = get_braced_content(p, p_match.end()-1)
                clean_parts.append(clean_solutions(part_content))
            else:
                clean_parts.append(clean_solutions(p))
        return {
            'type': 'parts',
            'intro': clean_solutions(intro_text),
            'parts': clean_parts
        }
    else:
        return {
            'type': 'single',
            'content': clean_solutions(outer_content)
        }

# ==========================================
# 3. MAIN PROCESSOR
# ==========================================

def process_exam(input_file, output_file):
    with open(input_file, 'r') as f:
        full_text = f.read()

    separator = r'\\item\s*%%%%% SpaTeXt Commands %%%%%'
    blocks = re.split(separator, full_text)
    if len(blocks) > 0: blocks = blocks[1:]
    
    print(f"Found {len(blocks)} Question Blocks.")
    
    final_output = []
    count = min(len(blocks), len(EXAM_MAP))
    
    for i in range(count):
        parsed = parse_checkit_item(blocks[i])
        if not parsed: continue
        
        config = EXAM_MAP[i]
        q_latex = ""
        
        if parsed['type'] == 'parts':
            q_latex += config.get('header_prefix', "")
            q_latex += parsed['intro']
            q_latex += config.get('header_suffix', "")
            q_latex += "\n" + r"\begin{parts}"
            
            pts = config.get('points', [])
            spacing_cfg = config.get('part_spacing', "")
            
            for p_idx, part_text in enumerate(parsed['parts']):
                pt_val = pts[p_idx] if p_idx < len(pts) else 1
                
                if isinstance(spacing_cfg, list):
                    this_space = spacing_cfg[p_idx] if p_idx < len(spacing_cfg) else ""
                else:
                    this_space = spacing_cfg
                
                q_latex += f"\n  \\part[{pt_val}] {part_text} {this_space}"
            
            q_latex += "\n" + r"\end{parts}"
            q_latex += config.get('footer', "")
            
        else: # Single
            q_latex += config.get('header', "")
            
            content = parsed['content']
            
            if 'replacements' in config:
                for (pattern, replacement) in config['replacements']:
                    content = re.sub(pattern, lambda m: replacement, content, flags=re.DOTALL)
            
            q_latex += content
            q_latex += config.get('footer', "")
            
        final_output.append(q_latex)

    with open(output_file, 'w') as f:
        f.write(PREAMBLE)
        for q in final_output:
            f.write(q + "\n\n")
        f.write(POSTAMBLE)

    print(f"Success! Processed {len(final_output)} questions.")

if __name__ == "__main__":
    process_exam("main.tex", "ReadyToPrint_Midterm.tex")