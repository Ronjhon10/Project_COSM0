# <><><><><><><><><><><><><><><><><><><><><>
# IMPORTS
# <><><><><><><><><><><><><><><><><><><><><>
from string_with_arrows import *

# <><><><><><><><><><><><><><><><><><><><><>
# CONSTANTS
# <><><><><><><><><><><><><><><><><><><><><>
DIGITS = '0123456789'


# <><><><><><><><><><><><><><><><><><><><><>
# ERRORS
# <><><><><><><><><><><><><><><><><><><><><>
class Error:
    def __init__(self, position_start, position_end, error_name, details):
        self.position_start = position_start
        self.position_end = position_end
        self.error_name = error_name
        self.details = details
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'\nFile {self.position_start.fn}, line {self.position_start.ln + 1}'
        result += '\n\n'+string_with_arrows(self.position_start.ftxt, self.position_start, self.position_end)
        return result

class IllegalCharError(Error):
    def __init__(self, position_start, position_end, details):
        super().__init__(position_start, position_end, 'Illegal character', details)
class InvalidSyntaxError(Error):
    def __init__(self, position_start, position_end, details=""):
        super().__init__(position_start, position_end, 'Invalid Syntax', details)

# <><><><><><><><><><><><><><><><><><><><><>
# POSITION
# <><><><><><><><><><><><><><><><><><><><><>

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt
    def advance(self, current_char):
        self.col += 1
        self.idx += 1

        if current_char == '\n':
            self.ln += 1
            self.col = 0

        return self
    def copy(self):
        return Position(self.idx, self.ln, self.col, self.fn, self.ftxt)

# <><><><><><><><><><><><><><><><><><><><><>
# TOKENS
# <><><><><><><><><><><><><><><><><><><><><>
TT_INT   = 'INT'
TT_FLOAT = 'FLOAT'
TT_PLUS  = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL   = 'MUL'
TT_DIV   = 'DIV'
TT_LPAREN= 'LPAREN'
TT_RPAREN= 'RPAREN'


class Token:
    def __init__(self, type_, value=None):
        self.type_ = type_
        self.value = value
    def __repr__(self):
        if self.value is not None:
            return f"<{self.type_}: {self.value}>"
        return f"{self.type_}"

# <><><><><><><><><><><><><><><><><><><><><>
# LEXER
# <><><><><><><><><><><><><><><><><><><><><>

class Lexer:
    def __init__(self, fn, text):
        self.fn = fn
        self.text = text
        self.pos = Position(-1, 0, -1, fn, text)
        self.current_char = None
        self.advance()

    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []
        while self.current_char is not None:
            if self.current_char in ' \t\n':
                self.advance()
            elif self.current_char in DIGITS or self.current_char == '.':
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS)); self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS)); self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL)); self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV)); self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN)); self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN)); self.advance()
            else:
                position_start = self.pos.copy()
                ch = self.current_char
                self.advance()
                return [], IllegalCharError(position_start, self.pos, "'" + ch + "'")
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        while self.current_char is not None and (self.current_char in DIGITS or self.current_char == '.'):
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
            num_str += self.current_char
            self.advance()
        if num_str == '.' or num_str == '':
            # handle lone dot as illegal char
            return Token(TT_FLOAT, 0.0)
        return Token(TT_INT, int(num_str)) if dot_count == 0 else Token(TT_FLOAT, float(num_str))

# <><><><><><><><><><><><><><><><><><><><><>
# NODES
# <><><><><><><><><><><><><><><><><><><><><>

class NumberNode:
    def __init__(self, token):
        self.token = token
    def __repr__(self):
        return f"{self.token}"

class BinOpNode:
    def __init__(self, left, op_token, right):
        self.left = left
        self.right = right
        self.op_token = op_token

    def __repr__(self):
        return f"({self.left} {self.op_token.type_} {self.right})"

# <><><><><><><><><><><><><><><><><><><><><>
# PARSER
# <><><><><><><><><><><><><><><><><><><><><>
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.current_tok = None
        self.advance()

    def advance(self):
        self.tok_idx += 1
        self.current_tok = self.tokens[self.tok_idx] if self.tok_idx < len(self.tokens) else None
        return self.current_tok

    def parse(self):
        return self.expr()

    def factor(self):
        tok = self.current_tok
        if tok is None:
            return None
        if tok.type_ in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(tok)
        if tok.type_ == TT_LPAREN:
            self.advance()
            node = self.expr()
            if self.current_tok and self.current_tok.type_ == TT_RPAREN:
                self.advance()
            return node
        if tok.type_ in (TT_PLUS, TT_MINUS):
            # unary +/-
            op = tok
            self.advance()
            node = self.factor()
            return BinOpNode(NumberNode(Token(TT_INT, 0)), op, node)
        return None

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        left = func()
        while self.current_tok is not None and self.current_tok.type_ in ops:
            op_tok = self.current_tok
            self.advance()
            right = func()
            left = BinOpNode(left, op_tok, right)
        return left

# <><><><><><><><><><><><><><><><><><><><><>
# RUN
# <><><><><><><><><><><><><><><><><><><><><>

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error
    parser = Parser(tokens)
    ast = parser.parse()
    return ast, None

# <><><><><><><><><><><><><><><><><><><><><>
# COLORS
# <><><><><><><><><><><><><><><><><><><><><>

class Colors:
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
