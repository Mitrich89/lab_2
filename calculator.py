#!/usr/bin/env python3
import math
import re
import argparse
import sys
from dataclasses import dataclass
from typing import List, Union, Optional

# ---------- Исключения ----------
class ParseError(Exception):
    """Ошибка разбора выражения."""

class EvalError(Exception):
    """Ошибка вычисления."""

# ---------- AST-узлы ----------
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

@dataclass
class FuncCall:
    name: str
    arg: 'AST'

@dataclass
class Constant:
    name: str

AST = Union[Number, BinOp, UnaryOp, FuncCall, Constant]

# ---------- Лексер ----------
TOKEN_REGEX = re.compile(r"""
    \s*                                      # пробелы перед токеном
    (?:                                      # любая из альтернатив:
        (                                    # ГРУППА 1 — число целиком
            (?:\d+\.?\d*|\.\d+)              #   целая/дробная часть
            (?:[eE][+-]?\d+)?                #   опциональная экспонента
        )
      | ([+\-*/^()])                         # ГРУППА 2 — оператор/скобка
      | ([a-zA-Z_][a-zA-Z_0-9]*)             # ГРУППА 3 — идентификатор
      | (.)                                  # ГРУППА 4 — недопустимый символ
    )
""", re.VERBOSE)

def tokenize(expr: str) -> list:
    tokens = []
    for m in TOKEN_REGEX.finditer(expr):
        if m.group(1) is not None:          # число
            tokens.append(('NUMBER', float(m.group(1))))
        elif m.group(2) is not None:        # оператор/скобка
            tokens.append(('OP', m.group(2)))
        elif m.group(3) is not None:        # идентификатор
            tokens.append(('ID', m.group(3)))
        elif m.group(4) is not None:        # недопустимый символ
            raise ParseError(f"Недопустимый символ: '{m.group(4)}'")
    return tokens

# ---------- Парсер ----------
FUNCTIONS = {'sqrt', 'sin', 'cos', 'tg', 'ctg', 'ln', 'exp', 'asin', 'arcctg'}
CONSTANTS = {'pi', 'e'}

class Parser:
    def __init__(self, tokens: List[tuple]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Optional[tuple]:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type: Optional[str] = None, expected_value: Optional[str] = None) -> tuple:
        if self.pos >= len(self.tokens):
            raise ParseError("Неожиданный конец выражения")
        tok = self.tokens[self.pos]
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

    # expr = term (('+'|'-') term)*
    def expr(self) -> AST:
        left = self.term()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('+', '-'):
            op = self.consume('OP')[1]
            right = self.term()
            left = BinOp(op, left, right)
        return left

    # term = unary (('*'|'/') unary)*
    def term(self) -> AST:
        left = self.unary()
        while self.peek() and self.peek()[0] == 'OP' and self.peek()[1] in ('*', '/'):
            op = self.consume('OP')[1]
            right = self.unary()
            left = BinOp(op, left, right)
        return left

    # unary = ('+'|'-') unary | power
    def unary(self) -> AST:
        tok = self.peek()
        if tok and tok[0] == 'OP' and tok[1] in ('+', '-'):
            op = self.consume('OP')[1]
            operand = self.unary()
            return UnaryOp(op, operand)
        else:
            return self.power()

    # power = atom ('^' [('+'|'-')] power)?   (правоассоциативная с унарным знаком показателя)
    def power(self) -> AST:
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
            # унарный '+' не меняет знак, его можно игнорировать
            return BinOp('^', left, right)
        return left

    # atom = NUMBER | ID ( '(' expr ')' )? | '(' expr ')' | CONST
    def atom(self) -> AST:
        tok = self.peek()
        if tok is None:
            raise ParseError("Неожиданный конец выражения")
        if tok[0] == 'NUMBER':
            val = self.consume('NUMBER')[1]
            return Number(val)
        elif tok[0] == 'ID':
            name = self.consume('ID')[1]
            # функция?
            if self.peek() and self.peek()[0] == 'OP' and self.peek()[1] == '(':
                self.consume('OP', '(')
                arg = self.expr()
                self.consume('OP', ')')
                if name in FUNCTIONS:
                    return FuncCall(name, arg)
                else:
                    raise ParseError(f"Неизвестная функция: {name}")
            else:
                if name in CONSTANTS:
                    return Constant(name)
                else:
                    raise ParseError(f"Неизвестная константа: {name}")
        elif tok[0] == 'OP' and tok[1] == '(':
            self.consume('OP', '(')
            expr = self.expr()
            self.consume('OP', ')')
            return expr
        else:
            raise ParseError(f"Неожиданный токен: {tok}")

def parse(expr: str) -> AST:
    tokens = tokenize(expr)
    parser = Parser(tokens)
    return parser.parse()

# ---------- Вычислитель ----------
def evaluate(ast: AST, angle_unit: str = 'radian') -> float:
    if isinstance(ast, Number):
        return ast.value
    elif isinstance(ast, BinOp):
        left = evaluate(ast.left, angle_unit)
        right = evaluate(ast.right, angle_unit)
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
            try:
                if left < 0 and not right.is_integer():
                    raise EvalError("Возведение отрицательного числа в нецелую степень")
                res = left ** right
                return res
            except OverflowError:
                raise EvalError("Арифметическое переполнение")
        else:
            raise EvalError(f"Неизвестная операция: {ast.op}")
        if math.isinf(res) or math.isnan(res):
            raise EvalError("Арифметическое переполнение")
        return res
    elif isinstance(ast, UnaryOp):
        val = evaluate(ast.operand, angle_unit)
        if ast.op == '-':
            res = -val
        else:
            res = val
        if math.isinf(res) or math.isnan(res):
            raise EvalError("Арифметическое переполнение")
        return res
    elif isinstance(ast, FuncCall):
        arg = evaluate(ast.arg, angle_unit)
        if ast.name in ('sin', 'cos', 'tg', 'ctg', 'asin'):
            if angle_unit == 'degree':
                arg = math.radians(arg)
            if ast.name == 'sin':
                res = math.sin(arg)
            elif ast.name == 'cos':
                res = math.cos(arg)
            elif ast.name == 'tg':
                res = math.tan(arg)
            elif ast.name == 'asin':
                if not (-1 <= arg <= 1):
                    raise EvalError("Арксинус определён только на [-1, 1]")
                res = math.asin(arg)
            elif ast.name == 'ctg':
                t = math.tan(arg)
                if t == 0:
                    raise EvalError("Котангенс неопределён")
                res = 1.0 / t
        elif ast.name == 'arcctg':
            if arg == 0:
                res = math.pi / 2
            else:
                if arg > 0:
                    res = math.atan(1.0 / arg)
                else:
                    res = math.atan(1.0 / arg) + math.pi
            if angle_unit == 'degree':
                res = math.degrees(res) 
        elif ast.name == 'sqrt':
            if arg < 0:
                raise EvalError("Квадратный корень из отрицательного числа")
            res = math.sqrt(arg)
        elif ast.name == 'ln':
            if arg <= 0:
                raise EvalError("Логарифм неположительного числа")
            res = math.log(arg)
        elif ast.name == 'exp':
            res = math.exp(arg)
        else:
            raise EvalError(f"Неизвестная функция: {ast.name}")
        if math.isinf(res) or math.isnan(res):
            raise EvalError("Арифметическое переполнение")
        return res
    elif isinstance(ast, Constant):
        if ast.name == 'pi':
            return math.pi
        elif ast.name == 'e':
            return math.e
        else:
            raise EvalError(f"Неизвестная константа: {ast.name}")
    else:
        raise EvalError("Неизвестный тип узла")

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Консольный калькулятор")
    parser.add_argument('expression', help="Арифметическое выражение")
    parser.add_argument('--angle-unit', choices=['degree', 'radian'], default='radian',
                        help="Единицы измерения углов (по умолчанию radian)")
    args = parser.parse_args()
    try:
        ast = parse(args.expression)
        result = evaluate(ast, args.angle_unit)
        print(result)
    except (ParseError, EvalError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()