import re
import argparse

# ==========================================
# 1. CORE UTILITIES & VACUUM EXTRACTORS
# ==========================================

def escape_currency(text):
    """Safely escapes dollar signs used for money so they do not trigger math mode."""
    return re.sub(r'(?<!\\)\$(\d)', r'\\$\1', text)

def get_braced_content(text, start_index):
    """Extracts content within nested LaTeX braces. Returns (inner_text, absolute_end_index)."""
    if start_index >= len(text) or text[start_index] != "{":
        return None, start_index
    count = 1
    for i in range(start_index + 1, len(text)):
        if text[i] == "{": count += 1
        elif text[i] == "}": count -= 1
        if count == 0:
            return text[start_index + 1:i], i + 1
    return None, len(text)

def extract_solutions_and_clean(raw_block):
    """
    Surgically unwraps CheckIt tags, extracts solutions, and cleans the text
    to prevent dangling closing braces and formatting cruft.
    """
    clean_text = raw_block
    
    while True:
        match = re.search(r'\\stxKnowl\s*\{', clean_text)
        if not match: break
        
        start = match.end() - 1
        inner, end_idx = get_braced_content(clean_text, start)
        
        if inner is not None:
            clean_text = clean_text[:match.start()] + inner + clean_text[end_idx:]
        else:
            clean_text = clean_text.replace(r'\stxKnowl', '')
            break
            
    sols = []
    while True:
        match = re.search(r'\\stxOuttro\s*\{', clean_text)
        if not match: break
        
        start = match.end() - 1
        inner, end_idx = get_braced_content(clean_text, start)
        
        if inner is not None:
            clean_sol = re.sub(r'^\s*SOLUTION\s*:?\s*', '', inner, flags=re.IGNORECASE).strip()
            if clean_sol: sols.append(escape_currency(clean_sol))
            clean_text = clean_text[:match.start()] + clean_text[end_idx:]
        else:
            clean_text = clean_text.replace(r'\stxOuttro', '')
            break
            
    clean_text = re.sub(r'\\stxTitle\s*\{.*?\}', '', clean_text)
    return clean_text, sols

def extract_math(text):
    """Finds all LaTeX math blocks universally and deduplicates them."""
    text_no_tikz = re.sub(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', '', text, flags=re.DOTALL)
    matches = re.findall(r'\\\[(.*?)\\\]|\\\((.*?)\\\)|\$(.*?)\$|<m>(.*?)</m>', text_no_tikz, re.DOTALL)
    results = []
    
    for m in matches:
        for group in m:
            if group:
                g_strip = group.strip()
                if g_strip not in results:
                    results.append(g_strip)
                break
                
    loose_envs = re.findall(r'(\\begin\{(matrix|bmatrix|pmatrix|vmatrix|Vmatrix|array|align\*?|equation\*?|cases|system)\}.*?\\end\{\2\})', text_no_tikz, re.DOTALL)
    for env in loose_envs:
        is_dup = any(env[0] in r or r in env[0] for r in results)
        if not is_dup:
            results.append(env[0].strip())
            
    return results

def format_math(m):
    """Wraps math in inline displaystyle and converts align* to aligned."""
    if not m: return ""
    m = m.replace(r'\begin{align*}', r'\begin{aligned}').replace(r'\end{align*}', r'\end{aligned}')
    m = m.replace(r'\begin{align}', r'\begin{aligned}').replace(r'\end{align}', r'\end{aligned}')
    return f"\\(\\displaystyle{{ {m} }}\\)"

def extract_func(text):
    """Robustly extracts the longest relevant function equation."""
    maths = extract_math(text)
    for m in maths:
        if re.search(r'[fghpP]\(x\)\s*=', m):
            return m
    valid_maths = [m for m in maths if 'x' in m]
    if valid_maths:
        best_match = max(valid_maths, key=len)
        if '=' in best_match:
            return best_match
        else:
            return f"f(x) = {best_match}"
    return "f(x)"

def get_word_problem_prompt(text):
    """Aggressively flattens lists and cleans word problems from CheckIt cruft."""
    text = re.sub(r'\\(?:provide|renew)command\{\\stx.*?\}(?:\{\}|\[1\]\{.*?\})', '', text)
    text = re.sub(r'(?<!\\)%.*', '', text) 
    text = text.replace(r'\newpage', '')
    
    text = re.sub(r'\\begin\{(itemize|enumerate)\}', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\\end\{(itemize|enumerate)\}', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\\item', ' ', text)
    
    text = re.sub(r'([a-zA-Z\s]+):\s*(?:_{3,}|\\underline\{.*?\})', '', text).strip()
    text = re.sub(r'\s+', ' ', text)
    
    return escape_currency(text.strip())

# ==========================================
# 2. THE 16 NON-COMPREHENSIVE SBG TEMPLATES
# ==========================================

def build_q1(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m or '(' in m]
    if len(eqs) < 2: eqs = maths
    
    math1 = format_math(eqs[0]) if len(eqs) > 0 else ""
    math2 = format_math(eqs[1]) if len(eqs) > 1 else ""
    sol1 = sols[0] if len(sols) > 0 else ""
    sol2 = sols[1] if len(sols) > 1 else ""
    
    return f"""%% Properties of Functions %%
\\headerbox{{\\oca}}

\\question
Find the domain and range for each of the following functions.\\\\
\\begin{{parts}}
    \\part[5]{{{math1}}}\\\\
    
         \\hspace{{\\stretch{{1}}}}domain: \\fillin[][2in]\\\\\\vspace{{12pt}}
        
         \\hspace{{\\stretch{{1}}}}range: \\fillin[][2in]\\\\
\\begin{{solution}}
{sol1}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}
    \\part[5]{{{math2}}}\\\\ 
    
         \\hspace{{\\stretch{{1}}}}domain: \\fillin[][2in]\\\\\\vspace{{12pt}}
        
         \\hspace{{\\stretch{{1}}}}range: \\fillin[][2in]\\\\
\\begin{{solution}}
{sol2}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}

\\end{{parts}}

\\label{{exact-endoca}}
\\newpage"""

def build_q2(item, sols):
    func = format_math(extract_func(item))
    sol = sols[0] if sols else ""
    
    return f"""%% Polynomial Functions %%
\\headerbox{{\\ocd}}
\\label{{exact-startocd}}

\\question[10] Fill in the table below with the zeros of the polynomial, their multiplicities and the behavior of the graph of the function around each zero. You may or may not use all of the rows in the table.\\\\

{func}

\\hspace{{\\stretch{{1}}}}
\\renewcommand{{\\arraystretch}}{{3}}
\\begin{{tabular}}{{|p{{20mm}}|p{{25mm}}|p{{20mm}}|}}\\hline
\\textbf{{Zero}} & \\textbf{{Multiplicity}} & \\textbf{{Behavior}}\\\\ \\hline
 & & \\\\ \\hline
 & & \\\\ \\hline
 & & \\\\ \\hline
 & & \\\\ \\hline
 & & \\\\ \\hline
\\end{{tabular}}

\\begin{{solution}}
{sol}
\\end{{solution}}
\\newpage"""

def build_q3(item, sols):
    tikz_match = re.search(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', item, re.DOTALL)
    tikz_math = f"\\begin{{center}}\n{tikz_match.group(0)}\n\\end{{center}}" if tikz_match else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question
Use the image of a polynomial below to answer the questions that follow.\\\\
\\begin{{solution}}
{sol}
\\end{{solution}}

{tikz_math}

\\begin{{parts}}
    \\part[1] Is the degree of the polynomial even or odd? \\\\\\vspace{{12pt}}

    \\begin{{oneparcheckboxes}}
    \\choice even
    \\choice odd
    \\end{{oneparcheckboxes}}\\\\\\vspace{{.125in}}
    \\part[1\\half] Is the lead coefficient of the polynomial positive or negative?\\\\\\vspace{{12pt}}
 
    \\begin{{oneparcheckboxes}}
    \\choice positive
    \\choice negative
    \\end{{oneparcheckboxes}}\\\\\\vspace{{.125in}}
    \\part[1] Is the constant of the polynomial positive or negative? \\\\\\vspace{{12pt}}
    
    \\begin{{oneparcheckboxes}}
    \\choice positive
    \\choice negative
    \\end{{oneparcheckboxes}}\\\\\\vspace{{.125in}}
    \\part[1\\half] What is the minimum degree? \\\\\\vspace{{12pt}}
    
    \\fillin
    
\\end{{parts}}

\\label{{exact-endocd}}

\\newpage"""

def build_q4(item, sols):
    func = format_math(extract_func(item))
    sol = sols[0] if sols else ""
    
    return f"""%% Rational Functions %%
\\headerbox{{\\oce}}
\\label{{exact-startoce}}

\\question[5]
List all of the vertical, horizontal, and oblique asymptotes of the rational function.\\\\

{func}

\\hspace{{\\stretch{{1}}}}
\\renewcommand{{\\arraystretch}}{{3}}
	\\begin{{tabular}}{{|c|c|}}
		\\hline
		\\textbf{{Asymptotes}}  & \\textbf{{Equation}} \\\\ \\hline
		Vertical   & \\hspace{{50mm}}         \\\\ \\hline
		Horizontal &          \\\\ \\hline
		Oblique    &          \\\\ \\hline
	\\end{{tabular}}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}
\\label{{exact-endoce}}

\\newpage"""

def build_q5(item, sols):
    match = re.search(r'(\\begin\{(?:array|tabular)\}.*?\\end\{(?:array|tabular)\})', item, re.DOTALL)
    math = match.group(1) if match else ""
    math = re.sub(r'\\rule\[.*?\]\{.*?\}\{.*?\}', '', math)
    math = math.replace(r'\hspace{3cm}', r'\hspace{75mm}')
    math = math.replace(r'\begin{tabular}', r'\begin{array}').replace(r'\end{tabular}', r'\end{array}')
    sol = sols[0] if sols else ""
    
    return f"""%% Exponential \& Logarithmic Functions %%
\\headerbox{{\\ocf}}
\\label{{exact-startocf}}

\\question[5]
Fill in the table to give an equivalent equation in the specified form.\\\\
{{\\centering {{\\renewcommand{{\\arraystretch}}{{3}}
\\[
{math}
\\]
}}}}

\\begin{{solution}}
{sol}
\\end{{solution}}"""

def build_q6(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if 'log' in m or 'ln' in m]
    if len(eqs) < 2: eqs = maths
    
    math1 = format_math(eqs[0]) if len(eqs) > 0 else ""
    math2 = format_math(eqs[1]) if len(eqs) > 1 else ""
    sol1 = sols[0] if len(sols) > 0 else ""
    sol2 = sols[1] if len(sols) > 1 else ""
    
    return f"""\\question Use properties of logarithms to expand or condense the logarithmic expression as specified.
\\begin{{parts}}
    \\part[5] Rewrite as the sum or difference of logarithms. Express all powers as factors.\\\\
    
    {math1}
    
\\hspace{{\\stretch{{1}}}}Answer: \\fillin[][2in]
\\begin{{solution}}
{sol1}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}

    \\part[5] Rewrite as a single logarithm. Express all factors as powers.\\\\
    
    {math2}
    
\\hspace{{\\stretch{{1}}}}Answer: \\fillin[][2in]
\\begin{{solution}}
{sol2}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}

\\end{{parts}}

\\label{{exact-endocf}}

\\newpage"""

def build_q7(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""%% Equations %%
\\headerbox{{\\ocg}}

\\uplevel{{In problems \\ref{{exact-startocg}} through~\\ref{{exact-endocgextra}}, solve for $x$ and identify any extraneous solutions.}}

\\question[6] {math}\\\\
    
         \\hspace{{\\stretch{{1}}}}solutions: \\fillin[][2in]\\\\\\vspace{{12pt}}
        
         \\hspace{{\\stretch{{1}}}}extraneous solutions: \\fillin[][2in]\\\\
\\begin{{solution}}
{sol}
\\end{{solution}}

\\label{{exact-startocg}}

\\newpage"""

def build_q8(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\uplevel{{In problems \\ref{{exact-startocg}} through~\\ref{{exact-endocgextra}}, solve for $x$ and identify any extraneous solutions.}}

\\question[6] {math}\\\\

         \\hspace{{\\stretch{{1}}}}solutions: \\fillin[][2in]\\\\\\vspace{{12pt}}
        
         \\hspace{{\\stretch{{1}}}}extraneous solutions: \\fillin[][2in]\\\\
\\begin{{solution}}
{sol}
\\end{{solution}}

\\label{{exact-endocgextra}}

\\newpage"""

def build_q9(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\uplevel{{In problems \\ref{{exact-startocg}} through~\\ref{{exact-endocgextra}}, solve for $x$ and identify any extraneous solutions.}}

\\question[6] {math}\\\\

         \\hspace{{\\stretch{{1}}}}solutions: \\fillin[][2in]\\\\\\vspace{{12pt}}
        
         \\hspace{{\\stretch{{1}}}}extraneous solutions: \\fillin[][2in]\\\\
\\begin{{solution}}
{sol}
\\end{{solution}}

\\newpage"""

def build_q10(item, sols):
    sol = sols[0] if sols else ""
    rate_match = re.search(r'(\d+(?:\.\d+)?)\s*\\?%', item)
    initial_match = re.search(r'initial deposit of\s*(?:\\?\$)?\s*([0-9,]+)', item, re.IGNORECASE)
    final_match = re.search(r'reach\s*(?:\\?\$)?\s*([0-9,]+)', item, re.IGNORECASE)
    freq_match = re.search(r'compounded\s+(monthly|quarterly|annually|semiannually|daily|continuously)', item, re.IGNORECASE)
    
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    math = format_math(max(eqs, key=len)) if eqs else ""
    
    if rate_match and initial_match and final_match and freq_match and math:
        rate, initial, final, freq = rate_match.group(1), initial_match.group(1), final_match.group(1), freq_match.group(1).lower()
        prompt = f"A savings account earns {rate}\\% annual interest compounded {freq}. An initial deposit of \\${initial} is made, where $t$ represents time in years and $A(t)$ represents the account balance in dollars. Determine how long it will take for the account balance to reach \\${final}, given:\\\\"
    else:
        prompt = get_word_problem_prompt(item)
            
    return f"""\\question[6] 
{prompt}

 {math} \\\\

 \\hspace{{\\stretch{{1}}}}Answer: \\fillin[][2in]
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}

\\label{{exact-endocg}}

\\newpage"""

def build_q11(item, sols):
    prompt = get_word_problem_prompt(item)
    sol = sols[0] if sols else ""
    matches = re.findall(r'([a-zA-Z\s]+):\s*(?:_{3,}|\\underline|\\fillin)', item)
    clean_matches = [m.strip().lower() for m in matches if m.strip()]
    
    if len(clean_matches) >= 2:
        item1, item2 = clean_matches[-2], clean_matches[-1]
    else:
        sol_items = re.findall(r'([a-zA-Z\s]+):\s*\\?\(', sol)
        if len(sol_items) >= 2:
            item1, item2 = sol_items[-2].strip().lower(), sol_items[-1].strip().lower()
        else:
            item1, item2 = "quantity 1", "quantity 2"
            
    return f"""%% Systems \& Matrices %%
\\headerbox{{\\och}}
\\label{{exact-startoch}}

\\question[6]
{prompt}\\\\\\vspace{{12pt}}
    
         \\hspace{{\\stretch{{1}}}}{item1} price: \\fillin[][2in]\\\\\\vspace{{12pt}}
        
         \\hspace{{\\stretch{{1}}}}{item2} price: \\fillin[][2in]\\\\
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{2}}}}"""

def build_q12(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if 'matrix' in m or 'array' in m or 'cases' in m or '=' in m]
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question[4] 
Write the following system as an augmented matrix.\\\\

{math}\\\\
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}
\\newpage"""

def build_q13(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if 'matrix' in m or 'array' in m]
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question[6] Solve the following system using row operations on matrices. Give your answer as an ordered pair. If the system has no solution, write \\textbf{{\\textit{{Inconsistent}}}}\\\\
\\renewcommand{{\\arraystretch}}{{1}}

{math}\\\\

 \\hspace{{\\stretch{{1}}}}Answer: \\fillin[][2in]
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}

\\label{{exact-endoch}}

\\newpage"""

def build_q14(item, sols):
    match = re.search(r'(\\begin\{(?:array|tabular)\}.*?\\end\{(?:array|tabular)\})', item, re.DOTALL)
    table_math = f"\\[{match.group(1)}\\]" if match else ""
    sol = sols[0] if sols else ""
    
    return f"""%% Graphing %%
\\headerbox{{\\oci}}
\\label{{exact-startoci}}

\\question[5] Suppose a rational function has the attributes in the table below. Using only the holes, asymptotes, and intercepts listed along with as many of the helpful points as required, sketch the graph of the function.\\\\
\\begin{{solution}}
{sol}
\\end{{solution}}

\\begin{{center}}
\\renewcommand{{\\arraystretch}}{{2}}
{table_math}

\\vspace{{12pt}}

    \\begin{{tikzpicture}}[scale=0.5,>=triangle 45]
      \\draw [step=1cm, style={{black!60}}] (-10,-10) grid (10,10);
      \\draw [<->, very thick] (-10.5,0) -- (10.5,0); 
      \\draw [<->, very thick] (0,-10.5) -- (0,10.5);
    \\end{{tikzpicture}}
\\end{{center}}
\\newpage"""

def build_q15(item, sols):
    func_matches = re.findall(r'[fghp]\(x\)\s*=\s*.*?(?=\$|\\\]|\\\))', item)
    func = format_math(func_matches[0]) if func_matches else "\\(f(x) = 3^{x-1}+2\\)"
    sol = sols[0] if sols else ""
    
    return f"""\\question [5] Use the table to identify the transformations described by {func}. Circle the option that applies and fill in the blanks as appropriate to describe the transformations on the given function. If one does not apply, you may leave it blank. Then sketch the graph of the transformed function on the grid below. Indicate any asymptotes with dashed lines.\\\\
	\\renewcommand{{\\arraystretch}}{{3}} % Triple spacing
	\\begin{{center}}
	\\begin{{tabular}}{{|l|l|}}
		\\hline
		\\textbf{{Horizontal Transformations}}               & \\textbf{{Vertical Transformations}}              \\\\ \\hline
		Reflection: YES    or     NO       & Reflection:       YES    or     NO    \\\\ \\hline
		Dilation: \\underline{{\\hspace{{2cm}}}} times as wide           & Dilation: \\underline{{\\hspace{{2cm}}}} times as tall        \\\\ \\hline
		Translation: \\underline{{\\hspace{{2cm}}}} units LEFT or RIGHT & Translation: \\underline{{\\hspace{{2cm}}}} units UP or DOWN \\\\ \\hline
	\\end{{tabular}}
\\end{{center}}
\\vspace{{12pt}}

\\begin{{center}}
 \\begin{{tikzpicture}}[scale=0.4,>=triangle 45] \\draw[step=1cm, black!60] (-10,-10) grid (10,10); \\draw[very thick, <->] (-10.5,0) -- (10.5,0); \\draw[very thick, <->] (0,-10.5) -- (0,10.5); \\end{{tikzpicture}} 
\\end{{center}}

\\begin{{solution}}
{sol}
\\end{{solution}}
\\newpage"""

def build_q16(item, sols):
    func_matches = re.findall(r'[fghp]\(x\)\s*=\s*.*?(?=\$|\\\]|\\\))', item)
    func = format_math(func_matches[0]) if func_matches else "\\(f(x)=\\log_4\\left(x+2\\right)+1\\)"
    sol = sols[0] if sols else ""
    
    return f"""\\question[5]
Use the table to identify the transformations described by {func}. Circle the option that applies and fill in the blanks as appropriate to describe the transformations on the given function. If one does not apply, you may leave it blank. Then sketch the graph of the transformed function on the grid below. Indicate any asymptotes with dashed lines.\\\\
	\\renewcommand{{\\arraystretch}}{{3}} % Triple spacing
	\\begin{{center}}
	\\begin{{tabular}}{{|l|l|}}
		\\hline
		\\textbf{{Horizontal Transformations}}               & \\textbf{{Vertical Transformations}}              \\\\ \\hline
		Reflection: YES    or     NO       & Reflection:       YES    or     NO    \\\\ \\hline
		Dilation: \\underline{{\\hspace{{2cm}}}} times as wide           & Dilation: \\underline{{\\hspace{{2cm}}}} times as tall        \\\\ \\hline
		Translation: \\underline{{\\hspace{{2cm}}}} units LEFT or RIGHT & Translation: \\underline{{\\hspace{{2cm}}}} units UP or DOWN \\\\ \\hline
	\\end{{tabular}}
\\end{{center}}
\\vspace{{12pt}}

\\begin{{center}}
 \\begin{{tikzpicture}}[scale=0.4,>=triangle 45] \\draw[step=1cm, black!60] (-10,-10) grid (10,10); \\draw[very thick, <->] (-10.5,0) -- (10.5,0); \\draw[very thick, <->] (0,-10.5) -- (0,10.5); \\end{{tikzpicture}} 
\\end{{center}}

\\begin{{solution}}
{sol}
\\end{{solution}}
\\label{{exact-endoci}}
\\newpage"""

# ==========================================
# 3. ROUTER MAPPING & GENERATOR
# ==========================================

# Maps the chronological order of SBG questions to their raw CheckIt bank index
SBG_MAPPING = [
    {"checkit_idx": 11, "template": build_q1},
    {"checkit_idx": 13, "template": build_q2},
    {"checkit_idx": 15, "template": build_q3},
    {"checkit_idx": 12, "template": build_q4},
    {"checkit_idx": 0,  "template": build_q5},
    {"checkit_idx": 1,  "template": build_q6},
    {"checkit_idx": 2,  "template": build_q7},
    {"checkit_idx": 3,  "template": build_q8},
    {"checkit_idx": 4,  "template": build_q9},
    {"checkit_idx": 5,  "template": build_q10},
    {"checkit_idx": 8,  "template": build_q11},
    {"checkit_idx": 9,  "template": build_q12},
    {"checkit_idx": 10, "template": build_q13},
    {"checkit_idx": 14, "template": build_q14},
    {"checkit_idx": 7,  "template": build_q15},
    {"checkit_idx": 6,  "template": build_q16},
]

PREAMBLE = r"""\documentclass[11pt]{exam}

%%%%%%%%%%%%%%%%%%%%%%%%%% Preamble %%%%%%%%%%%%%%%%%%%%%%%%%% 
\input{01. Admin/1. Packages}
\input{01. Admin/2. WEB Course Info}
\input{01. Admin/3. WEB Outcomes}
\input{01. Admin/4. Commands}
\input{01. Admin/8. Fonts}
%%%%%%%%%%%%% Exam Information  %%%%%%%%%%%%%%%%%%%%%%%%%% 

\newcommand{\exam}{Non-Comprehensive  Exam}
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
\input{01. Admin/6. CoverPage}

\newpage

%%%% Questions %%%%

\begin{questions}
"""

POSTAMBLE = r"""
\headerbox{Bonus Question}

\input{01. Admin/7. Extra Credit}

\end{questions}

%%%%%%%%%%%%%%%%%%%%%%%%%% Scratch Paper %%%%%%%%%%%%%%%%%%%%%%%%%%
\blankpage

\end{document}
"""

def process_checkit_sbg_noncomp(input_filename, output_filename):
    with open(input_filename, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Split the raw CheckIt document by item blocks
    raw_blocks = re.split(r'\\item\s*%%%%% SpaTeXt Commands %%%%%', raw_text)
    
    if len(raw_blocks) > 0:
        raw_blocks = raw_blocks[1:]
        
    # Vacuum Phase: Extract all data strictly in CheckIt order
    checkit_data = []
    for block in raw_blocks:
        if '\\stxKnowl' in block:
            clean_text, sols = extract_solutions_and_clean(block)
            checkit_data.append({"text": clean_text, "sols": sols})
            
    # Construction Phase: Map the vacuumed data directly into the SBG templates
    output_lines = []
    for map_info in SBG_MAPPING:
        idx = map_info["checkit_idx"]
        if idx < len(checkit_data):
            data = checkit_data[idx]
            question_latex = map_info["template"](data["text"], data["sols"])
            output_lines.append(question_latex)
        else:
            print(f"Warning: CheckIt index {idx} not found in input data.")
            
    with open(output_filename, "w", encoding="utf-8") as outfile:
        outfile.write(PREAMBLE)
        outfile.write("\n\n".join(output_lines))
        outfile.write(POSTAMBLE)

    print(f"Success! Built {len(output_lines)} customized questions into the Non-Comp SBG template.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile CheckIt LaTeX banks directly into the Non-Comprehensive SBG format.")
    parser.add_argument("--in", "--input", dest="input_file", default="CheckIt-Output.tex", help="The raw CheckIt output .tex file")
    parser.add_argument("--out", "--output", dest="output_file", default="SBG_NonComp_Ready.tex", help="The final generated exam .tex file")
    
    args = parser.parse_args()
    
    print(f"Reading from: {args.input_file}")
    
    try:
        process_checkit_sbg_noncomp(args.input_file, args.output_file)
        print(f"File successfully saved as: {args.output_file}")
    except FileNotFoundError:
        print(f"Error: Could not locate the input file '{args.input_file}'. Ensure the file name is correct and it is located in the same directory.")