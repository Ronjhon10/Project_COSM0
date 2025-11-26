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
class RTError(Error):
    def __init__(self, position_start, position_end, details, context):
        super().__init__(position_start, position_end, 'Runtime Error', details)
        self.context = context

    def as_string(self):
        result = self.generate_traceback()
        result += f'{self.error_name}: {self.details}'
        result += '\n\n' + string_with_arrows(self.position_start.ftxt, self.position_start, self.position_end)
        return result

    def generate_traceback(self):
        result = ''
        pos =self.position_start
        ctx = self.context

        while ctx:
            result = f'File {pos.fn}, line {str(pos.ln + 1)}, in {ctx.display_name}\n' + result
            pos = ctx.parent_entry_pos
            ctx = ctx.parent
        return 'Traceback (most recent call last):\n' + result

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
TT_POW = 'POW'
TT_SQRT = 'SQRT'


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
            elif self.current_char == '^':
                tokens.append(Token(TT_POW, pos_start=self.pos))
                self.advance()
            elif self.current_char == '|':
                tokens.append(Token(TT_SQRT, pos_start=self.pos))
                self.advance()
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
        self.pos_start = token.pos_start
        self.pos_end = token.pos_end

    def __repr__(self):
        return f"{self.token}"

class BinOpNode:
    def __init__(self, left, op_token, right):
        self.left = left
        self.right = right
        self.op_token = op_token

        self.pos_start = self.left.pos_start
        self.pos_end = self.right.pos_end

    def __repr__(self):
        return f"({self.left} {self.op_token.type_} {self.right})"

class UnaryOpNode:
    def __init__(self, op_tok, node):
        self.op_tok = op_tok
        self.node = node

        self.pos_start = self.op_tok.pos_start
        self.pos_end = self.node.pos_end

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

    def atom(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type_ in (TT_INT, TT_FLOAT):
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

        return res.fail(InvalidSyntaxError(self.current_tok.pos_start, self.current_tok.pos_end, "Excpected '+', '-', '*', '/'"))

    def power(self):
        return self.bin_op(self.atom, (TT_POW, ), self.factor)

    def factor(self):
        res = ParseResult()
        tok = self.current_tok

        if tok.type_ in (TT_PLUS, TT_MINUS, TT_SQRT):
            res.register(self.advance())
            node = res.register(self.factor())
            if res.error: return res
            return res.success(UnaryOpNode(tok, node))

        return self.power()

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))

    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))

    def bin_op(self, func_a, ops, func_b = None):
        if func_b is None:
            func_b = func_a
        res = ParseResult()
        left = res.register(func_a())
        if res.error: return res
        while self.current_tok.type_ in ops:
            op_tok = self.current_tok
            res.register(self.advance())
            right = res.register(func_b())
            if res.error: return res
            left = BinOpNode(left, op_tok, right)
        return res.success(left)

# <><><><><><><><><><><><><><><><><><><><><>
# Runtime Result
# <><><><><><><><><><><><><><><><><><><><><>
class RTResult:
    def __init__(self):
        self.value = None
        self.error = None

    def register(self, res):
        if res.error: self.error = res.error
        return res.value
    def success(self, value):
        self.value = value
        return self
    def fail(self, error):
        self.error = error
        return self

# <><><><><><><><><><><><><><><><><><><><><>
# Values
# <><><><><><><><><><><><><><><><><><><><><>

class Number:
    def __init__(self, value):
        self.value = value
        self.set_pos()
        self.set_context()

    def set_pos(self, pos_start = None, pos_end = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self

    def set_context(self, context = None):
        self.context = context
        return self

    def added_to(self, other):
        if isinstance(other, Number):
            return Number(self.value + other.value).set_context(self.context), None
    def subtracted_from(self, other):
        if isinstance(other, Number):
            return Number(self.value - other.value).set_context(self.context), None
    def multiply_by(self, other):
        if isinstance(other, Number):
            return Number(self.value * other.value).set_context(self.context), None
    def divided_by(self, other):
        if isinstance(other, Number):
            if other.value == 0:
                return None, RTError(other.pos_start, other.pos_end, "YOU CAN'T FLIPPING DIVIDE BY ZERO", self.context)
            return Number(self.value / other.value).set_context(self.context), None
    def powered_by(self, other):
        if isinstance(other, Number):
            if isinstance(other, Number):
                return Number(self.value ** other.value).set_context(self.context), None
    def rooted(self):
        if self.value < 0:
            return None, RTError(self.pos_start, self.pos_end, "SORRY! No taking the square root of a negative number!", self.context)
        return Number(self.value ** .5).set_context(self.context), None

    def __repr__(self):
        return str(self.value)

# <><><><><><><><><><><><><><><><><><><><><>
# Context
# <><><><><><><><><><><><><><><><><><><><><>
class Context:
    def __init__(self, display_name, parent=None, parent_entry_pos = None):
        self.display_name = display_name
        self.parent = parent
        self.parent_entry_pos = parent_entry_pos

# <><><><><><><><><><><><><><><><><><><><><>
# Interpreter
# <><><><><><><><><><><><><><><><><><><><><>

class Interpreter:
    def visit(self, node, context):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self, method_name, self.no_visit_method)
        return method(node, context)

    def no_visit_method(self,node, context):
        raise Exception(f"No visit_{type(node).__name__} method defined")


    def visit_NumberNode(self, node, context):
        return RTResult().success(Number(node.token.value).set_context(context).set_pos(node.pos_start, node.pos_end))

    def visit_BinOpNode(self, node, context):
        res = RTResult()
        left = res.register(self.visit(node.left, context))
        if res.error: return res
        right = res.register(self.visit(node.right, context))

        if node.op_token.type_ == TT_PLUS:
            result, error = left.added_to(right)
        elif node.op_token.type_ == TT_MINUS:
            result, error = left.subtracted_from(right)
        elif node.op_token.type_ == TT_MUL:
            result, error = left.multiply_by(right)
        elif node.op_token.type_ == TT_DIV:
            result, error = left.divided_by(right)
        elif node.op_token.type_ == TT_POW:
            result, error = left.powered_by(right)

        if error:
            return res.fail(error)
        else:
            return res.success(result.set_pos(node.pos_start, node.pos_end))

    def visit_UnaryOpNode(self, node, context):
        res = RTResult()
        number = res.register(self.visit(node.node, context))
        if res.error: return res

        if node.op_tok.type_ == TT_MINUS:
            number, error = number.multiply_by(Number(-1))
        elif node.op_tok.type_ == TT_SQRT:
            number, error = number.rooted()

        if error: return res.fail(error)
        else:
            return res.success(number.set_pos(node.pos_start, node.pos_end))

# <><><><><><><><><><><><><><><><><><><><><>
# RUN
# <><><><><><><><><><><><><><><><><><><><><>
def run(fn, text):
    #Generates the tokens
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_tokens()
    if error:
        return None, error

    # Generates the syntax tree
    parser = Parser(tokens)
    ast = parser.parse()
    if ast.error: return None, ast.error

    #Run program
    interpreter = Interpreter()
    context = Context('<program>')
    result = interpreter.visit(ast.node, context)

    return result.value, result.error

# <><><><><><><><><><><><><><><><><><><><><>
# COLORS
# <><><><><><><><><><><><><><><><><><><><><>
class Colors:
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
