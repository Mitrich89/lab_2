import sys
import re
import math
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

# ---------- Лексер ----------
TOKEN_REGEX = re.compile(r"""
    \s*
    (?:
        (\d+\.?\d*)                 # число (без экспоненты)
      | ([+\-*/()])                 # операторы и скобки (^ пока нет)
      | ([a-zA-Z_][a-zA-Z_0-9]*)    # идентификатор (пока ошибка)
      | (.)                         # недопустимый символ
    )
""", re.VERBOSE)

def tokenize(expr: str) -> List[Tuple[str, object]]:
    tokens = []
    for m in TOKEN_REGEX.finditer(expr):
        if m.group(1) is not None:          # число
            tokens.append(('NUMBER', float(m.group(1))))
        elif m.group(2) is not None:        # оператор/скобка
            op = m.group(2)
            if op == '^':
                raise ParseError(f"Оператор '^' не поддерживается")
            tokens.append(('OP', op))
        elif m.group(3) is not None:        # идентификатор
            raise ParseError(f"Идентификаторы не поддерживаются: '{m.group(3)}'")
        elif m.group(4) is not None:        # недопустимый
            raise ParseError(f"Недопустимый символ: '{m.group(4)}'")
    return tokens

# ---------- Парсер ----------
class Parser:
    def __init__(self, tokens: List[tuple]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[tuple]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type: Optional[str] = None, expected_value: Optional[str] = None) -> tuple:
        tok = self.peek()
        if tok is None:
            raise ParseError("Неожиданный конец выражения")
        if expected_type is not None and tok[0] != expected_type:
            raise ParseError(f"Ожидался {expected_type}, получен {tok[0]} ('{tok[1]}')")
        if expected_value is not None and tok[1] != expected_value:
            raise ParseError(f"Ожидался '{expected_value}', получен '{tok[1]}'")
        self.pos += 1
        return tok

    def parse(self) -> AST:
        tree = self.expr()
        if self.pos != len(self.tokens):
            raise ParseError("Лишние символы после выражения")
        return tree

    def expr(self) -> AST:
        left = self.term()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('+', '-'):
            op = self.consume('OP')[1]
            right = self.term()
            left = BinOp(op, left, right)
        return left

    def term(self) -> AST:
        left = self.unary()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('*', '/'):
            op = self.consume('OP')[1]
            right = self.unary()
            left = BinOp(op, left, right)
        return left

    def unary(self) -> AST:
        tok = self.peek()
        if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
            op = self.consume('OP')[1]
            operand = self.unary()
            return UnaryOp(op, operand)
        else:
            return self.atom()

    def atom(self) -> AST:
        tok = self.peek()
        if tok is None:
            raise ParseError("Неожиданный конец выражения")
        if tok[0] == 'NUMBER':
            return Number(self.consume('NUMBER')[1])
        elif tok[0] == 'OP' and tok[1] == '(':
            raise ParseError("Скобки не поддерживаются")
        else:
            raise ParseError(f"Неожиданный токен: {tok}")

def parse(expr: str) -> AST:
    tokens = tokenize(expr)
    parser = Parser(tokens)
    return parser.parse()

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
        else:
            raise EvalError(f"Неизвестная операция: {ast.op}")
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