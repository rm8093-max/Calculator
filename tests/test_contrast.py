"""WCAG AA contrast check for every text/background pair the UI uses.

PAIRS mirrors the CSS in app.py. If you change a color there, change it here.
"""

import pytest

from app_theme import COLORS, PAIRS


def _luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    channels = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


@pytest.mark.parametrize("name,fg,bg", PAIRS)
def test_text_meets_wcag_aa(name, fg, bg):
    ratio = contrast(COLORS[fg], COLORS[bg])
    assert ratio >= 4.5, f"{name}: {fg} on {bg} is {ratio:.2f}:1 (needs 4.5:1)"


def test_only_palette_colors_plus_ink_and_white():
    allowed = {"dusk-blue", "alabaster-grey", "apricot-cream", "pumpkin-spice", "molten-orange", "ink", "white"}
    assert set(COLORS) == allowed
