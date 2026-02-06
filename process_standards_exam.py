import re
import sys

# ==========================================
# 1. EXAM CONFIGURATION (Standards-Based Order)
# ==========================================

EXAM_MAP = [
    # --- OUTCOME: Quadratic Functions (\occ) ---
    
    # Target Q1: Discriminant (CheckIt #1)
    {
        "checkit_idx": 1,
        "type": "single",
        "pre_block": r"\headerbox{\occ}" + "\n", 
        "header": r"\question[10] \textbf{\textit{Without solving}}, use the discriminant to determine the number and the type of the solutions." + "\n",
        # Added hspace and newlines for spacing
        "footer": r"\\\begin{solution}\end{solution} \vspace{\stretch{3}}\\" + "\n" + r"number of solutions: \fillin \hspace{1in} type of solutions: \fillin[][2.5in]"
    },
    
    # Target Q2: Graphing Characteristics (CheckIt #10)
    {
        "checkit_idx": 10,
        "type": "single",
        "header": r"\question[5] A quadratic function has the characteristics given below. Use the axis of symmetry to generate two additional points, then use all five points to graph the function." + "\n" + r"\vspace{.25in}" + "\n",
        "footer": r" \vspace{\stretch{1}}",
        "replacements": [
            (r"A quadratic function.*", r""), # Strip CheckIt intro
            # Robustly capture the list and the tikzpicture to force side-by-side
            (
                r"(\\begin\{itemize\}.*?\\end\{itemize\})\s*(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})",
                r"\\begin{multicols}{2} \n \1 \n \\columnbreak \n \\centering \n \2 \n \\end{multicols}"
            )
        ]
    },

    # Target Q3: Vertex/Properties (CheckIt #9)
    {
        "checkit_idx": 9,
        "type": "single",
        "header": r"\newpage" + "\n" + r"\question[5] ",
        "replacements": [
            # 1. Replace List with Department Table
            (
                r"\\begin\{itemize\}.*?\\end\{itemize\}", 
                r"\renewcommand{\arraystretch}{3}\begin{table}[h]\begin{tabular}{|l|l|}\hline vertex & \hspace{175px} \\ \hline axis of symmetry & \\ \hline $x$-intercepts(s) & \\ \hline $y$-intercept & \\ \hline domain & \\ \hline range & \\ \hline \end{tabular}\end{table}"
            ),
            # 2. Update Instructions & Force Line Break before Function
            (
                r"Find each of the properties below for the given function:(.*?)(\\(?:\[|\().*?(?:\]|\)))", 
                r"Find the vertex, axis of symmetry, $x$- and $y$- intercepts, domain, and range for the function \n \\[\n \2 \n \\]"
            ),
            (r"Consider the function:", r"")
        ]
    },

    # Target Q4: Rocket (CheckIt #6)
    {
        "checkit_idx": 6,
        "type": "parts",
        "points": [2, 2, 1],
        "header_prefix": r"\newpage" + "\n" + r"\question ",
        "part_spacing": [
            r" \vspace{\stretch{1}} \\ \answerline", 
            r" \vspace{\stretch{1}} \\ \answerline", 
            r" \fillwithlines{1in}"
        ],
        "footer": r" \newpage"
    },

    # --- OUTCOME: Equations (\ocg) ---

    # Target Q5: Quadratic Eq (CheckIt #2)
    {
        "checkit_idx": 2,
        "type": "single",
        # Updated Instructions to bold "all"
        "pre_block": r"\headerbox{\ocg}" + "\n" + r"\uplevel{In problems \ref{eq_start} through \ref{eq_end}, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n",
        # Removed "Solve:" text
        "header": r"\question[10] \label{eq_start} ",
        "footer": r"\\\begin{solution}\end{solution} \vspace{\stretch{1}}\\\answerline"
    },

    # Target Q6: Radical Eq (CheckIt #3)
    {
        "checkit_idx": 3,
        "type": "single",
        "header": r"\newpage" + "\n" + r"\uplevel{In problems \ref{eq_start} through \ref{eq_end}, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n" + r"\question[10] ",
        "footer": r"\\\begin{solution}\end{solution} \vspace{\stretch{1}}\\\answerline"
    },

    # Target Q7: Rational Eq (CheckIt #4)
    {
        "checkit_idx": 4,
        "type": "single",
        "header": r"\newpage" + "\n" + r"\uplevel{In problems \ref{eq_start} through \ref{eq_end}, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n" + r"\question[10] \label{eq_end} ",
        "footer": r"\\\begin{solution}\end{solution} \vspace{\stretch{1}}\\\answerline \newpage"
    },

    # --- OUTCOME: Combining & Undoing (\ocb) ---

    # Target Q8: Diff Quotient (CheckIt #8)
    {
        "checkit_idx": 8,
        "type": "single",
        "pre_block": r"\headerbox{\ocb}" + "\n",
        "header": r"\question[5] ",
        # Remove redundant intro text
        "replacements": [(r"Evaluate the difference quotient.*?,", r"Evaluate the difference quotient,")],
        "footer": r"\\\begin{solution}\end{solution} \vspace{\stretch{1}} \\ \answerline \newpage"
    },

    # Target Q9: Composition (CheckIt #7)
    {
        "checkit_idx": 7,
        "type": "parts",
        "points": [6, 4],
        "header_prefix": r"\question ", 
        "header_suffix": r"\\\begin{solution}\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline",
        "footer": r" \newpage"
    },

    # Target Q10: Inverse (CheckIt #5)
    {
        "checkit_idx": 5,
        "type": "single",
        "header": r"\question[10] ",
        # Reformat: "Given that f(x)=... is one-to-one..."
        "replacements": [
            (
                r"Given that the function is one-to-one, find the inverse function.*?\.\s*(\\(?:\[|\().*?(?:\]|\)))",
                r"Given that \1 is one-to-one, find $f^{-1}(x)$."
            )
        ],
        "footer": r"\\\begin{solution}\end{solution} \vspace{\stretch{2}}\\\answerline \newpage"
    },

    # --- OUTCOME: Graphing (\oci) ---

    # Target Q11: Transformations (CheckIt #11)
    {
        "checkit_idx": 11,
        "type": "single",
        "pre_block": r"\headerbox{\oci}" + "\n",
        "header": r"\question[10] ",
        "replacements": [
            # 1. Move g(x) to its own line
            (
                r"(\\(?:\[|\().*?g\(x\).*?(?:\]|\)))",
                r"\n\[ \1 \]\n"
            ),
            # 2. Remove extra instruction text
            (r"Identify transformations and graph.", r""),
            # 3. Extract the problem graph (first tikzpicture) and discard the CheckIt layout/grid
            (
                r"\\noindent\\makebox.*?(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}).*?\\end\{minipage\} \}", 
                r"\\begin{multicols}{2} \n \\centering \n \1 \n \\columnbreak \n \\includegraphics[width=3in]{General Images/blankgraph.PNG} \n \\end{multicols}"
            )
        ],
        "footer": r" \newpage"
    },

    # --- OUTCOME: Properties of Functions (\oca) ---

    # Target Q12: Eval Function (CheckIt #0)
    {
        "checkit_idx": 0,
        "type": "parts",
        "points": [3, 3, 4],
        "pre_block": r"\headerbox{\oca}" + "\n",
        "header_prefix": r"\question ", 
        "header_suffix": r"\\\begin{solution}\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline"
    }
]

# ==========================================
# 2. TARGET PREAMBLE
# ==========================================
PREAMBLE = r"""\documentclass[11pt]{exam}

%%%%%%%%%%%%%%%%%%%%%%%%%% Preamble %%%%%%%%%%%%%%%%%%%%%%%%%% 
\input{Admin/1. Packages}
\input{Admin/2. WEB Course Info}
\input{Admin/3. WEB Outcomes}
\input{Admin/4. Commands}
\input{Admin/8. Fonts}

%%%%%%%%%%%%% Exam Information  %%%%%%%%%%%%%%%%%%%%%%%%%% 

\newcommand{\exam}{Midterm Exam}
\newcommand{\TimeLimit}{2 hours}

\begin{document}

%%%% Show/Don't Show Points %%%% 
\addpoints
% \pointformat{}
% \nopointsmargin

%%%% Show/Don't Show Solutions %%%% 
%\printanswers
\noprintanswers

%%%%%%%%%%%%%%%%%%%%%%%%%% Scratch Paper %%%%%%%%%%%%%%%%%%%%%%%%%%
\blankpage

%%%%%%%%%%%%%%%% Cover Page %%%%%%%%%%%%%%%% 
\input{Admin/6. CoverPage}

\newpage

%%%% Questions %%%%
\begin{questions}
"""

POSTAMBLE = r"""
\newpage
\headerbox{Bonus Question}
\input{Admin/7. Extra Credit}

\end{questions}

%%%%%%%%%%%%%%%%%%%%%%%%%% Scratch Paper %%%%%%%%%%%%%%%%%%%%%%%%%%
\blankpage

\end{document}
"""

# ==========================================
# 3. PARSING LOGIC
# ==========================================

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
        
        # Strip "SOLUTION" text
        inner_text = re.sub(r'^\s*SOLUTION\s*', '', inner_text, flags=re.IGNORECASE | re.MULTILINE).strip()
        
        # Wrap in exam class solution
        new_block = r'\begin{solution}' + "\n" + inner_text + "\n" + r'\end{solution}'
        content = content[:start_pos] + new_block + content[end_pos:]
    return content.strip()

def parse_checkit_item(raw_block):
    # Locate outer knowl
    match = re.search(r'\\stxKnowl\s*\{', raw_block)
    if not match: return None
    outer_content, _ = get_braced_content(raw_block, match.end() - 1)
    
    # Detect Parts (enumerate)
    if r'\begin{enumerate}' in outer_content:
        split_parts = re.split(r'\\begin\{enumerate\}', outer_content, 1)
        intro_text = split_parts[0].strip()
        enum_body = split_parts[1].split(r'\end{enumerate}')[0]
        
        # Split items
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
# 4. MAIN PROCESSOR
# ==========================================

def process_standards_exam(input_file, output_file):
    with open(input_file, 'r') as f:
        full_text = f.read()

    separator = r'\\item\s*%%%%% SpaTeXt Commands %%%%%'
    blocks = re.split(separator, full_text)
    if len(blocks) > 0: blocks = blocks[1:]
    
    # Store parsed items in a list
    parsed_items = []
    for block in blocks:
        item = parse_checkit_item(block)
        if item:
            parsed_items.append(item)
            
    print(f"Parsed {len(parsed_items)} items from CheckIt output.")
    
    final_output = []
    
    # Map CheckIt items to Target Layout
    for config in EXAM_MAP:
        idx = config.get('checkit_idx')
        
        if idx >= len(parsed_items):
            print(f"Warning: Configuration requests Item {idx}, but only {len(parsed_items)} items found.")
            continue
            
        parsed = parsed_items[idx]
        q_latex = config.get('pre_block', "") 
        
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
            
            # Apply replacements
            if 'replacements' in config:
                for (pattern, replacement) in config['replacements']:
                    # Use lambda to prevent backslash escape issues
                    content = re.sub(pattern, lambda m: replacement.replace(r'\1', m.group(1)).replace(r'\2', m.group(2)) if r'\1' in replacement or r'\2' in replacement else replacement, content, flags=re.DOTALL)
            
            q_latex += content
            q_latex += config.get('footer', "")
            
        final_output.append(q_latex)

    # Write Output
    with open(output_file, 'w') as f:
        f.write(PREAMBLE)
        for q in final_output:
            f.write(q + "\n\n")
        f.write(POSTAMBLE)

    print(f"Generated Standards-Based Exam: {output_file}")

if __name__ == "__main__":
    process_standards_exam("main.tex", "ReadyToPrint_Standards.tex")