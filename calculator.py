"""Pure calculator logic. No Streamlit imports so it can be unit-tested."""

import math
from dataclasses import dataclass, replace
from typing import Callable, Optional

SYMBOLS = {"+": "+", "-": "−", "*": "×", "/": "÷", "^": "^"}
ERROR = "Error"
NAN = float("nan")


@dataclass(frozen=True)
class State:
    current: str = "0"
    previous: Optional[str] = None
    operator: Optional[str] = None
    overwrite: bool = True
    angle: str = "deg"  # "deg" or "rad"


def _format(value: float) -> str:
    if value != value or value in (float("inf"), float("-inf")):
        return ERROR
    text = f"{value:.12g}"
    return text[:-2] if text.endswith(".0") else text


def _compute(a: float, b: float, op: str) -> float:
    try:
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            return NAN if b == 0 else a / b
        if op == "^":
            result = a**b
            return NAN if isinstance(result, complex) else result
    except (OverflowError, ValueError, ZeroDivisionError):
        return NAN
    raise ValueError(f"unknown operator: {op}")


def _reset_if_error(s: State) -> State:
    return State(angle=s.angle) if s.current == ERROR else s


def _to_radians(x: float, angle: str) -> float:
    return math.radians(x) if angle == "deg" else x


def _from_radians(x: float, angle: str) -> float:
    return math.degrees(x) if angle == "deg" else x


def _tidy(x: float) -> float:
    """Round away float noise such as sin(pi) = 1.2e-16."""
    return round(x, 12) + 0.0


def _sin(x: float, angle: str) -> float:
    return _tidy(math.sin(_to_radians(x, angle)))


def _cos(x: float, angle: str) -> float:
    return _tidy(math.cos(_to_radians(x, angle)))


def _tan(x: float, angle: str) -> float:
    if abs(math.cos(_to_radians(x, angle))) < 1e-12:
        return NAN
    return _tidy(math.tan(_to_radians(x, angle)))


def _factorial(x: float, _: str) -> float:
    if x < 0 or x != int(x) or x > 170:
        return NAN
    return float(math.factorial(int(x)))


# name -> function(x, angle). Domain/overflow errors are caught in unary().
FUNCTIONS: dict[str, Callable[[float, str], float]] = {
    "sin": _sin,
    "cos": _cos,
    "tan": _tan,
    "asin": lambda x, a: _tidy(_from_radians(math.asin(x), a)),
    "acos": lambda x, a: _tidy(_from_radians(math.acos(x), a)),
    "atan": lambda x, a: _tidy(_from_radians(math.atan(x), a)),
    "ln": lambda x, a: math.log(x),
    "log": lambda x, a: _tidy(math.log10(x)),
    "exp": lambda x, a: math.exp(x),
    "tenpow": lambda x, a: 10.0**x,
    "sqrt": lambda x, a: math.sqrt(x),
    "cbrt": lambda x, a: math.copysign(abs(x) ** (1 / 3), x) if x else 0.0,
    "sq": lambda x, a: x * x,
    "cube": lambda x, a: x**3,
    "inv": lambda x, a: NAN if x == 0 else 1 / x,
    "abs": lambda x, a: abs(x),
    "fact": _factorial,
}

CONSTANTS = {"pi": math.pi, "e": math.e}


def digit(s: State, d: str) -> State:
    s = _reset_if_error(s)
    if s.overwrite:
        return replace(s, current=d, overwrite=False)
    return replace(s, current=d if s.current == "0" else s.current + d)


def decimal(s: State) -> State:
    s = _reset_if_error(s)
    if s.overwrite:
        return replace(s, current="0.", overwrite=False)
    if "." in s.current:
        return s
    return replace(s, current=s.current + ".")


def operator(s: State, op: str) -> State:
    if s.current == ERROR:
        return s
    current = s.current
    if s.operator and not s.overwrite:
        current = _format(_compute(float(s.previous), float(s.current), s.operator))
        if current == ERROR:
            return State(current=ERROR, angle=s.angle)
    return State(current=current, previous=current, operator=op, overwrite=True, angle=s.angle)


def equals(s: State) -> State:
    if not s.operator or s.current == ERROR:
        return s
    result = _format(_compute(float(s.previous), float(s.current), s.operator))
    return State(current=result, overwrite=True, angle=s.angle)


def clear(s: State = State()) -> State:
    return State(angle=s.angle)


def unary(s: State, name: str) -> State:
    """Apply a function (sin, ln, sqrt, ...) to the number being entered."""
    if s.current == ERROR:
        return s
    try:
        value = FUNCTIONS[name](float(s.current), s.angle)
    except (OverflowError, ValueError, ZeroDivisionError):
        value = NAN
    return replace(s, current=_format(value), overwrite=True)


def constant(s: State, name: str) -> State:
    s = _reset_if_error(s)
    return replace(s, current=_format(CONSTANTS[name]), overwrite=True)


def set_angle(s: State, angle: str) -> State:
    return replace(s, angle=angle)


def toggle_sign(s: State) -> State:
    if s.current in ("0", ERROR):
        return s
    current = s.current[1:] if s.current.startswith("-") else "-" + s.current
    return replace(s, current=current)


def percent(s: State) -> State:
    if s.current == ERROR:
        return s
    return replace(s, current=_format(float(s.current) / 100), overwrite=True)


def backspace(s: State) -> State:
    if s.overwrite or s.current == ERROR:
        return s
    if len(s.current) > 1 and not (len(s.current) == 2 and s.current.startswith("-")):
        return replace(s, current=s.current[:-1])
    return replace(s, current="0", overwrite=True)


def history(s: State) -> str:
    if s.previous is not None and s.operator:
        return f"{s.previous} {SYMBOLS[s.operator]}"
    return ""
