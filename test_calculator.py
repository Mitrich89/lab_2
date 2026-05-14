import unittest
import sys
import subprocess
from calculator import (
    tokenize, parse, evaluate,
    ParseError, EvalError,
    Number, BinOp, UnaryOp
)

class TestParserStage1(unittest.TestCase):
    def test_number(self):
        self.assertEqual(parse("42"), Number(42.0))
        self.assertEqual(parse("3.14"), Number(3.14))

    def test_simple_ops(self):
        self.assertEqual(parse("1+2"), BinOp('+', Number(1.0), Number(2.0)))
        self.assertEqual(parse("3-1"), BinOp('-', Number(3.0), Number(1.0)))
        self.assertEqual(parse("2*3"), BinOp('*', Number(2.0), Number(3.0)))
        self.assertEqual(parse("4/2"), BinOp('/', Number(4.0), Number(2.0)))

    def test_priority(self):
        ast = parse("1+2*3")
        expected = BinOp('+', Number(1.0),
                        BinOp('*', Number(2.0), Number(3.0)))
        self.assertEqual(ast, expected)

    def test_multi_digit(self):
        self.assertEqual(parse("123"), Number(123.0))
        self.assertEqual(parse("45+67"), BinOp('+', Number(45.0), Number(67.0)))

    def test_invalid_expressions(self):
        with self.assertRaises(ParseError):
            parse("2 / ")
        with self.assertRaises(ParseError):
            parse("1 + 4j")
        with self.assertRaises(ParseError):
            parse("2 ^ 4")          # на этапе 1 ^ запрещён
        with self.assertRaises(ParseError):
            parse("(1+2")           # скобки запрещены
        with self.assertRaises(ParseError):
            parse("1+2)")

    def test_spaces_ignored(self):
        # проверяем, что разные пробелы дают одинаковое дерево
        ast1 = parse("1+2")
        ast2 = parse("1 + 2")
        ast3 = parse(" 1+ 2")
        self.assertEqual(ast1, ast2)
        self.assertEqual(ast2, ast3)

class TestEvaluatorStage1(unittest.TestCase):
    def test_number(self):
        self.assertEqual(evaluate(Number(42.0)), 42.0)

    def test_basic_ops(self):
        self.assertEqual(evaluate(BinOp('+', Number(2.0), Number(2.0))), 4.0)
        self.assertEqual(evaluate(BinOp('-', Number(5.0), Number(3.0))), 2.0)
        self.assertAlmostEqual(evaluate(BinOp('/', Number(7.0), Number(2.0))), 3.5)

    def test_division_by_zero(self):
        with self.assertRaises(EvalError) as cm:
            evaluate(BinOp('/', Number(2.0), Number(0.0)))
        self.assertIn("Деление на 0", str(cm.exception))

    def test_overflow(self):
        with self.assertRaises(EvalError):
            evaluate(BinOp('/', Number(1e300), Number(1e-300)))

    def test_precision(self):
        # 1 + 1e-23 -> 1.0 для float64
        self.assertEqual(evaluate(BinOp('+', Number(1.0), Number(1e-23))), 1.0)

if __name__ == '__main__':
    unittest.main()