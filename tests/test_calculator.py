import calculator as calc


def run(*steps):
    s = calc.State()
    for step in steps:
        s = step(s)
    return s


def d(n):
    return lambda s: calc.digit(s, n)


def op(o):
    return lambda s: calc.operator(s, o)


def test_addition():
    assert run(d("2"), op("+"), d("3"), calc.equals).current == "5"


def test_chained_operations_evaluate_left_to_right():
    assert run(d("2"), op("+"), d("3"), op("*"), d("4"), calc.equals).current == "20"


def test_decimal_input_and_float_rounding():
    s = run(d("0"), calc.decimal, d("1"), op("+"), d("0"), calc.decimal, d("2"), calc.equals)
    assert s.current == "0.3"


def test_large_results_keep_full_precision():
    s = run(d("1"), d("2"), d("3"), d("4"), d("5"), d("6"), d("7"), op("*"), d("1"), calc.equals)
    assert s.current == "1234567"


def test_second_decimal_point_ignored():
    assert run(d("1"), calc.decimal, d("5"), calc.decimal).current == "1.5"


def test_divide_by_zero_is_error_and_recovers():
    s = run(d("5"), op("/"), d("0"), calc.equals)
    assert s.current == calc.ERROR
    assert calc.digit(s, "7").current == "7"


def test_chained_divide_by_zero_is_error():
    assert run(d("5"), op("/"), d("0"), op("+")).current == calc.ERROR


def test_operator_change_before_second_operand():
    assert run(d("8"), op("+"), op("-"), d("3"), calc.equals).current == "5"


def test_sign_percent_and_clear():
    assert run(d("5"), calc.toggle_sign).current == "-5"
    assert run(d("5"), d("0"), calc.percent).current == "0.5"
    assert run(d("9"), op("+"), calc.clear) == calc.State()


def test_backspace():
    assert run(d("1"), d("2"), calc.backspace).current == "1"
    assert run(d("1"), calc.backspace).current == "0"
    assert run(d("5"), calc.toggle_sign, calc.backspace).current == "0"


def test_no_leading_zeros():
    assert run(d("0"), d("0"), d("7")).current == "7"


def test_history_shows_pending_operation():
    assert calc.history(run(d("6"), op("*"))) == "6 ×"
