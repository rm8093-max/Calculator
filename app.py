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


STYLE = """
<style>
:root {
  --dusk-blue: #485696;
  --alabaster-grey: #e7e7e7;
  --apricot-cream: #f9c784;
  --pumpkin-spice: #fc7a1e;
  --molten-orange: #f24c00;
  --ink: #1d2240;
}
.calc-display {
  background: var(--dusk-blue);
  color: var(--alabaster-grey);
  border-radius: 16px;
  padding: 12px 20px;
  text-align: right;
  margin-bottom: 12px;
}
.calc-display .history { min-height: 1.4rem; color: var(--apricot-cream); }
.calc-display .current {
  font-size: 2.6rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
[class*="st-key-num-"] button,
[class*="st-key-fn-"] button,
[class*="st-key-op-"] button,
[class*="st-key-eq-"] button {
  height: 3.6rem;
  font-size: 1.4rem;
  font-weight: 600;
  border: 0;
  border-radius: 14px;
}
[class*="st-key-num-"] button { background: var(--dusk-blue); color: var(--alabaster-grey); }
[class*="st-key-fn-"] button { background: var(--apricot-cream); color: var(--ink); }
[class*="st-key-op-"] button { background: var(--pumpkin-spice); color: var(--ink); }
[class*="st-key-eq-"] button { background: var(--molten-orange); color: var(--ink); }
[class*="st-key-"] button:hover { filter: brightness(1.12); }
[class*="st-key-"] button:active { filter: brightness(0.9); }
</style>
"""

OPERATORS = set("÷×−+")


def kind(label):
    if label == "=":
        return "eq"
    if label in OPERATORS:
        return "op"
    if label.isdigit() or label == ".":
        return "num"
    return "fn"


def press(handler):
    st.session_state.state = handler(st.session_state.state)


st.markdown(STYLE, unsafe_allow_html=True)

state = st.session_state.state
st.markdown(
    f'<div class="calc-display"><div class="history">{calc.history(state) or "&nbsp;"}</div>'
    f'<div class="current">{state.current}</div></div>',
    unsafe_allow_html=True,
)

for r, row in enumerate(ROWS):
    cols = st.columns(4)
    for c, (label, handler) in enumerate(row):
        cols[c].button(
            label,
            key=f"{kind(label)}-{r}-{c}",
            on_click=press,
            args=(handler,),
            use_container_width=True,
        )
