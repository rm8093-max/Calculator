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


def fn(name):
    return lambda s: calc.unary(s, name)


def rad(s):
    return calc.set_angle(s, "rad")


def test_trig_in_degrees_is_clean():
    assert run(d("9"), d("0"), fn("sin")).current == "1"
    assert run(d("1"), d("8"), d("0"), fn("sin")).current == "0"
    assert run(d("6"), d("0"), fn("cos")).current == "0.5"
    assert run(d("4"), d("5"), fn("tan")).current == "1"


def test_trig_in_radians():
    assert run(rad, lambda s: calc.constant(s, "pi"), fn("cos")).current == "-1"


def test_inverse_trig_in_degrees():
    assert run(d("1"), fn("asin")).current == "90"
    assert run(d("1"), fn("atan")).current == "45"


def test_tan_90_degrees_is_error():
    assert run(d("9"), d("0"), fn("tan")).current == calc.ERROR


def test_logs_and_exp():
    assert run(d("1"), d("0"), d("0"), fn("log")).current == "2"
    assert run(d("1"), fn("exp")).current == "2.71828182846"
    assert run(d("1"), fn("ln")).current == "0"
    assert run(d("3"), fn("tenpow")).current == "1000"


def test_roots_powers_and_inverse():
    assert run(d("1"), d("4"), d("4"), fn("sqrt")).current == "12"
    assert run(d("6"), d("4"), fn("cbrt")).current == "4"
    assert run(d("1"), d("2"), fn("sq")).current == "144"
    assert run(d("3"), fn("cube")).current == "27"
    assert run(d("4"), fn("inv")).current == "0.25"
    assert run(d("5"), calc.toggle_sign, fn("abs")).current == "5"


def test_factorial():
    assert run(d("5"), fn("fact")).current == "120"
    assert run(d("0"), fn("fact")).current == "1"
    assert run(d("5"), calc.decimal, d("5"), fn("fact")).current == calc.ERROR
    assert run(d("5"), calc.toggle_sign, fn("fact")).current == calc.ERROR


def test_domain_errors():
    assert run(d("4"), calc.toggle_sign, fn("sqrt")).current == calc.ERROR
    assert run(d("0"), fn("ln")).current == calc.ERROR
    assert run(d("0"), fn("inv")).current == calc.ERROR
    assert run(d("2"), fn("asin")).current == calc.ERROR


def test_power_operator():
    assert run(d("2"), op("^"), d("1"), d("0"), calc.equals).current == "1024"
    assert run(d("2"), op("^"), d("3"), op("+"), d("1"), calc.equals).current == "9"
    assert run(d("4"), calc.toggle_sign, op("^"), d("0"), calc.decimal, d("5"), calc.equals).current == calc.ERROR
    assert run(d("9"), d("9"), d("9"), op("^"), d("9"), d("9"), d("9"), calc.equals).current == calc.ERROR


def test_constants_replace_current_value():
    pi = lambda s: calc.constant(s, "pi")
    assert run(d("7"), pi).current == "3.14159265359"
    assert run(pi, op("*"), d("2"), calc.equals).current == "6.28318530718"


def test_angle_mode_survives_clear_and_errors():
    s = run(rad, d("5"), op("/"), d("0"), calc.equals)
    assert s.current == calc.ERROR and s.angle == "rad"
    assert calc.clear(s).angle == "rad"
    assert calc.digit(s, "3").angle == "rad"


def test_history_shows_pending_operation():
    assert calc.history(run(d("6"), op("*"))) == "6 ×"
