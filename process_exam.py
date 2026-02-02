import re
import sys

# ==========================================
# 1. EXAM CONFIGURATION (The "Map")
# ==========================================
# This list corresponds 1-to-1 with the questions in your CheckIt bank order.
# We don't need indices anymore; just the order 0, 1, 2... 

EXAM_MAP = [
    # --- Q1: Evaluate Function ---
    {
        "type": "parts",
        "points": [3, 3, 4],
        "header_prefix": r"\question ", 
        "header_suffix": r"\\\begin{solution}\ci\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline"
    },
    # --- Q2: Discriminant ---
    {
        "type": "single",
        "header": r"\question[10] \textbf{\textit{Without solving}}, use the discriminant to determine the number and the type of the solutions.\\\begin{solution}\ciii\end{solution} \vspace{\stretch{3}}\\" + "\n" + r"number of solutions: \fillin \hspace{\stretch{1}} type of solutions: \fillin[][2.5in] \newpage" + "\n" + r"% Original: "
    },
    # --- Q3: Quadratic ---
    {
        "type": "single",
        "header": r"\uplevel{For the following questions, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n" + r"\question[10] Solve: ",
        "footer": r"\\\begin{solution}\cii\end{solution} \vspace{\stretch{1}}\\\,\answerline"
    },
    # --- Q4: Radical ---
    {
        "type": "single",
        "header": r"\question[10] Solve: ",
        "footer": r"\\\begin{solution}\cii\end{solution} \vspace{\stretch{1}}\\\,\answerline"
    },
    # --- Q5: Rational ---
    {
        "type": "single",
        "header": r"\question[10] Solve: ",
        "footer": r"\\\begin{solution}\cii\end{solution} \vspace{\stretch{1}}\\\,\answerline \newpage"
    },
    # --- Q6: Inverse ---
    {
        "type": "single",
        "header": r"\question[10] ",
        "footer": r"\\\begin{solution}\ci\end{solution} \vspace{\stretch{2}}\\\,\answerline \newpage"
    },
    # --- Q7: Rocket ---
    {
        "type": "parts",
        "points": [2, 2, 1],
        "header_prefix": r"\question ",
        "part_spacing": r" \fillwithlines{0.5in}" # Special spacing for Rocket
    },
    # --- Q8: Composition ---
    {
        "type": "parts",
        "points": [6, 4],
        "header_prefix": r"\question Find the following compositions:",
        "header_suffix": r"\\\begin{solution}\ci\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline",
        "footer": r" \newpage"
    },
    # --- Q9: Difference Quotient ---
    {
        "type": "single",
        "header": r"\question[5] Evaluate the difference quotient.\\\begin{solution}\ci\end{solution}" + "\n",
        "footer": r" \vspace{\stretch{1}} \\ \answerline \newpage"
    },
    # --- Q10: Vertex ---
    {
        "type": "single",
        "header": r"\question[5] Find the vertex and properties." + "\n"
    },
    # --- Q11: Graphing ---
    {
        "type": "single",
        "header": r"\question[5] Use the characteristics to graph." + "\n",
        "footer": r" \newpage"
    },
    # --- Q12: Transformations ---
    {
        "type": "single",
        "header": r"\question[10] Identify transformations and graph." + "\n",
        "footer": r" \newpage"
    }
]

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

# ==========================================
# 2. PARSING HELPERS
# ==========================================

def get_braced_content(text, start_index=0):
    """
    Given text and the index of an opening brace '{', 
    finds the matching closing brace '}' handling nesting.
    Returns: (content_inside, index_after_closing_brace)
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
    Converts CheckIt \stxOuttro{SOLUTION ...} to \begin{solution}...\end{solution}
    """
    # Remove junk macros
    content = re.sub(r'\\stxTitle\{.*?\}', '', content)
    
    # Process Outtros
    while r'\stxOuttro' in content:
        match = re.search(r'\\stxOuttro\s*\{', content)
        if not match: break
        
        start_pos = match.start()
        open_brace_pos = match.end() - 1
        
        inner_text, end_pos = get_braced_content(content, open_brace_pos)
        
        # Clean "SOLUTION" label
        inner_text = re.sub(r'^\s*SOLUTION\s*', '', inner_text, flags=re.IGNORECASE).strip()
        
        new_block = r'\begin{solution}' + "\n" + inner_text + "\n" + r'\end{solution}'
        content = content[:start_pos] + new_block + content[end_pos:]
        
    return content.strip()

def parse_checkit_item(raw_block):
    """
    Parses a top-level CheckIt item block.
    Returns a dict: {'type': 'single'|'parts', 'content': ..., 'parts': [...], 'intro': ...}
    """
    # 1. Extract the main \stxKnowl content
    match = re.search(r'\\stxKnowl\s*\{', raw_block)
    if not match:
        return None
        
    outer_content, _ = get_braced_content(raw_block, match.end() - 1)
    
    # 2. Check structure (Single vs Parts)
    if r'\begin{enumerate}' in outer_content:
        # Split into Intro and Parts
        parts = re.split(r'\\begin\{enumerate\}', outer_content, 1)
        intro_text = parts[0].strip()
        
        # Isolate the enumerate body
        enum_body = parts[1].split(r'\end{enumerate}')[0]
        
        # Split by \item to get parts
        # We ignore the first split if it's empty
        raw_parts = re.split(r'\\item', enum_body)
        clean_parts = []
        for p in raw_parts:
            if not p.strip(): continue
            
            # Peel off inner \stxKnowl if present (standard CheckIt structure)
            p_match = re.search(r'\\stxKnowl\s*\{', p)
            if p_match:
                p_content, _ = get_braced_content(p, p_match.end()-1)
                clean_parts.append(clean_solutions(p_content))
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

    # 1. Split by the User's Magic Separator
    # This guarantees we get exactly the Question Blocks
    separator = r'\\item\s*%%%%% SpaTeXt Commands %%%%%'
    blocks = re.split(separator, full_text)
    
    # Remove preamble (chunk 0)
    if len(blocks) > 0:
        blocks = blocks[1:]
    
    print(f"Found {len(blocks)} Question Blocks.")
    
    # 2. Generate LaTeX
    final_output = []
    
    # Iterate safely up to the number of configured questions
    count = min(len(blocks), len(EXAM_MAP))
    
    for i in range(count):
        parsed = parse_checkit_item(blocks[i])
        config = EXAM_MAP[i]
        
        q_latex = ""
        
        # Handle 'Parts' type questions
        if parsed['type'] == 'parts':
            # Header + Intro
            q_latex += config.get('header_prefix', "") 
            q_latex += parsed['intro']
            q_latex += config.get('header_suffix', "") # e.g. Solution bucket
            
            q_latex += "\n" + r"\begin{parts}"
            
            # Add parts
            points = config.get('points', [])
            spacing = config.get('part_spacing', "")
            
            for p_idx, part_content in enumerate(parsed['parts']):
                pt_val = points[p_idx] if p_idx < len(points) else 1
                q_latex += f"\n  \\part[{pt_val}] {part_content} {spacing}"
            
            q_latex += "\n" + r"\end{parts}"
            q_latex += config.get('footer', "")

        # Handle 'Single' type questions
        else:
            q_latex += config.get('header', "")
            q_latex += parsed['content']
            q_latex += config.get('footer', "")
            
        final_output.append(q_latex)

    # 3. Write
    with open(output_file, 'w') as f:
        f.write(PREAMBLE)
        for q in final_output:
            f.write(q + "\n\n")
        f.write(POSTAMBLE)

    print(f"Successfully generated {len(final_output)} questions to {output_file}")

if __name__ == "__main__":
    process_exam("main.tex", "ReadyToPrint_Midterm.tex")