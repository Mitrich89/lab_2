import sys, re, math
from dataclasses import dataclass
from typing import List, Union, Optional, Tuple

class ParseError(Exception):
    pass

class EvalError(Exception):
    pass

@dataclass
class Number:
    value: float

@dataclass
class BinOp:
    op: str
    left: 'AST'
    right: 'AST'

@dataclass
class UnaryOp:
    op: str
    operand: 'AST'

AST = Union[Number, BinOp, UnaryOp]

# ---------- Лексер (научная нотация) ----------
TOKEN_REGEX = re.compile(r"""
    \s*
    (?:
        (\d+\.?\d*(?:[eE][+-]?\d+)?)   # число с экспонентой
      | ([+\-*/^()])                   # операторы (добавлен ^)
      | ([a-zA-Z_][a-zA-Z_0-9]*)       # идентификатор (пока ошибка)
      | (.)                            # недопустимый символ
    )
""", re.VERBOSE)

def tokenize(expr: str) -> List[Tuple[str, object]]:
    tokens = []
    for m in TOKEN_REGEX.finditer(expr):
        if m.group(1) is not None:
            tokens.append(('NUMBER', float(m.group(1))))
        elif m.group(2) is not None:
            tokens.append(('OP', m.group(2)))
        elif m.group(3) is not None:
            raise ParseError(f"Идентификаторы не поддерживаются: '{m.group(3)}'")
        elif m.group(4) is not None:
            raise ParseError(f"Недопустимый символ: '{m.group(4)}'")
    return tokens

# ---------- Парсер (добавлены power и скобки) ----------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_type=None, expected_value=None):
        tok = self.peek()
        if tok is None:
            raise ParseError("Неожиданный конец выражения")
        if expected_type is not None and tok[0] != expected_type:
            raise ParseError(f"Ожидался {expected_type}, получен {tok[0]} ('{tok[1]}')")
        if expected_value is not None and tok[1] != expected_value:
            raise ParseError(f"Ожидался '{expected_value}', получен '{tok[1]}'")
        self.pos += 1
        return tok

    def parse(self):
        tree = self.expr()
        if self.pos != len(self.tokens):
            raise ParseError("Лишние символы после выражения")
        return tree

    def expr(self):
        left = self.term()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('+', '-'):
            op = self.consume('OP')[1]
            right = self.term()
            left = BinOp(op, left, right)
        return left

    def term(self):
        left = self.unary()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('*', '/'):
            op = self.consume('OP')[1]
            right = self.unary()
            left = BinOp(op, left, right)
        return left

    def unary(self):
        tok = self.peek()
        if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
            op = self.consume('OP')[1]
            operand = self.unary()
            return UnaryOp(op, operand)
        return self.power()

    def power(self):
        left = self.atom()
        if self.peek() and self.peek()[0] == 'OP' and self.peek()[1] == '^':
            self.consume('OP', '^')
            # необязательный унарный знак перед показателем
            sign = None
            if self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('+', '-'):
                sign = self.consume('OP')[1]
            right = self.power()
            if sign == '-':
                right = UnaryOp('-', right)
            # унарный '+' игнорируется
            return BinOp('^', left, right)
        return left

    def atom(self):
        tok = self.peek()
        if tok is None:
            raise ParseError("Неожиданный конец выражения")
        if tok[0] == 'NUMBER':
            return Number(self.consume('NUMBER')[1])
        elif tok[0] == 'OP' and tok[1] == '(':
            self.consume('OP', '(')
            expr = self.expr()
            self.consume('OP', ')')
            return expr
        else:
            raise ParseError(f"Неожиданный токен: {tok}")

def parse(expr: str) -> AST:
    return Parser(tokenize(expr)).parse()

# ---------- Вычислитель ----------
def evaluate(ast: AST) -> float:
    if isinstance(ast, Number):
        return ast.value
    elif isinstance(ast, BinOp):
        left = evaluate(ast.left)
        right = evaluate(ast.right)
        if ast.op == '+':
            res = left + right
        elif ast.op == '-':
            res = left - right
        elif ast.op == '*':
            res = left * right
        elif ast.op == '/':
            if right == 0:
                raise EvalError("Деление на 0")
            res = left / right
        elif ast.op == '^':
            if left < 0 and not right.is_integer():
                raise EvalError("Отрицательное число в нецелой степени не определено в действительных числах")
            try:
                res = left ** right
                return res
            except OverflowError:
                raise EvalError("Арифметическое переполнение")     
        else:
            raise EvalError(f"Неизвестная операция: {ast.op}")

        # Проверка переполнения для любой бинарной операции
        if math.isinf(res) or math.isnan(res):
            raise EvalError("Арифметическое переполнение")
        return res

    elif isinstance(ast, UnaryOp):
        val = evaluate(ast.operand)
        res = -val if ast.op == '-' else val
        if math.isinf(res) or math.isnan(res):
            raise EvalError("Арифметическое переполнение")
        return res
    else:
        raise EvalError("Неизвестный узел AST")

# ---------- CLI ----------
def main():
    if len(sys.argv) < 2:
        print("Использование: python calculator.py выражение", file=sys.stderr)
        sys.exit(1)
    expr = sys.argv[1]
    try:
        ast = parse(expr)
        result = evaluate(ast)
        print(result)
    except (ParseError, EvalError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()