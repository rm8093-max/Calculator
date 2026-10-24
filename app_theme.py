"""Theme tokens shared by the app CSS and the contrast test."""

COLORS = {
    "dusk-blue": "#485696",
    "alabaster-grey": "#e7e7e7",
    "apricot-cream": "#f9c784",
    "pumpkin-spice": "#fc7a1e",
    "molten-orange": "#f24c00",
    "ink": "#0b0e1f",  # near-black navy for dark, bold lettering
    "white": "#ffffff",
}

# (where, text color, background color) for every text the UI draws.
PAIRS = [
    ("page text", "ink", "alabaster-grey"),
    ("display", "white", "dusk-blue"),
    ("display history", "white", "dusk-blue"),
    ("digit keys", "ink", "alabaster-grey"),
    ("scientific keys", "white", "dusk-blue"),
    ("function keys", "ink", "apricot-cream"),
    ("operator keys", "ink", "pumpkin-spice"),
    ("equals key", "ink", "molten-orange"),
]


def css_variables() -> str:
    return "\n".join(f"  --{name}: {value};" for name, value in COLORS.items())
