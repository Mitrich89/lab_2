import unittest
from calculator import (
    parse, evaluate, ParseError, EvalError,
    Number, BinOp, UnaryOp
)

class TestParserStage2(unittest.TestCase):
    """Модульные тесты парсера (Этап 2): научная нотация, степень, скобки"""

    def test_scientific_notation(self):
        """Числа в научной нотации парсятся корректно"""
        self.assertEqual(parse("1.25e+09"), Number(1.25e9))
        self.assertEqual(parse("2.5E-03"), Number(2.5e-3))

    def test_exponentiation(self):
        """Оператор ^ создаёт правоассоциативное дерево"""
        self.assertEqual(parse("3^4"), BinOp('^', Number(3.0), Number(4.0)))
        ast = parse("2^3^4")
        expected = BinOp('^', Number(2.0),
                         BinOp('^', Number(3.0), Number(4.0)))
        self.assertEqual(ast, expected)

    def test_parentheses(self):
        """Скобки изменяют порядок вычислений"""
        ast = parse("1+2/(3+4)")
        expected = BinOp('+', Number(1.0),
                         BinOp('/', Number(2.0),
                                BinOp('+', Number(3.0), Number(4.0))))
        self.assertEqual(ast, expected)

    def test_combined_new_features(self):
        """Выражение с научной нотацией, степенью и скобками"""
        ast = parse("3.375e+09^(1/3)")
        inner = BinOp('/', Number(1.0), Number(3.0))
        expected = BinOp('^', Number(3.375e9), inner)
        self.assertEqual(ast, expected)

    def test_invalid_expressions(self):
        """По-прежнему ловятся неверные конструкции"""
        with self.assertRaises(ParseError):
            parse("2 / ")
        with self.assertRaises(ParseError):
            parse("1 + 4j")

    def test_power_with_unary_minus(self):
        """2^-3 = 0.125"""
        ast = parse("2^-3")
        expected = BinOp('^', Number(2.0), UnaryOp('-', Number(3.0)))
        self.assertEqual(ast, expected)

    def test_power_unary_minus_and_right_associativity(self):
        """2^-3^2 = 2^(-(3^2)) = 2^(-9)"""
        ast = parse("2^-3^2")
        expected = BinOp('^', Number(2.0),
                         UnaryOp('-', BinOp('^', Number(3.0), Number(2.0))))
        self.assertEqual(ast, expected)

class TestEvaluatorStage2(unittest.TestCase):
    """Тесты вычислителя (Этап 2)"""

    def test_power(self):
        """3^4 = 81"""
        self.assertEqual(evaluate(BinOp('^', Number(3.0), Number(4.0))), 81.0)

    def test_basic_ops_still_work(self):
        """Старые операции работают"""
        self.assertEqual(evaluate(BinOp('+', Number(2.0), Number(2.0))), 4.0)

    def test_overflow_power(self):
        """Переполнение при возведении в степень -> EvalError (через parse)"""
        with self.assertRaises(EvalError):
            evaluate(parse("1.000000000000001 ^ 36893488147419103232"))

    def test_negative_base_fractional_exponent(self):
        """Отрицательное основание и нецелая степень → ошибка"""
        with self.assertRaises(EvalError):
            evaluate(parse("(-2)^0.5"))

    def test_unary_minus_exponent(self):
        """2^-3 = 0.125"""
        self.assertAlmostEqual(evaluate(parse("2^-3")), 0.125)

    def test_unary_minus_exponent_right_assoc(self):
        """2^-3^2 = 2^(-9) ≈ 0.001953"""
        self.assertAlmostEqual(evaluate(parse("2^-3^2")), 2.0 ** -9)

# Интеграционные тесты
class TestIntegration(unittest.TestCase):
    """Совместная работа парсера и вычислителя (интеграционные)"""

    def test_simple_eval(self):
        """1+1 = 2 через parse+evaluate"""
        self.assertEqual(evaluate(parse("1+1")), 2.0)

    def test_scientific_and_power(self):
        """3.375e+09^(1/3) ≈ 1500.0"""
        self.assertAlmostEqual(evaluate(parse("3.375e+09^(1/3)")), 1500.0, places=5)

    def test_parser_error_propagation(self):
        """Ошибка парсера доходит до evaluate"""
        with self.assertRaises(ParseError):
            evaluate(parse("1 /"))

    def test_eval_error_propagation(self):
        """Ошибка вычислителя (деление на 0) пробрасывается"""
        with self.assertRaises(EvalError):
            evaluate(parse("1/0"))

if __name__ == '__main__':
    unittest.main()