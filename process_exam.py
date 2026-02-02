import re
import sys

# ==========================================
# 1. EXAM MAP (Order is strictly guaranteed)
# ==========================================
EXAM_MAP = [
    # Q1: Evaluate Function (Parts)
    {
        "type": "parts",
        "points": [3, 3, 4],
        "header_prefix": r"\question ", 
        "header_suffix": r"\\\begin{solution}\ci\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline"
    },
    # Q2: Discriminant (Single)
    {
        "type": "single",
        "header": r"\question[10] \textbf{\textit{Without solving}}, use the discriminant to determine the number and the type of the solutions.\\\begin{solution}\ciii\end{solution} \vspace{\stretch{3}}\\" + "\n" + r"number of solutions: \fillin \hspace{\stretch{1}} type of solutions: \fillin[][2.5in] \newpage" + "\n" + r"% Original: "
    },
    # Q3: Quadratic (Single)
    {
        "type": "single",
        "header": r"\uplevel{For the following questions, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n" + r"\question[10] Solve: ",
        "footer": r"\\\begin{solution}\cii\end{solution} \vspace{\stretch{1}}\\\,\answerline"
    },
    # Q4: Radical (Single)
    {
        "type": "single",
        "header": r"\question[10] Solve: ",
        "footer": r"\\\begin{solution}\cii\end{solution} \vspace{\stretch{1}}\\\,\answerline"
    },
    # Q5: Rational (Single)
    {
        "type": "single",
        "header": r"\question[10] Solve: ",
        "footer": r"\\\begin{solution}\cii\end{solution} \vspace{\stretch{1}}\\\,\answerline \newpage"
    },
    # Q6: Inverse (Single)
    {
        "type": "single",
        "header": r"\question[10] ",
        "footer": r"\\\begin{solution}\ci\end{solution} \vspace{\stretch{2}}\\\,\answerline \newpage"
    },
    # Q7: Rocket (Parts)
    {
        "type": "parts",
        "points": [2, 2, 1],
        "header_prefix": r"\question ",
        "part_spacing": r" \fillwithlines{0.5in}"
    },
    # Q8: Composition (Parts)
    {
        "type": "parts",
        "points": [6, 4],
        "header_prefix": r"\question Find the following compositions:",
        "header_suffix": r"\\\begin{solution}\ci\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline",
        "footer": r" \newpage"
    },
    # Q9: Difference Quotient (Single)
    {
        "type": "single",
        "header": r"\question[5] Evaluate the difference quotient.\\\begin{solution}\ci\end{solution}" + "\n",
        "footer": r" \vspace{\stretch{1}} \\ \answerline \newpage"
    },
    # Q10: Vertex (Single)
    {
        "type": "single",
        "header": r"\question[5] Find the vertex and properties." + "\n"
    },
    # Q11: Graphing (Single)
    {
        "type": "single",
        "header": r"\question[5] Use the characteristics to graph." + "\n",
        "footer": r" \newpage"
    },
    # Q12: Transformations (Single)
    {
        "type": "single",
        "header": r"\question[10] Identify transformations and graph." + "\n",
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
    """
    Finds the content of the curly brace group starting at start_index.
    Returns (content, end_index).
    """
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
    """
    Converts \stxOuttro{ SOLUTION ... } into \begin{solution}...\end{solution}.
    """
    # Remove junk
    content = re.sub(r'\\stxTitle\{.*?\}', '', content)
    
    # Process Outtros
    while True:
        match = re.search(r'\\stxOuttro\s*\{', content)
        if not match: break
        
        start_pos = match.start()
        open_brace_pos = match.end() - 1
        
        inner_text, end_pos = get_braced_content(content, open_brace_pos)
        
        # Remove "SOLUTION" header inside
        inner_text = re.sub(r'^\s*SOLUTION\s*', '', inner_text, flags=re.IGNORECASE | re.MULTILINE).strip()
        
        # Wrap in exam solution environment
        new_block = r'\begin{solution}' + "\n" + inner_text + "\n" + r'\end{solution}'
        
        content = content[:start_pos] + new_block + content[end_pos:]
        
    return content.strip()

def parse_checkit_item(raw_block):
    """
    Parses a top-level item block (separated by '%%%%% SpaTeXt Commands %%%%%').
    Detects if it has parts (enumerate) or is single.
    """
    # 1. Extract the Outer Knowl Content
    match = re.search(r'\\stxKnowl\s*\{', raw_block)
    if not match: return None
        
    outer_content, _ = get_braced_content(raw_block, match.end() - 1)
    
    # 2. Check for Enumerate (Parts)
    if r'\begin{enumerate}' in outer_content:
        # Split Intro from Parts
        split_parts = re.split(r'\\begin\{enumerate\}', outer_content, 1)
        intro_text = split_parts[0].strip()
        
        # Get the body inside enumerate
        enum_body = split_parts[1].split(r'\end{enumerate}')[0]
        
        # Split items
        raw_parts = re.split(r'\\item', enum_body)
        clean_parts = []
        
        for p in raw_parts:
            if not p.strip(): continue
            
            # CRITICAL: Each part is wrapped in its own \stxKnowl
            p_match = re.search(r'\\stxKnowl\s*\{', p)
            if p_match:
                # Extract content of this specific part
                part_content, _ = get_braced_content(p, p_match.end()-1)
                # Convert solution INSIDE this part
                clean_parts.append(clean_solutions(part_content))
            else:
                # Fallback if structure is weird
                clean_parts.append(clean_solutions(p))
                
        return {
            'type': 'parts',
            'intro': clean_solutions(intro_text),
            'parts': clean_parts
        }
    else:
        # Single Question
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

    # Split by the user's guaranteed delimiter
    separator = r'\\item\s*%%%%% SpaTeXt Commands %%%%%'
    blocks = re.split(separator, full_text)
    
    # Skip preamble (chunk 0)
    if len(blocks) > 0:
        blocks = blocks[1:]
    
    print(f"Found {len(blocks)} Question Blocks.")
    
    final_output = []
    
    # Process blocks in order according to EXAM_MAP
    count = min(len(blocks), len(EXAM_MAP))
    
    for i in range(count):
        parsed = parse_checkit_item(blocks[i])
        if not parsed: continue
        
        config = EXAM_MAP[i]
        q_latex = ""
        
        if parsed['type'] == 'parts':
            # Intro
            q_latex += config.get('header_prefix', "")
            q_latex += parsed['intro']
            q_latex += config.get('header_suffix', "")
            
            # Parts Environment
            q_latex += "\n" + r"\begin{parts}"
            
            pts = config.get('points', [])
            spacing = config.get('part_spacing', "")
            
            # Loop through parts found
            for p_idx, part_text in enumerate(parsed['parts']):
                pt_val = pts[p_idx] if p_idx < len(pts) else 1
                q_latex += f"\n  \\part[{pt_val}] {part_text} {spacing}"
            
            q_latex += "\n" + r"\end{parts}"
            q_latex += config.get('footer', "")
            
        else: # Single
            q_latex += config.get('header', "")
            q_latex += parsed['content']
            q_latex += config.get('footer', "")
            
        final_output.append(q_latex)

    # Write File
    with open(output_file, 'w') as f:
        f.write(PREAMBLE)
        for q in final_output:
            f.write(q + "\n\n")
        f.write(POSTAMBLE)

    print(f"Success! Processed {len(final_output)} questions.")

if __name__ == "__main__":
    process_exam("main.tex", "ReadyToPrint_Midterm.tex")