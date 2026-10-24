"""Pure calculator logic. No Streamlit imports so it can be unit-tested."""

from dataclasses import dataclass, replace
from typing import Optional

SYMBOLS = {"+": "+", "-": "−", "*": "×", "/": "÷"}
ERROR = "Error"


@dataclass(frozen=True)
class State:
    current: str = "0"
    previous: Optional[str] = None
    operator: Optional[str] = None
    overwrite: bool = True


def _format(value: float) -> str:
    if value != value or value in (float("inf"), float("-inf")):
        return ERROR
    text = f"{value:.12g}"
    return text[:-2] if text.endswith(".0") else text


def _compute(a: float, b: float, op: str) -> float:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return float("nan") if b == 0 else a / b
    raise ValueError(f"unknown operator: {op}")


def _reset_if_error(s: State) -> State:
    return State() if s.current == ERROR else s


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
            return State(current=ERROR)
    return State(current=current, previous=current, operator=op, overwrite=True)


def equals(s: State) -> State:
    if not s.operator or s.current == ERROR:
        return s
    result = _format(_compute(float(s.previous), float(s.current), s.operator))
    return State(current=result, overwrite=True)


def clear(_: State = State()) -> State:
    return State()


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
