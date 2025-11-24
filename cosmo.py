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
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'
TT_RPAREN = 'RPAREN'


class Token:
    def __init__(self, type_, value = None):
        self.type_ = type_
        self.value = value
    def __repr__(self):
        if self.value: return f"<{self.type_}: {self.value}>"
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

        while self.current_char != None:
            if self.current_char in ' /t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(TT_PLUS)
                self.advance()
            elif self.current_char == '-':
                tokens.append(TT_MINUS)
                self.advance()
            elif self.current_char == '*':
                tokens.append(TT_MUL)
                self.advance()
            elif self.current_char == '/':
                tokens.append(TT_DIV)
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                position_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(position_start, self.pos, "'"+char+"'")

        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0

        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT, float(num_str))
# <><><><><><><><><><><><><><><><><><><><><>
# NODES
# <><><><><><><><><><><><><><><><><><><><><>

class NumberNode:
    def __init__(self, token):
        self.tokens = token

    def __repr__(self):
        return f"{self.tokens}"
class BinOpNode:
    def __init__(self, left, op_token, right):
        self.left = left
        self.right = right
        self.op_token = op_token

    def __repr__(self):
        return f"({self.left} {self.op_token} {self.right})"

# <><><><><><><><><><><><><><><><><><><><><>
# PARSER
#<><><><><><><><><><><><><><><><><><><><><>

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.tok_idx = 1
        self.advance()

    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok

    def factor(self):
        token = self.current_tok

        if token.type in (TT_INT, TT_FLOAT):
            self.advance()
            return NumberNode(token)
        pass
    def term(self):
        pass
    def expr(self):
        pass


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
    RESET = '\033[0m' # Resets color to default