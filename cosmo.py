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
    def advance(self, current_char = None):
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
TT_EOF = 'EOF'


class Token:
    def __init__(self, type_, value=None, pos_start=None, pos_end=None):
        self.type_ = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end.copy()

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
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_number())
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS, pos_start = self.pos)); self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS, pos_start = self.pos)); self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL, pos_start = self.pos)); self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV, pos_start = self.pos)); self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN, pos_start = self.pos)); self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN, pos_start = self.pos)); self.advance()
            else:
                pos_start = self.pos.copy()
                ch = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos, "'" + ch + "'")

        tokens.append(Token(TT_EOF, pos_start = self.pos))
        return tokens, None

    def make_number(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()
        while self.current_char is not None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += "."
            else:
                num_str += self.current_char
            self.advance()

        if dot_count == 0:
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT, float(num_str), pos_start, self.pos)

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
class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node
    def __repr__(self):
        return f"({self.op_tok} {self.node})"

# <><><><><><><><><><><><><><><><><><><><><>
# PARSE RESULT
# <><><><><><><><><><><><><><><><><><><><><>

class ParseResult:
    def __init__(self):
        self.error = None
        self.node = None

    def register(self, res):
        if isinstance(res, ParseResult):
            if res.error: self.error = res.error
            return res.node
        return res

    def success(self, node):
        self.node = node
        return self

    def fail(self, error):
        self.error = error
        return self

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
        res = self.expr()
        if not res.error and self.current_tok.type_ != TT_EOF:
            return res.fail(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Excpected '+', '-', '*', '/'"))
        return res

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type_ in (TT_PLUS, TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, factor))

        elif tok.type_ in (TT_INT, TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))

        elif tok.type_ == TT_LPAREN:
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.current_tok.type_ == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.fail(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Excpected ')' "))

        return res.fail(InvalidSyntaxError(tok.pos_start, tok.pos_end, "Expected int or float"))

        # if tok.type_ == TT_LPAREN:
        #     self.advance()
        #     node = self.expr()
        #     if self.current_tok and self.current_tok.type_ == TT_RPAREN:
        #         self.advance()
        #     return node
        # if tok.type_ in (TT_PLUS, TT_MINUS):
        #     # unary +/-
        #     op = tok
        #     self.advance()
        #     node = self.factor()
        #     return BinOpNode(NumberNode(Token(TT_INT, 0)), op, node)
        # return None

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func, ops):
        res = ParseResult()
        left = res.register(func())
        if res.error: return res
        while self.current_tok.type_ in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)

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
    return ast.node, ast.error

# <><><><><><><><><><><><><><><><><><><><><>
# COLORS
# <><><><><><><><><><><><><><><><><><><><><>
class Colors:
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
