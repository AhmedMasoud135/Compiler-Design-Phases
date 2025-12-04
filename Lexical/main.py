
import re
from pathlib import Path

# Define keywords for the language
KEYWORDS = {
    "int", "float", "if", "else", "while", "for", "return",
    "char", "void", "double", "do", "break", "continue", "switch", "case", "default"
}

# Build the regex pattern for tokenization
def build_regex():
    parts = []
    for name, pattern in [
        ("MULTI_COMMENT", r'/\*[\s\S]*?\*/'),       
        ("SINGLE_COMMENT", r'//.*'),                
        ("NEWLINE",   r'\n'),                       
        ("SKIP",      r'[ \t\r]+'),                 
        ("STRING",    r'"(?:\\.|[^"\\])*"'),        
        ("CHAR",      r"'(?:\\.|[^'\\])*'"),         
        ("NUMBER", r'(?:\d*\.\d+|\d+\.?\d*)(?:[eE][+-]?\d+)?'),   
        ("IDENT",     r'[A-Za-z_]\w*'),              
        ("OP",        r'(?:==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|&&|\|\||->|[+\-*/%=<>&|!^~])'),     
        ("SEMICOLON", r';'),
        ("COMMA",     r','),
        ("LIBRARY",   r'#'),
        ("LPAREN",    r'\('),
        ("RPAREN",    r'\)'),
        ("LBRACE",    r'\{'),
        ("RBRACE",    r'\}'),
        ("LBRACKET",  r'\['),
        ("RBRACKET",  r'\]'),
        ("QUESTION",  r'\?'),
        ("COLON",     r':'),
        ("MISMATCH",  r'.')                         
    ]:
        parts.append(f"(?P<{name}>{pattern})")
    return re.compile("|".join(parts))              


REGEX = build_regex()

# Tokenize the input code
def tokenize(code):
    tokens = []
    line_no = 1
    line_start = 0
    pos = 0
    while pos < len(code):
        mo = REGEX.match(code, pos)       
        if not mo:                        
            break
        kind = mo.lastgroup               
        value = mo.group(kind)            
        if kind == "NEWLINE":
            line_no += 1
            line_start = mo.end()         
            pos = mo.end()                
            continue
        elif kind in ("SKIP", "SINGLE_COMMENT", "MULTI_COMMENT", "LIBRARY"):
            if kind == "MULTI_COMMENT":
                newlines = value.count('\n')        
                if newlines:
                    line_no += newlines
                    last_nl = value.rfind('\n')    
                    if last_nl != -1:
                        line_start = mo.start() + last_nl + 1  
            pos = mo.end()
            continue
        elif kind == "IDENT" and value in KEYWORDS:
            kind = "KEYWORD"
        elif kind in ("NUMBER", "STRING", "CHAR"):
            kind = "LITERAL"
        elif kind in ("SEMICOLON", "COMMA", "LPAREN", "RPAREN", "LBRACE", "RBRACE", "LBRACKET", "RBRACKET", "QUESTION", "COLON"):
            kind = "DELIMITER"
        elif kind == "MISMATCH":
            col = mo.start() - line_start + 1
            raise RuntimeError(f"Lexical error at line {line_no} col {col}: unexpected character {value!r}")
        col = mo.start() - line_start + 1         
        tokens.append({"type": kind, "value": value, "line": line_no, "col": col})
        pos = mo.end()
    return tokens

def tokenize_file(filename):
    text = Path(filename).read_text(encoding='utf-8')
    return tokenize(text)





# Example usage
code = """
// This is a single-line comment
/* This is a
   multi-line comment
    dkkkkkk 
    */
int x = 5;
float y = 3.14;
char c = 'a';
string s = "hello";
x += y * 2;
"""
tokens = tokenize(code)
for t in tokens:
    print(f"{t['type']:10} | {t['value']:10} | line {t['line']}, col {t['col']}")


# Example usage with file
print("*"*60)
tokens = tokenize_file("test.c")
for t in tokens:
    print(f"{t['type']:10} | {t['value']:10} | line {t['line']}, col {t['col']}")
