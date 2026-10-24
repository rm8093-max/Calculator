# Calculator - project rules

Streamlit scientific calculator. Logic in `calculator.py` (pure, no Streamlit), UI in `app.py`.

## Standing UI rules (apply to every UI change)
- Colors come from the user's palette: dusk-blue `#485696`, alabaster-grey `#e7e7e7`, apricot-cream `#f9c784`, pumpkin-spice `#fc7a1e`, molten-orange `#f24c00` (plus a dark ink for text).
- Every text/background pair must meet WCAG AA (4.5:1). `tests/test_contrast.py` enforces this; keep it in sync with the CSS.
- Lettering is dark and bold (weight 700+) unless the fill is dark.
- All UI testing uses Playwright (`tests/ui/`), against a real running app.
- After UI testing, delete screenshots and caches (`__pycache__`, `.pytest_cache`, temp artifacts). Never commit them.
- Metabob: check `get_problems`/`path_activity` before editing, record findings, close them with `mark_complete` after pushing. Policy is also stored in concept-db as `development_policy`.
