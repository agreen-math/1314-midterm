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
    
    # 1. Recursive Unwrapper: Remove all \stxKnowl wrappers safely to prevent dangling '}'
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
            
    # 2. Extract and Delete \stxOuttro blocks
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
            
    # 3. Strip internal titles
    clean_text = re.sub(r'\\stxTitle\s*\{.*?\}', '', clean_text)
            
    return clean_text, sols

def extract_math(text):
    """Finds all LaTeX math blocks universally and deduplicates them."""
    # Temporarily remove TikZ pictures so we do not extract axis labels
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
    """Aggressively flattens lists and cleans word problems (Q6, Q9) from CheckIt cruft."""
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
# 2. THE 16 DEPARTMENT QUESTION TEMPLATES
# ==========================================

def build_q1(item, sols):
    match = re.search(r'(\\begin\{(?:array|tabular)\}.*?\\end\{(?:array|tabular)\})', item, re.DOTALL)
    math = match.group(1) if match else ""
    math = re.sub(r'\\rule\[.*?\]\{.*?\}\{.*?\}', '', math)
    math = math.replace(r'\hspace{3cm}', r'\hspace{75mm}')
    # Keep array to prevent math mode crashes, but convert tabular back to array just in case
    math = math.replace(r'\begin{tabular}', r'\begin{array}').replace(r'\end{tabular}', r'\end{array}')
    sol = sols[0] if sols else ""
    
    return f"""\\question[5] Fill in the table to give an equivalent equation in the specified form.\\\\
\\begin{{center}} {{\\renewcommand{{\\arraystretch}}{{3}}
\\[
{math}
\\]
}}\\end{{center}}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}"""

def build_q2(item, sols):
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
    \\begin{{solution}}
    {sol1}
    \\end{{solution}}
    \\vspace{{\\stretch{{1}}}}\\answerline

    \\part[5] Rewrite as a single logarithm. Express all factors as powers.\\\\
    
    {math2}
    \\begin{{solution}}
    {sol2}
    \\end{{solution}}
    \\vspace{{\\stretch{{1}}}}\\answerline
\\end{{parts}}
\\newpage"""

def build_q3(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    if not eqs: eqs = maths
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\uplevel{{For questions \\ref{{exact-start}} through~\\ref{{exact-end}}, solve for \\textbf{{all}} solutions. Identify any extraneous solutions.}}
\\question[6] \\label{{exact-start}}
{math}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}
\\par solutions: \\fillin[][1.5in] \\hspace{{\\stretch{{1}}}} extraneous solutions: \\fillin[][1.5in]"""

def build_q4(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    if not eqs: eqs = maths
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question[6] 
{math}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}
\\par solutions: \\fillin[][1.5in] \\hspace{{\\stretch{{1}}}} extraneous solutions: \\fillin[][1.5in]\\newpage"""

def build_q5(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    if not eqs: eqs = maths
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question[6] \\label{{exact-end}}
{math}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}
\\par solutions: \\fillin[][1.5in] \\hspace{{\\stretch{{1}}}} extraneous solutions: \\fillin[][1.5in]"""

def build_q6(item, sols):
    sol = sols[0] if sols else ""
    
    rate_match = re.search(r'(\d+(?:\.\d+)?)\s*\\?%', item)
    initial_match = re.search(r'initial deposit of\s*(?:\\?\$)?\s*([0-9,]+)', item, re.IGNORECASE)
    final_match = re.search(r'reach\s*(?:\\?\$)?\s*([0-9,]+)', item, re.IGNORECASE)
    freq_match = re.search(r'compounded\s+(monthly|quarterly|annually|semiannually|daily|continuously)', item, re.IGNORECASE)
    
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m]
    math = format_math(max(eqs, key=len)) if eqs else ""
    
    if rate_match and initial_match and final_match and freq_match and math:
        rate = rate_match.group(1)
        initial = initial_match.group(1)
        final = final_match.group(1)
        freq = freq_match.group(1).lower()
        
        prompt = f"A savings account earns {rate}\\% annual interest compounded {freq}. An initial deposit of \\${initial} is made, where $t$ represents time in years and $A(t)$ represents the account balance in dollars. Determine how long it will take for the account balance to reach \\${final} given:\n\n{math}"
    else:
        prompt = get_word_problem_prompt(item)
        if math not in prompt:
            prompt += f"\n\n{math}"
            
    return f"""\\question[6] {prompt}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}\\answerline
\\newpage"""

def build_q7_8(item, sols):
    func = format_math(extract_func(item))
    sol = sols[0] if sols else ""
    
    return f"""\\question[5] Use the table to identify the transformations described by {func}. Circle the option that applies and fill in the blanks as appropriate to describe the transformations on the given function. If one does not apply, you may leave it blank. Then sketch the graph of the transformed function on the grid below. Indicate any asymptotes with dashed lines.\\\\
\\begin{{table}}[h]
    \\renewcommand{{\\arraystretch}}{{3}} 
    \\centering
    \\begin{{tabular}}{{|l|l|}}
        \\hline
        \\textbf{{Horizontal Transformations}} & \\textbf{{Vertical Transformations}} \\\\ \\hline
        Reflection: YES or NO & Reflection: YES or NO \\\\ \\hline
        Dilation: \\underline{{\\hspace{{2cm}}}} times as wide & Dilation: \\underline{{\\hspace{{2cm}}}} times as tall \\\\ \\hline
        Translation: \\underline{{\\hspace{{2cm}}}} units LEFT or RIGHT & Translation: \\underline{{\\hspace{{2cm}}}} units UP or DOWN \\\\ \\hline
    \\end{{tabular}}
\\end{{table}}
\\begin{{solution}}
{sol}
\\end{{solution}}

\\begin{{center}}
    \\begin{{tikzpicture}}[scale=0.35,>=triangle 45]
      \\draw [step=1cm, style={{black!60}}] (-10,-10) grid (10,10);
      \\draw [<->, very thick] (-10.5,0) -- (10.5,0); 
      \\draw [<->, very thick] (0,-10.5) -- (0,10.5);
    \\end{{tikzpicture}}
\\end{{center}}
\\newpage"""

def build_q9(item, sols):
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
            
    return f"""\\question[6] {prompt}
\\vspace{{\\stretch{{1}}}}\\\\
{item1}: \\fillin[][1.5in] \\hspace{{\\stretch{{1}}}} {item2}: \\fillin[][1.5in]
\\begin{{solution}}
{sol}
\\end{{solution}}
\\newpage"""

def build_q10(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if 'matrix' in m or 'array' in m or 'cases' in m or '=' in m]
    if not eqs: eqs = maths
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question[4] Write the following system as an augmented matrix.\\\\
    
{math}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}"""

def build_q11(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if 'matrix' in m or 'array' in m]
    if not eqs: eqs = maths
    math = format_math(max(eqs, key=len)) if eqs else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question[6] Solve the following system using row operations on matrices.\\\\
    
{math}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{5}}}}\\answerline
\\newpage"""

def build_q12(item, sols):
    maths = extract_math(item)
    eqs = [m for m in maths if '=' in m or '(' in m]
    if len(eqs) < 2: eqs = maths
    
    math1 = format_math(eqs[0]) if len(eqs) > 0 else ""
    math2 = format_math(eqs[1]) if len(eqs) > 1 else ""
    sol1 = sols[0] if len(sols) > 0 else ""
    sol2 = sols[1] if len(sols) > 1 else ""
    
    return f"""\\question Find the domain and range of the functions.
\\begin{{parts}}
    \\part[5] {math1}
    \\vspace{{\\stretch{{1}}}}\\\\
    domain: \\fillin[][2in] \\hspace{{\\stretch{{1}}}} range: \\fillin[][2in]
    \\begin{{solution}}
    {sol1}
    \\end{{solution}}

    \\part[5] {math2}
    \\vspace{{\\stretch{{1}}}}\\\\
    domain: \\fillin[][2in] \\hspace{{\\stretch{{1}}}} range: \\fillin[][2in]
    \\begin{{solution}}
    {sol2}
    \\end{{solution}}
\\end{{parts}}
\\newpage
\\newpage"""

def build_q13(item, sols):
    func = format_math(extract_func(item))
    sol = sols[0] if sols else ""
    
    return f"""\\question[5] List all of the vertical, horizontal, and oblique asymptotes of the rational function.\\\\
        
    {func}
    
\\hspace{{\\stretch{{1}}}}
    \\renewcommand{{\\arraystretch}}{{3}}
    \\begin{{tabular}}{{|c|c|}}
        \\hline
        \\textbf{{Asymptotes}}  & \\textbf{{Equation}} \\\\ \\hline
        Vertical   & \\hspace{{50mm}} \\\\ \\hline
        Horizontal &  \\\\ \\hline
        Oblique    &  \\\\ \\hline
    \\end{{tabular}}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\vspace{{\\stretch{{1}}}}"""

def build_q14(item, sols):
    func = format_math(extract_func(item))
    sol = sols[0] if sols else ""
    
    return f"""\\question[10] Fill in the table below with the zeros of the polynomial, their multiplicities and the behavior of the graph of the function around each zero. You may or may not use all of the rows in the table.\\\\
    
    {func}\\
    
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

def build_q15(item, sols):
    match = re.search(r'(\\begin\{(?:array|tabular)\}.*?\\end\{(?:array|tabular)\})', item, re.DOTALL)
    table_math = f"\\[{match.group(1)}\\]" if match else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question[5] Suppose a rational function has the attributes in the table below. Using only the holes, asymptotes, and intercepts listed along with as many of the helpful points as required, sketch the graph of the function.\\\\
\\renewcommand{{\\arraystretch}}{{1.5}}
    
    {table_math}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\begin{{center}}
\\scalebox{{1}}{{
    \\begin{{tikzpicture}}[scale=0.5,>=triangle 45]
      \\draw [step=1cm, style={{black!60}}] (-10,-10) grid (10,10);
      \\draw [<->, very thick] (-10.5,0) -- (10.5,0); 
      \\draw [<->, very thick] (0,-10.5) -- (0,10.5);
    \\end{{tikzpicture}}
}}
\\end{{center}}
\\newpage"""

def build_q16(item, sols):
    tikz_match = re.search(r'\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}', item, re.DOTALL)
    tikz_math = f"\\begin{{center}}\n{tikz_match.group(0)}\n\\end{{center}}" if tikz_match else ""
    sol = sols[0] if sols else ""
    
    return f"""\\question Use the image of a polynomial below to answer the questions that follow.\\\\
{tikz_math}
\\begin{{solution}}
{sol}
\\end{{solution}}
\\begin{{parts}}
    \\part[1] Is the degree of the polynomial even or odd? \\\\\\\\
    \\begin{{oneparcheckboxes}}
    \\choice even
    \\choice odd
    \\end{{oneparcheckboxes}}\\\\\\vspace{{.125in}}
    \\part[1\\half] Is the lead coefficient of the polynomial positive or negative?\\\\\\\\
    \\begin{{oneparcheckboxes}}
    \\choice positive
    \\choice negative
    \\end{{oneparcheckboxes}}\\\\\\vspace{{.125in}}
    \\part[1] Is the constant of the polynomial positive or negative? \\\\\\\\
    \\begin{{oneparcheckboxes}}
    \\choice positive
    \\choice negative
    \\end{{oneparcheckboxes}}\\\\\\vspace{{.125in}}
    \\part[1\\half] What is the minimum degree? \\\\\\\\\\fillin
\\end{{parts}}"""


# Array mapping question indices directly to their exact template builder
TEMPLATE_BUILDERS = [
    build_q1, build_q2, build_q3, build_q4, build_q5, build_q6,
    build_q7_8, build_q7_8, build_q9, build_q10, build_q11, 
    build_q12, build_q13, build_q14, build_q15, build_q16
]

# ==========================================
# 3. GENERATOR
# ==========================================

PREAMBLE = r"""\documentclass[addpoints]{exam}

\usepackage[utf8]{inputenc}
\usepackage{array}
\usepackage{graphicx}
\usepackage{multicol}
\usepackage{amsmath}
\usepackage{tikz}
\usetikzlibrary{arrows}

\renewcommand*\half{.5}

\setlength\answerlinelength{3in}

%%%%% Question Info %%%%% 

%\printanswers

%%%%% Header and Footer %%%%% 

\pagestyle{headandfoot}
\runningheadrule
\firstpageheader{Math 1314}{Non-Comprehensive Final Exam}{Spring 2026}
\runningheader{Math 1314}
{Non-Comprehensive Final Exam}
{Spring 2026}
\runningheadrule
\firstpagefooter{}{}{}
\runningfooter{}{Page \thepage\ of \numpages}{}

%%%%% Questions %%%%% 

\begin{document}

\uplevel{Number of Questions: \numquestions\hspace{\stretch{1}} Point Total: \numpoints}
\begin{questions}
"""

POSTAMBLE = r"""
\end{questions}
\end{document}
"""

def process_checkit_bank(input_filename, output_filename):
    with open(input_filename, "r", encoding="utf-8") as f:
        raw_text = f.read()

    raw_blocks = re.split(r'\\item\s*%%%%% SpaTeXt Commands %%%%%', raw_text)
    
    if len(raw_blocks) > 0:
        raw_blocks = raw_blocks[1:]
        
    output_lines = []
    
    for idx, block in enumerate(raw_blocks):
        if '\\stxKnowl' in block and idx < len(TEMPLATE_BUILDERS):
            clean_text, sols = extract_solutions_and_clean(block)
            question_latex = TEMPLATE_BUILDERS[idx](clean_text, sols)
            output_lines.append(question_latex)
                
    with open(output_filename, "w", encoding="utf-8") as outfile:
        outfile.write(PREAMBLE)
        outfile.write("\n\n".join(output_lines))
        outfile.write(POSTAMBLE)

    print(f"Success! Built {len(output_lines)} customized questions directly into the Dept template.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compile CheckIt LaTeX banks directly into the Department formatting template.")
    parser.add_argument("--in", "--input", dest="input_file", default="CheckIt.tex", help="The raw CheckIt output .tex file (default: CheckIt.tex)")
    parser.add_argument("--out", "--output", dest="output_file", default="Dept.tex", help="The final generated exam .tex file (default: Dept.tex)")
    
    args = parser.parse_args()
    
    print(f"Reading from: {args.input_file}")
    
    try:
        process_checkit_bank(args.input_file, args.output_file)
        print(f"File successfully saved as: {args.output_file}")
    except FileNotFoundError:
        print(f"Error: Could not locate the input file '{args.input_file}'. Ensure the file name is correct and it is located in the same directory.")