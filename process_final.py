import re
import sys

# ==========================================
# 1. HELPER FUNCTIONS
# ==========================================

def strip_stxKnowl(text):
    """Force-strips \stxKnowl{...} wrappers from a block of text."""
    text = text.strip()
    match = re.search(r'\\stxKnowl\s*\{', text)
    if match:
        inner, _ = get_braced_content(text, match.end() - 1)
        return inner.strip()
    return text

def get_braced_content(text, start_index):
    if text[start_index] != "{":
        return None, start_index
    
    count = 1
    for i in range(start_index + 1, len(text)):
        if text[i] == "{":
            count += 1
        elif text[i] == "}":
            count -= 1
            
        if count == 0:
            return text[start_index + 1:i], i + 1
            
    return None, len(text)

def clean_solutions(content):
    """
    Finds CheckIt's \stxOuttro{SOLUTION ...} blocks and converts them 
    to exam class \begin{solution} ... \end{solution}.
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

# ==========================================
# 2. PARSER
# ==========================================

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
            
            # Use robust stripper to ensure no \stxKnowl wrappers survive
            clean_p = strip_stxKnowl(p)
            clean_parts.append(clean_solutions(clean_p))
            
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
# 3. EXAM CONFIGURATION
# ==========================================
    
EXAM_MAP = [
    {
        "index": 1,
        "type": "single",
        "points": 5,
        "pre_text": "",
        "post_text": r"",
        "custom_space": r""
    },
    {
        "index": 2,
        "type": "parts",
        "points": [5, 5],
        "pre_text": r"Use properties of logarithms to expand or condense the logarithmic expression as specified.",
        "post_text": r"",
        "custom_space": r"\vspace{\stretch{1}}\answerline"
    },
    {
        "index": 3,
        "type": "single",
        "points": 6,
        "pre_text": r"\uplevel{For questions \ref{exact-start} through~\ref{exact-end}, solve for \textbf{all} solutions. Identify any extraneous solutions.}",
        "label": r"\label{exact-start}",
        "custom_space": r"\vspace{\stretch{1}}",
        "post_text": r"\par solutions: \fillin\fillin \hspace{\stretch{1}} extraneous solutions: \fillin\fillin"
    },
    {
        "index": 4,
        "type": "single",
        "points": 6,
        "pre_text": "",
        "custom_space": r"\vspace{\stretch{1}}",
        "post_text": r"\par solutions: \fillin\fillin \hspace{\stretch{1}} extraneous solutions: \fillin\fillin"
    },
    {
        "index": 5,
        "type": "single",
        "points": 6,
        "pre_text": "",
        "label": r"\label{exact-end}",
        "custom_space": r"\vspace{\stretch{1}}",
        "post_text": r"\par solutions: \fillin\fillin \hspace{\stretch{1}} extraneous solutions: \fillin\fillin"
    },
    {
        "index": 6,
        "type": "single",
        "points": 6,
        "pre_text": "",
        "custom_space": r"\vspace{\stretch{1}}\answerline",
        "post_text": ""
    }
]

# ==========================================
# 4. GENERATOR
# ==========================================

def generate_latex_source(parsed_data, config):
    """
    Constructs the LaTeX source code for a single examination question.
    """
    latex_lines = []
    
    if config.get("pre_text"):
        latex_lines.append(config["pre_text"])
        
    label_str = config.get("label", "")
    
    if parsed_data["type"] == "parts":
        # Question header (points omitted here, as they are distributed to parts)
        latex_lines.append(fr"\question {label_str}")
        
        # Intro text (already contains \begin{solution} if parsed correctly)
        # Note: Do not wrap this in { } braces.
        latex_lines.append(parsed_data['intro'] + r"\\")
        
        latex_lines.append(r"\begin{parts}")
        
        points_list = config.get("points", [])
        for idx, part in enumerate(parsed_data["parts"]):
            pts = points_list[idx] if idx < len(points_list) else 1
            # Clean up CheckIt's manual (a), (b) labels
            clean_part = re.sub(r'^(\(\w\)|[\w]\)|[\w]\.)\s*', '', part)
            latex_lines.append(fr"    \part[{pts}] {clean_part}")
            
        latex_lines.append(r"\end{parts}")
        
    else:
        pts = config.get("points", 1)
        latex_lines.append(fr"\question[{pts}] {label_str}")
        
        # Content (already contains \begin{solution} block)
        latex_lines.append(parsed_data["content"])
        
    if config.get("custom_space"):
        latex_lines.append(config["custom_space"])
        
    if config.get("post_text"):
        latex_lines.append(config["post_text"])
        
    return "\n".join(latex_lines)

def process_checkit_bank(input_filename, output_filename):
    """
    Executes the primary routine to parse a raw CheckIt LaTeX export and 
    compile it into a formatted departmental examination document.
    """
    with open(input_filename, "r", encoding="utf-8") as infile:
        raw_text = infile.read()
        
    items = []
    search_index = 0
    
    while True:
        match = re.search(r"\\stxKnowl\s*\{", raw_text[search_index:])
        if not match:
            break
            
        start_idx = search_index + match.end() - 1
        content, end_idx = get_braced_content(raw_text, start_idx)
        
        if content is not None:
            full_item_text = r"\stxKnowl{" + content + "}"
            items.append(full_item_text)
            search_index = search_index + end_idx
        else:
            break
            
    output_lines = []
    
    for idx, item_text in enumerate(items):
        if idx < len(EXAM_MAP):
            config = EXAM_MAP[idx]
            parsed = parse_checkit_item(item_text)
            
            if parsed is not None:
                question_latex = generate_latex_source(parsed, config)
                output_lines.append(question_latex)
                output_lines.append("\n")
                
    with open(output_filename, "w", encoding="utf-8") as outfile:
        outfile.write("\n".join(output_lines))

if __name__ == "__main__":
    process_checkit_bank("CheckIt.tex", "Dept.tex")