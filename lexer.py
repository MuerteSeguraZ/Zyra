import re

TOKEN_SPEC = [
    # Numeric literals (order matters - most specific first)
    ("FLOAT_HEX", r"0x[0-9A-Fa-f]+\.[0-9A-Fa-f]+"),  # 0x1A.4F
    ("INT_HEX", r"0x[0-9A-Fa-f]+"),                    # 0xFF
    ("INT_OCTAL", r"0o[0-7]+"),                        # 0o77
    ("INT_BINARY", r"0b[01]+"),                        # 0b1010
    ("BIGINT", r"\d+n"),                               # 123n
    ("DECIMAL", r"\d+\.\d+d"),                         # 12.345d
    ("FLOAT", r"\d+\.\d+([eE][+-]?\d+)?"),            # 12.34 or 1.2e-5
    ("NUMBER", r"\d+"),                                # 123
    
    # String literals with interpolation support
    ("STRING_INTERP", r'f"(\\.|[^"\\])*"'),           # f"Hello {name}"
    ("STRING", r'"(\\.|[^"\\])*"'),                   # "normal string"
    ("RAW_STRING", r'r"[^"]*"'),                       # r"raw\nstring"
    ("MULTILINE_STRING", r'"""[\s\S]*?"""'),          # """multi
                                                       # line"""
    
    # Character and boolean literals
    ("CHAR", r"'(\\.|[^'\\])'"),
    ("BOOL", r"(true|false)"),
    ("NULL", r"null"),
    
    # Identifiers (keywords will be checked separately)
    ("ID", r"[A-Za-z_][A-Za-z0-9_]*"),
    
    # Operators (longest first to avoid partial matches)
    ("OP", r"(<<<=|>>>=|\*\*=|//=|%=|&=|\|=|\^=|<<=|>>=|<=>|===|!==|\+=|-=|\*=|/=|==|!=|<=|>=|<<|>>|\*\*|//|&&|\|\||::|->|=>|\.\.\.|\.\.|:=|\+\+|--|\+|\-|\*|/|%|=|<|>|!|&|\||\^|\~|\?)"),
    
    # Delimiters
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("LBRACE", r"\{"),
    ("RBRACE", r"\}"),
    ("LBRACKET", r"\["),
    ("RBRACKET", r"\]"),
    ("SEMICOL", r";"),
    ("COLON", r":"),
    ("COMMA", r","),
    ("DOT", r"\."),
    ("AT", r"@"),
    ("HASH", r"#"),
    ("DOLLAR", r"\$"),
    
    # Whitespace and comments
    ("NEWLINE", r"\n"),
    ("SKIP", r"[ \t]+"),
    ("MISMATCH", r"."),
]

class Token:
    """Enhanced token class with position tracking"""
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line}:C{self.column})"

def tokenize(code, track_position=True):
    """
    Tokenize source code with optional position tracking.
    
    Args:
        code: Source code string
        track_position: Whether to track line/column numbers
    
    Returns:
        List of tokens (tuples or Token objects)
    """
    # Remove comments
    code = remove_comments(code)
    
    # Keywords set for classification
    keywords = {
        "dec", "if", "else", "elif", "while", "for", "in", "print", "printf",  # <-- Make sure "elif" is here
        "fnc", "return", "break", "continue", "switch", "case", "default",
        "try", "catch", "throw", "match", "async", "await", "yield",
        "import", "from", "as", "export", "const", "mut", "ref",
        "type", "struct", "enum", "trait", "impl", "pub", "priv",
        "static", "self", "super", "where", "unsafe", "macro", "finally"
    }
    
    regex = "|".join(f"(?P<{name}>{pattern})" for name, pattern in TOKEN_SPEC)
    tokens = []
    
    line = 1
    line_start = 0
    
    for m in re.finditer(regex, code):
        kind = m.lastgroup
        value = m.group()
        column = m.start() - line_start + 1
        
        if kind == "SKIP":
            continue
        elif kind == "NEWLINE":
            line += 1
            line_start = m.end()
            continue
        elif kind == "MISMATCH":
            raise SyntaxError(f"Unexpected character '{value}' at line {line}, column {column}")
        
        # Convert ID to KEYWORD if it's a keyword
        if kind == "ID" and value in keywords:
            kind = "KEYWORD"
        
        if track_position:
            tokens.append(Token(kind, value, line, column))
        else:
            tokens.append((kind, value))
    
    return tokens

def remove_comments(code):
    """Remove single-line and multi-line comments from code"""
    # Multi-line comments /* ... */
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    # Single-line comments // ...
    code = re.sub(r"//[^\n]*", "", code)
    # Hash-style comments # ...
    code = re.sub(r"#[^\n]*", "", code)
    return code

def preprocess(code):
    """Optional preprocessor for macros and conditional compilation"""
    # Simple macro substitution (can be expanded)
    macros = {}
    lines = []
    
    for line in code.split('\n'):
        # Simple #define support
        if line.strip().startswith('#define'):
            parts = line.split(None, 2)
            if len(parts) >= 3:
                macros[parts[1]] = parts[2]
            continue
        
        # Substitute macros
        for macro, value in macros.items():
            line = line.replace(macro, value)
        
        lines.append(line)
    
    return '\n'.join(lines)

# Utility functions for token type checking
def is_literal(token_type):
    """Check if token type is a literal"""
    return token_type in {
        "NUMBER", "FLOAT", "INT_HEX", "INT_OCTAL", "INT_BINARY",
        "BIGINT", "DECIMAL", "STRING", "STRING_INTERP", "RAW_STRING",
        "MULTILINE_STRING", "CHAR", "BOOL", "NULL"
    }

def is_operator(token_type):
    """Check if token type is an operator"""
    return token_type == "OP"

def is_keyword(token_type):
    """Check if token type is a keyword"""
    return token_type == "KEYWORD"