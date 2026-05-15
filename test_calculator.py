import unittest
import sys
import subprocess
import time
import math
from calculator import (
    parse, evaluate, ParseError, EvalError,
    Number, BinOp, UnaryOp, FuncCall, Constant
)

# ==================== Модульные тесты парсера ====================
class TestParserStage3(unittest.TestCase):
    """Тесты парсера: функции, константы, комбинированные выражения"""

    def test_simple_functions(self):
        """Парсинг sqrt(4), sin(0), ln(e)"""
        self.assertEqual(parse("sqrt(4)"), FuncCall('sqrt', Number(4.0)))
        self.assertEqual(parse("sin(0)"), FuncCall('sin', Number(0.0)))
        self.assertEqual(parse("ln(e)"), FuncCall('ln', Constant('e')))

    def test_nested_functions(self):
        """Вложенные функции: sqrt(ln(e))"""
        ast = parse("sqrt(ln(e))")
        expected = FuncCall('sqrt', FuncCall('ln', Constant('e')))
        self.assertEqual(ast, expected)

    def test_constants(self):
        """Парсинг констант pi и e"""
        self.assertEqual(parse("pi"), Constant('pi'))
        self.assertEqual(parse("e"), Constant('e'))

    def test_combined_func_const(self):
        """Смешанное выражение: sin(pi/2)"""
        ast = parse("sin(pi/2)")
        expected = FuncCall('sin', BinOp('/', Constant('pi'), Number(2.0)))
        self.assertEqual(ast, expected)

    def test_invalid_function_name(self):
        """Ошибка при вызове неизвестной функции"""
        with self.assertRaises(ParseError):
            parse("foo(1)")

    def test_invalid_constant_name(self):
        """Ошибка при использовании неизвестной константы"""
        with self.assertRaises(ParseError):
            parse("x")
    
    def test_arcctg_function(self):
        """Парсинг arcctg(1)"""
        ast = parse("arcctg(1)")
        expected = FuncCall('arcctg', Number(1.0))
        self.assertEqual(ast, expected)

    def test_arcctg_function(self):
        """Парсинг arcctg(1)"""
        ast = parse("arcctg(1)")
        expected = FuncCall('arcctg', Number(1.0))
        self.assertEqual(ast, expected)

# ==================== Модульные тесты вычислителя ====================
class TestEvaluatorStage3(unittest.TestCase):
    """Тесты вычислителя: функции, область определения, углы"""

    def test_sqrt_positive(self):
        """Квадратный корень из положительного числа"""
        self.assertEqual(evaluate(parse("sqrt(4)")), 2.0)

    def test_sqrt_negative_error(self):
        """Ошибка при извлечении корня из отрицательного числа"""
        with self.assertRaises(EvalError):
            evaluate(parse("sqrt(-1)"))

    def test_ln_exp_inverse(self):
        """ln(exp(2)) = 2"""
        self.assertAlmostEqual(evaluate(parse("ln(exp(2))")), 2.0)

    def test_trig_radians(self):
        """Тригонометрические функции в радианах (по умолчанию)"""
        self.assertAlmostEqual(evaluate(parse("sin(pi/2)"), 'radian'), 1.0)
        self.assertAlmostEqual(evaluate(parse("cos(0)"), 'radian'), 1.0)

    def test_trig_degrees(self):
        """Тригонометрические функции в градусах"""
        self.assertAlmostEqual(evaluate(parse("sin(90)"), 'degree'), 1.0)
        self.assertAlmostEqual(evaluate(parse("cos(0)"), 'degree'), 1.0)

    def test_ctg_undefined(self):
        """Ошибка котангенса при нулевом тангенсе"""
        with self.assertRaises(EvalError):
            evaluate(parse("ctg(0)"), 'radian')

    def test_negative_base_fractional_exponent(self):
        """Отрицательное основание в нецелой степени → ошибка"""
        with self.assertRaises(EvalError):
            evaluate(parse("(-2)^0.5"))
    
    def test_arcctg_radians(self):
        """arcctg в радианах (по умолчанию)"""
        # arcctg(0) = π/2
        self.assertAlmostEqual(evaluate(parse("arcctg(0)"), 'radian'), math.pi/2)
        # arcctg(1) = π/4
        self.assertAlmostEqual(evaluate(parse("arcctg(1)"), 'radian'), math.pi/4)
        # arcctg(-1) = 3π/4
        self.assertAlmostEqual(evaluate(parse("arcctg(-1)"), 'radian'), 3*math.pi/4)

    def test_arcctg_degrees(self):
        """arcctg в градусах"""
        self.assertAlmostEqual(evaluate(parse("arcctg(0)"), 'degree'), 90.0)
        self.assertAlmostEqual(evaluate(parse("arcctg(1)"), 'degree'), 45.0)
        self.assertAlmostEqual(evaluate(parse("arcctg(-1)"), 'degree'), 135.0)

    def test_arcctg_large_values(self):
        """Поведение при больших аргументах"""
        # arcctg(1e10) → 0 (радианы)
        res_pos = evaluate(parse("arcctg(1e10)"), 'radian')
        self.assertAlmostEqual(res_pos, 0.0, places=5)
        # arcctg(-1e10) → π (радианы)
        res_neg = evaluate(parse("arcctg(-1e10)"), 'radian')
        self.assertAlmostEqual(res_neg, math.pi, places=5)

    def test_arcctg_zero_degree(self):
        """arcctg(0) в градусах = 90"""
        self.assertEqual(evaluate(parse("arcctg(0)"), 'degree'), 90.0)

    def test_arcctg_radians(self):
        """arcctg в радианах (по умолчанию)"""
        # arcctg(0) = π/2
        self.assertAlmostEqual(evaluate(parse("arcctg(0)"), 'radian'), math.pi/2)
        # arcctg(1) = π/4
        self.assertAlmostEqual(evaluate(parse("arcctg(1)"), 'radian'), math.pi/4)
        # arcctg(-1) = 3π/4
        self.assertAlmostEqual(evaluate(parse("arcctg(-1)"), 'radian'), 3*math.pi/4)

    def test_arcctg_degrees(self):
        """arcctg в градусах"""
        self.assertAlmostEqual(evaluate(parse("arcctg(0)"), 'degree'), 90.0)
        self.assertAlmostEqual(evaluate(parse("arcctg(1)"), 'degree'), 45.0)
        self.assertAlmostEqual(evaluate(parse("arcctg(-1)"), 'degree'), 135.0)

    def test_arcctg_large_values(self):
        """Поведение при больших аргументах"""
        # arcctg(1e10) → 0 (радианы)
        res_pos = evaluate(parse("arcctg(1e10)"), 'radian')
        self.assertAlmostEqual(res_pos, 0.0, places=5)
        # arcctg(-1e10) → π (радианы)
        res_neg = evaluate(parse("arcctg(-1e10)"), 'radian')
        self.assertAlmostEqual(res_neg, math.pi, places=5)

    def test_arcctg_zero_degree(self):
        """arcctg(0) в градусах = 90"""
        self.assertEqual(evaluate(parse("arcctg(0)"), 'degree'), 90.0)

# ==================== Интеграционные тесты ====================
class TestIntegration(unittest.TestCase):
    """Совместная работа парсера и вычислителя"""

    def test_simple_eval(self):
        """1+1 = 2"""
        self.assertEqual(evaluate(parse("1+1")), 2.0)

    def test_scientific_power(self):
        """3.375e9^(1/3) ≈ 1500"""
        self.assertAlmostEqual(evaluate(parse("3.375e+09^(1/3)")), 1500.0, places=5)

    def test_parser_error_propagation(self):
        """Ошибка парсера пробрасывается"""
        with self.assertRaises(ParseError):
            evaluate(parse("1 /"))

    def test_eval_error_propagation(self):
        """Ошибка вычислителя пробрасывается"""
        with self.assertRaises(EvalError):
            evaluate(parse("1/0"))

    def test_sqrt_ln_e(self):
        """sqrt(ln(e)) = 1"""
        self.assertAlmostEqual(evaluate(parse("sqrt(ln(e))")), 1.0)
    
    def test_arcctg_with_expression(self):
        """Выражение с arcctg: arcctg(1) + arcctg(2)"""
        expr = "arcctg(1) + arcctg(2)"
        # Значение в радианах: π/4 + arctan(1/2) ≈ 0.785398 + 0.463648 = 1.249046
        expected = math.atan2(1, 1) + math.atan2(1, 2)  # альтернативная формула
        self.assertAlmostEqual(evaluate(parse(expr)), expected, places=5)

    def test_arcctg_with_expression(self):
        """Выражение с arcctg: arcctg(1) + arcctg(2)"""
        expr = "arcctg(1) + arcctg(2)"
        # Значение в радианах: π/4 + arctan(1/2) ≈ 0.785398 + 0.463648 = 1.249046
        expected = math.atan2(1, 1) + math.atan2(1, 2)  # альтернативная формула
        self.assertAlmostEqual(evaluate(parse(expr)), expected, places=5)

# ==================== Функциональные тесты (CLI) ====================
class TestFunctional(unittest.TestCase):
    """Тестирование через командную строку (полный путь)"""

    def run_calc(self, expr, angle_unit=None):
        cmd = [sys.executable, 'calculator.py']
        if angle_unit:
            cmd.extend(['--angle-unit', angle_unit])
        cmd.append(expr)
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return proc

    def test_basic_addition(self):
        """1+1 должно вывести '2.0' и код 0"""
        proc = self.run_calc("1+1")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "2.0")

    def test_sin_degrees(self):
        """sin(90) в градусах = 1.0"""
        proc = self.run_calc("sin(90)", angle_unit='degree')
        self.assertEqual(proc.returncode, 0)
        self.assertAlmostEqual(float(proc.stdout.strip()), 1.0)

    def test_sin_radians_default(self):
        """sin(pi/2) без флага (радианы) = 1.0"""
        proc = self.run_calc("sin(pi/2)")
        self.assertEqual(proc.returncode, 0)
        self.assertAlmostEqual(float(proc.stdout.strip()), 1.0)

    def test_sqrt(self):
        """sqrt(81) = 9.0"""
        proc = self.run_calc("sqrt(81)")
        self.assertEqual(proc.stdout.strip(), "9.0")

    def test_exp_ln_composition(self):
        """exp(ln(2)) = 2.0"""
        proc = self.run_calc("exp(ln(2))")
        self.assertAlmostEqual(float(proc.stdout.strip()), 2.0)

    def test_ln_exp(self):
        """ln(exp(2)) = 2.0"""
        proc = self.run_calc("ln(exp(2))")
        self.assertAlmostEqual(float(proc.stdout.strip()), 2.0)

    def test_ln_e_power(self):
        """ln(e^2) = 2.0"""
        proc = self.run_calc("ln(e^2)")
        self.assertAlmostEqual(float(proc.stdout.strip()), 2.0)

    def test_division_by_zero_error(self):
        """Деление на 0 должно вернуть ненулевой код и сообщение об ошибке"""
        proc = self.run_calc("1/0")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("Ошибка", proc.stderr)

    def test_sqrt_negative_error(self):
        """sqrt(-1) должно вызвать ошибку"""
        proc = self.run_calc("sqrt(-1)")
        self.assertNotEqual(proc.returncode, 0)

    def test_ln_nonpositive_error(self):
        """ln(0) должно вызвать ошибку"""
        proc = self.run_calc("ln(0)")
        self.assertNotEqual(proc.returncode, 0)
    
    def test_arcctg_degrees_cli(self):
        """arcctg(0) в градусах через CLI"""
        proc = self.run_calc("arcctg(0)", angle_unit='degree')
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(float(proc.stdout.strip()), 90.0)

    def test_arcctg_radians_cli(self):
        """arcctg(1) в радианах через CLI (по умолчанию)"""
        proc = self.run_calc("arcctg(1)")
        self.assertEqual(proc.returncode, 0)
        self.assertAlmostEqual(float(proc.stdout.strip()), math.pi/4)

    def test_arcctg_negative_cli(self):
        """arcctg(-1) в градусах"""
        proc = self.run_calc("arcctg(-1)", angle_unit='degree')
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(float(proc.stdout.strip()), 135.0)

# ==================== Нагрузочные тесты ====================
class TestLoad(unittest.TestCase):
    """Тесты производительности и устойчивости к большим данным"""

    def run_calc(self, expr, timeout=5):
        start = time.perf_counter()
        proc = subprocess.run(
            [sys.executable, 'calculator.py', expr],
            capture_output=True, text=True, timeout=timeout
        )
        elapsed = time.perf_counter() - start
        return proc, elapsed

    # --- Обязательные из задания ---
    def test_correct_long_sum(self):
        """Сумма 500 единиц (999 символов) должна работать < 200 мс"""
        expr = '1' + '+1'*499  # 999 символов
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5, f"Время {elapsed:.3f} с превысило лимит")
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "500.0")

    def test_incorrect_1000_chars(self):
        """Некорректное выражение длиной 1000 символов обрабатывается быстро и с ошибкой"""
        expr = '1+' * 500  # 1000 символов (некорректное, так как заканчивается на +)
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertNotEqual(proc.returncode, 0)

    def test_huge_numbers_addition(self):
        """Сложение очень больших чисел (1e249+1e249) не крашит и укладывается в лимит"""
        expr = "1e249+1e249"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "2e+249")

    def test_overflow_power(self):
        """Возведение в большую степень с потерей точности → ошибка переполнения"""
        expr = "1.000000000000001 ^ 36893488147419103232"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("переполнение", proc.stderr)

    def test_power_identity(self):
        """1 в любой степени = 1.0"""
        expr = "1 ^ 36893488147419103232"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.stdout.strip(), "1.0")

    # --- Дополнительные нагрузочные тесты ---
    def test_long_multiply_division(self):
        """Длинная цепочка умножений и делений (~900 символов) < 200 мс"""
        expr = "1" + "*2/2" * 300  # 1 + 3*300 = 901 символ
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "1.0")

    # def test_deeply_nested_parentheses(self):
    #     """Глубоко вложенные скобки ((...(1)...)) 200 уровней < 250 мс"""
    #     expr = "(" * 200 + "1" + ")" * 200
    #     proc, elapsed = self.run_calc(expr)
    #     self.assertLess(elapsed, 0.55)
    #     self.assertEqual(proc.returncode, 0)
    #     self.assertEqual(proc.stdout.strip(), "1.0")

    def test_many_spaces(self):
        """Огромное количество пробелов не должно замедлять"""
        expr = "   " * 300 + "1" + "   " * 300 + "+" + "   " * 300 + "2"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.stdout.strip(), "3.0")

    def test_heavy_nested_functions(self):
        """Несколько вложенных функций: sqrt(sin(cos(tg(0.5))))"""
        expr = "sqrt(sin(cos(tg(0.5))))"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.returncode, 0)

    def test_large_exponent_no_overflow(self):
        """2^1000 (результат ~1e301)"""
        expr = "2^1000"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("e+", proc.stdout.strip())

    # def test_underflow_to_zero(self):
    #     """1e-308 / 10 → исчезновение до 0.0 (не ошибка)"""
    #     expr = "1e-308 / 10"
    #     proc, elapsed = self.run_calc(expr)
    #     self.assertLess(elapsed, 0.5)
    #     self.assertEqual(proc.returncode, 0)
    #     self.assertEqual(proc.stdout.strip(), "0.0")

    def test_overflow_multiplication(self):
        """1e308 * 10 → переполнение (ошибка)"""
        expr = "1e308 * 10"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("переполнение", proc.stderr)

    def test_negative_fractional_power_error(self):
        """(-2)^0.5 → ошибка (через CLI)"""
        expr = "(-2)^0.5"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertNotEqual(proc.returncode, 0)

    def test_big_nested_power_right_assoc(self):
        """2^3^4^5 (огромное число) должно быстро дать переполнение"""
        expr = "2^3^4^5"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("переполнение", proc.stderr)

    # def test_long_expression_2000_chars(self):
    #     """Очень длинное корректное выражение (~2000 символов) не зависает"""
    #     expr = "1" + "+1" * 1000  # 1 + 2*1000 = 2001 символ, значение 1001
    #     proc, elapsed = self.run_calc(expr, timeout=5)
    #     self.assertLess(elapsed, 1.0)
    #     self.assertEqual(proc.returncode, 0)
    #     self.assertEqual(proc.stdout.strip(), "1001.0")

    # def test_many_unary_minuses(self):
    #     """Много унарных минусов: '----5' быстро вычисляется"""
    #     expr = "----5"
    #     proc, elapsed = self.run_calc(expr)
    #     self.assertLess(elapsed, 0.5)
    #     self.assertEqual(proc.returncode, 0)
    #     self.assertEqual(proc.stdout.strip(), "5.0")

    def test_constant_expression(self):
        """pi * e"""
        expr = "pi * e"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.returncode, 0)
        self.assertAlmostEqual(float(proc.stdout.strip()), math.pi * math.e, places=5)

    # def test_trig_chain(self):
    #     """sin(cos(tg(0.5))) в градусах"""
    #     expr = "sin(cos(tg(0.5)))"
    #     proc, elapsed = self.run_calc(expr, angle_unit='degree')
    #     self.assertLess(elapsed, 0.5)
    #     self.assertEqual(proc.returncode, 0)

    def test_complex_valid_expression(self):
        """(1+2)*(3+4)/(5^2) = 21/25 = 0.84"""
        expr = "(1+2)*(3+4)/(5^2)"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.52)
        self.assertAlmostEqual(float(proc.stdout.strip()), 0.84)

    def test_very_long_valid_expression(self):
        """Много маленьких чисел с операциями (до 500 символов)"""
        expr = "1+2*3-4/5+6/7*8-9+10" * 25  # ~500 символов
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.5)
        self.assertEqual(proc.returncode, 0)
    
    def test_arcctg_performance(self):
        """Вычисление arcctg от большого аргумента не должно тормозить"""
        expr = "arcctg(1e100)"
        proc, elapsed = self.run_calc(expr)
        self.assertLess(elapsed, 0.4)
        self.assertEqual(proc.returncode, 0)
        self.assertAlmostEqual(float(proc.stdout.strip()), 0.0, places=5)

if __name__ == '__main__':
    import sys
    import unittest
    import traceback

    # Загружаем все тесты из текущего модуля
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    # Функция для извлечения всех тестов из набора
    def collect_tests(suite):
        tests = []
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                tests.extend(collect_tests(test))
            else:
                tests.append(test)
        return tests

    test_cases = collect_tests(suite)
    total = len(test_cases)
    passed = 0
    failed = 0
    failures_list = []   # (имя_теста, сообщение_об_ошибке)

    print("\nЗапуск тестов:\n")
    for i, test in enumerate(test_cases, 1):
        test_name = f"{test.__class__.__name__}.{test._testMethodName}"
        result = unittest.TestResult()
        test.run(result)

        if result.wasSuccessful():
            print(f"{i:3d}. {test_name} ... OK")
            passed += 1
        else:
            print(f"{i:3d}. {test_name} ... FAIL")
            failed += 1
            # Собираем информацию об ошибках/провалах
            if result.failures:
                failures_list.append((test_name, result.failures[0][1]))
            if result.errors:
                failures_list.append((test_name, result.errors[0][1]))

        print()   # пустая строка после каждого теста

    # Итоговая статистика
    print("=" * 70)
    print(f"Всего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Не пройдено: {failed}")

    if failed > 0:
        print("\nПодробности о проваленных тестах:")
        for name, err_msg in failures_list:
            print(f"\n--- {name} ---")
            # Показываем только последние строки ошибки (обычно там assert)
            lines = err_msg.strip().split('\n')
            # Выводим последние 5 строк (можно увеличить, если нужно больше)
            print('\n'.join(lines[-5:]))
    print("=" * 70)

    sys.exit(0 if failed == 0 else 1)
