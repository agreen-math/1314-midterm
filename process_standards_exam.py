import re
import sys

# ==========================================
# 1. HELPER FUNCTIONS
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
    """
    Converts CheckIt \stxOuttro{SOLUTION...} blocks 
    into exam class \begin{solution}...\end{solution} blocks.
    """
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

# --- Custom Processors ---

def process_equations(content):
    """Q5-7: Clean up redundant text inside the question body."""
    content = content.replace("Solve for all solutions. Identify any extraneous solutions.", "")
    content = content.replace("Solve the rational equation for all solutions. Identify any extraneous solutions.", "")
    content = content.replace("Solve:", "")
    return content.strip()

def process_graphing_chars(content):
    """Q2: Forces side-by-side layout for characteristics list and graph."""
    content = content.replace("A quadratic function has the characteristics given below.", "")
    
    list_match = re.search(r"(\\begin\{itemize\}.*?\\end\{itemize\})", content, re.DOTALL)
    graph_match = re.search(r"(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})", content, re.DOTALL)
    
    list_code = list_match.group(1) if list_match else ""
    graph_code = graph_match.group(1) if graph_match else ""
    
    if list_code and graph_code:
        return f"""
\\begin{{multicols}}{{2}}
{list_code}
\\columnbreak
\\centering
{graph_code}
\\end{{multicols}}
"""
    return content

def process_properties(content):
    """Q3: Replaces list with Department Table and fixes instructions."""
    func_match = re.search(r"(\\(?:\[|\().*?f\(x\).*?(?:\]|\)))", content)
    func_eqn = func_match.group(1) if func_match else ""
    
    table = r"""
\renewcommand{\arraystretch}{3}
\begin{center}
\begin{tabular}{|l|l|}
\hline
vertex & \hspace{175px} \\ \hline
axis of symmetry & \\ \hline
$x$-intercepts(s) & \\ \hline
$y$-intercept & \\ \hline
domain & \\ \hline
range & \\ \hline
\end{tabular}
\end{center}
"""
    return f"Find the vertex, axis of symmetry, $x$- and $y$- intercepts, domain, and range for the function \n\n {func_eqn} \n\n {table}"

# ==========================================
# 2. EXAM CONFIGURATION
# ==========================================

EXAM_MAP = [
    # Q1: Discriminant
    {
        "checkit_idx": 1,
        "type": "single",
        "pre_block": r"\headerbox{\occ}" + "\n", 
        "header": r"\question[10] \textbf{\textit{Without solving}}, use the discriminant to determine the number and the type of the solutions." + "\n",
        "footer": r"\begin{solution}\end{solution} \vspace{\stretch{3}}\\" + "\n" + r"number of solutions: \fillin \, type of solutions: \fillin[][2.5in]"
    },
    
    # Q2: Graphing Characteristics
    {
        "checkit_idx": 10,
        "type": "single",
        "header": r"\question[5] A quadratic function has the characteristics given below. Use the axis of symmetry to generate two additional points, then use all five points to graph the function." + "\n" + r"\vspace{.25in}" + "\n",
        "footer": r" \vspace{\stretch{1}}",
        "custom_processor": process_graphing_chars
    },

    # Q3: Properties
    {
        "checkit_idx": 9,
        "type": "single",
        "header": r"\newpage" + "\n" + r"\question[5] ",
        "custom_processor": process_properties
    },

    # Q4: Rocket
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

    # Q5: Quadratic Eq
    {
        "checkit_idx": 2,
        "type": "single",
        "pre_block": r"\headerbox{\ocg}" + "\n" + r"\uplevel{In problems \ref{eq_start} through \ref{eq_end}, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n",
        "header": r"\question[10] \label{eq_start} ",
        "footer": r"\begin{solution}\end{solution} \vspace{\stretch{1}}\\\answerline",
        "custom_processor": process_equations
    },

    # Q6: Radical Eq
    {
        "checkit_idx": 3,
        "type": "single",
        "pre_block": r"\newpage" + "\n" + r"\uplevel{In problems \ref{eq_start} through \ref{eq_end}, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n",
        "header": r"\question[10] ",
        "footer": r"\begin{solution}\end{solution} \vspace{\stretch{1}}\\\answerline",
        "custom_processor": process_equations
    },

    # Q7: Rational Eq
    {
        "checkit_idx": 4,
        "type": "single",
        "pre_block": r"\newpage" + "\n" + r"\uplevel{In problems \ref{eq_start} through \ref{eq_end}, solve for \textbf{all} solutions. Identify any extraneous solutions.}" + "\n",
        "header": r"\question[10] \label{eq_end} ",
        "footer": r"\begin{solution}\end{solution} \vspace{\stretch{1}}\\\answerline \newpage",
        "custom_processor": process_equations
    },

    # Q8: Diff Quotient
    {
        "checkit_idx": 8,
        "type": "single",
        "pre_block": r"\headerbox{\ocb}" + "\n",
        "header": r"\question[5] ",
        # Use lambda to safely handle replacement
        "replacements": [(r"Evaluate the difference quotient.*?,", r"Evaluate the difference quotient,")],
        "footer": r"\begin{solution}\end{solution} \vspace{\stretch{1}} \\ \answerline \newpage"
    },

    # Q9: Composition
    {
        "checkit_idx": 7,
        "type": "parts",
        "points": [6, 4],
        "header_prefix": r"\question ", 
        "header_suffix": r"\begin{solution}\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline",
        "footer": r" \newpage"
    },

    # Q10: Inverse (RAW CHECKIT OUTPUT)
    {
        "checkit_idx": 5,
        "type": "single",
        "header": r"\question[10] ",
        "footer": r"\begin{solution}\end{solution} \vspace{\stretch{2}}\\\answerline \newpage"
    },

    # Q11: Transformations (RAW CHECKIT OUTPUT)
    {
        "checkit_idx": 11,
        "type": "single",
        "pre_block": r"\headerbox{\oci}" + "\n",
        # Added points to the question
        "header": r"\question[10] ",
        # No custom processing - keeps minipages, makebox, and blank grid from CheckIt
        "footer": r" \newpage"
    },

    # Q12: Eval Function
    {
        "checkit_idx": 0,
        "type": "parts",
        "points": [3, 3, 4],
        "pre_block": r"\headerbox{\oca}" + "\n",
        "header_prefix": r"\question ", 
        "header_suffix": r"\begin{solution}\end{solution}" + "\n",
        "part_spacing": r" \vspace{\stretch{1}} \\ \answerline"
    }
]

# ==========================================
# 3. MAIN PROCESSOR
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
        return { 'type': 'parts', 'intro': clean_solutions(intro_text), 'parts': clean_parts }
    else:
        return { 'type': 'single', 'content': clean_solutions(outer_content) }

def process_standards_exam(input_file, output_file):
    with open(input_file, 'r') as f:
        full_text = f.read()

    separator = r'\\item\s*%%%%% SpaTeXt Commands %%%%%'
    blocks = re.split(separator, full_text)
    if len(blocks) > 0: blocks = blocks[1:]
    
    parsed_items = []
    for block in blocks:
        item = parse_checkit_item(block)
        if item: parsed_items.append(item)
            
    print(f"Parsed {len(parsed_items)} items.")
    
    final_output = []
    
    for config in EXAM_MAP:
        idx = config.get('checkit_idx')
        if idx >= len(parsed_items): continue
            
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
            
            if 'custom_processor' in config:
                content = config['custom_processor'](content)
            elif 'replacements' in config:
                for (pattern, replacement) in config['replacements']:
                    # Simple regex replace without complex lambda if no backreferences
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            
            q_latex += content
            q_latex += config.get('footer', "")
            
        final_output.append(q_latex)

    with open(output_file, 'w') as f:
        f.write(PREAMBLE)
        for q in final_output:
            f.write(q + "\n\n")
        f.write(POSTAMBLE)

    print(f"Generated {output_file}")

if __name__ == "__main__":
    process_standards_exam("main.tex", "ReadyToPrint_Standards.tex")