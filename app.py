import streamlit as st

import calculator as calc

st.set_page_config(page_title="Calculator", page_icon="🧮", layout="centered")

if "state" not in st.session_state:
    st.session_state.state = calc.State()

# (label, handler) rows; the handler takes and returns a State.
ROWS = [
    [("AC", calc.clear), ("+/−", calc.toggle_sign), ("%", calc.percent), ("÷", lambda s: calc.operator(s, "/"))],
    [("7", lambda s: calc.digit(s, "7")), ("8", lambda s: calc.digit(s, "8")), ("9", lambda s: calc.digit(s, "9")), ("×", lambda s: calc.operator(s, "*"))],
    [("4", lambda s: calc.digit(s, "4")), ("5", lambda s: calc.digit(s, "5")), ("6", lambda s: calc.digit(s, "6")), ("−", lambda s: calc.operator(s, "-"))],
    [("1", lambda s: calc.digit(s, "1")), ("2", lambda s: calc.digit(s, "2")), ("3", lambda s: calc.digit(s, "3")), ("+", lambda s: calc.operator(s, "+"))],
    [("0", lambda s: calc.digit(s, "0")), (".", calc.decimal), ("⌫", calc.backspace), ("=", calc.equals)],
]


def press(handler):
    st.session_state.state = handler(st.session_state.state)


st.title("Calculator")

state = st.session_state.state
st.caption(calc.history(state) or " ")
st.markdown(f"## `{state.current}`")

for r, row in enumerate(ROWS):
    cols = st.columns(4)
    for c, (label, handler) in enumerate(row):
        cols[c].button(
            label,
            key=f"btn-{r}-{c}",
            on_click=press,
            args=(handler,),
            use_container_width=True,
        )
