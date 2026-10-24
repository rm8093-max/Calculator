import streamlit as st

import calculator as calc
from app_theme import css_variables

st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="wide")

if "state" not in st.session_state:
    st.session_state.state = calc.State()


def digit(n):
    return lambda s: calc.digit(s, n)


def op(o):
    return lambda s: calc.operator(s, o)


def fn(name):
    return lambda s: calc.unary(s, name)


def const(name):
    return lambda s: calc.constant(s, name)


# (label, kind, handler). Each row is 4 scientific keys then 4 basic keys.
ROWS = [
    [("π", "sci", const("pi")), ("e", "sci", const("e")), ("x!", "sci", fn("fact")), ("1/x", "sci", fn("inv")),
     ("AC", "fn", calc.clear), ("⌫", "fn", calc.backspace), ("%", "fn", calc.percent), ("÷", "op", op("/"))],
    [("sin", "sci", fn("sin")), ("cos", "sci", fn("cos")), ("tan", "sci", fn("tan")), ("√x", "sci", fn("sqrt")),
     ("7", "num", digit("7")), ("8", "num", digit("8")), ("9", "num", digit("9")), ("×", "op", op("*"))],
    [("sin⁻¹", "sci", fn("asin")), ("cos⁻¹", "sci", fn("acos")), ("tan⁻¹", "sci", fn("atan")), ("x²", "sci", fn("sq")),
     ("4", "num", digit("4")), ("5", "num", digit("5")), ("6", "num", digit("6")), ("−", "op", op("-"))],
    [("ln", "sci", fn("ln")), ("log", "sci", fn("log")), ("eˣ", "sci", fn("exp")), ("10ˣ", "sci", fn("tenpow")),
     ("1", "num", digit("1")), ("2", "num", digit("2")), ("3", "num", digit("3")), ("+", "op", op("+"))],
    [("xʸ", "sci", op("^")), ("x³", "sci", fn("cube")), ("∛x", "sci", fn("cbrt")), ("|x|", "sci", fn("abs")),
     ("+/−", "fn", calc.toggle_sign), ("0", "num", digit("0")), (".", "num", calc.decimal), ("=", "eq", calc.equals)],
]

STYLE = f"""
<style>
:root {{
{css_variables()}
}}
h1, h2, h3, label, p, span {{ color: var(--ink); font-weight: 700; }}
.calc-display {{
  background: var(--dusk-blue);
  color: var(--white);
  border-radius: 16px;
  padding: 12px 20px;
  text-align: right;
  margin-bottom: 12px;
}}
.calc-display .meta {{
  display: flex;
  justify-content: space-between;
  min-height: 1.5rem;
  color: var(--white);
  font-weight: 700;
}}
.calc-display .current {{
  font-size: 2.8rem;
  font-weight: 800;
  color: var(--white);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}
.calc-display, .calc-display * {{ color: var(--white); }}
[class*="st-key-num-"] button, [class*="st-key-sci-"] button,
[class*="st-key-fn-"] button, [class*="st-key-op-"] button,
[class*="st-key-eq-"] button {{
  height: 3.4rem;
  border: 2px solid var(--ink);
  border-radius: 14px;
}}
[class*="st-key-"] button {{ padding: 0 2px; }}
[class*="st-key-"] button, [class*="st-key-"] button * {{
  font-size: clamp(0.85rem, 1.7vw, 1.25rem) !important;
  font-weight: 800 !important;
  white-space: nowrap;
  overflow: visible !important;
  text-overflow: clip !important;
}}
/* Streamlit restyles hover/focus/active, so every state is pinned to the same colors. */
[class*="st-key-"] button *, [class*="st-key-"] button *:hover {{ background: transparent !important; }}
[class*="st-key-num-"] button, [class*="st-key-num-"] button:hover, [class*="st-key-num-"] button:focus, [class*="st-key-num-"] button:active,
[class*="st-key-num-"] button * {{ background-color: var(--alabaster-grey) !important; color: var(--ink) !important; }}
[class*="st-key-sci-"] button, [class*="st-key-sci-"] button:hover, [class*="st-key-sci-"] button:focus, [class*="st-key-sci-"] button:active,
[class*="st-key-sci-"] button * {{ background-color: var(--dusk-blue) !important; color: var(--white) !important; }}
[class*="st-key-fn-"] button, [class*="st-key-fn-"] button:hover, [class*="st-key-fn-"] button:focus, [class*="st-key-fn-"] button:active,
[class*="st-key-fn-"] button * {{ background-color: var(--apricot-cream) !important; color: var(--ink) !important; }}
[class*="st-key-op-"] button, [class*="st-key-op-"] button:hover, [class*="st-key-op-"] button:focus, [class*="st-key-op-"] button:active,
[class*="st-key-op-"] button * {{ background-color: var(--pumpkin-spice) !important; color: var(--ink) !important; }}
[class*="st-key-eq-"] button, [class*="st-key-eq-"] button:hover, [class*="st-key-eq-"] button:focus, [class*="st-key-eq-"] button:active,
[class*="st-key-eq-"] button * {{ background-color: var(--molten-orange) !important; color: var(--ink) !important; }}
[class*="st-key-"] button:hover {{ filter: brightness(1.1); border-color: var(--ink) !important; }}
[class*="st-key-"] button:active {{ filter: brightness(0.9); }}
[class*="st-key-"] button:focus-visible {{ outline: 3px solid var(--ink); outline-offset: 2px; }}
</style>
"""


def press(handler):
    state = st.session_state.state
    state = calc.set_angle(state, st.session_state.angle_mode.lower())
    st.session_state.state = handler(state)


st.markdown(STYLE, unsafe_allow_html=True)
_, middle, _ = st.columns([1, 6, 1])
with middle:
    st.markdown("### Scientific Calculator")
    st.radio("Angle", ["DEG", "RAD"], horizontal=True, key="angle_mode")
    state = st.session_state.state
    st.markdown(
        f'<div class="calc-display"><div class="meta"><span>{st.session_state.angle_mode}</span>'
        f'<span class="history">{calc.history(state) or "&nbsp;"}</span></div>'
        f'<div class="current">{state.current}</div></div>',
        unsafe_allow_html=True,
    )
    for r, row in enumerate(ROWS):
        cols = st.columns(8)
        for c, (label, kind, handler) in enumerate(row):
            cols[c].button(
                label,
                key=f"{kind}-{r}-{c}",
                on_click=press,
                args=(handler,),
                use_container_width=True,
            )
