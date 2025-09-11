import re

TOKEN_SPEC = [
    ("BIGINT", r"\d+n"),             # 123n
    ("NUMBER", r"\d+(\.\d+)?"),
    ("STRING", r'"(\\.|[^"\\])*"'),
    ("BOOL", r"(true|false)"),
    ("NULL", r"null"),
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    ("CHAR", r"'(\\.|[^'\\])'"),   # <--- NEW for char literals

    # Multi-character operators must come before single-char
    ("OP", r"(==|!=|<=|>=|\+|\-|\*|/|=|<|>)"),

    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("SEMICOL", r";"),
    ("COLON", r":"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("COMMA", r","),

    ("SKIP", r"[ \t\n]+"),
    ("MISMATCH", r"."),
]

def tokenize(code):
    # Remove comments first
    code = re.sub(r"//.*", "", code)         # single-line comments
    code = re.sub(r"#.*", "", code)          # single-line comments (# style)
    code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)  # multi-line comments

    regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
    tokens = []
    for m in re.finditer(regex, code):
        kind = m.lastgroup
        value = m.group()
        if kind == "SKIP":
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected token: {value}")
        else:
            tokens.append((kind, value))  

    return tokens   