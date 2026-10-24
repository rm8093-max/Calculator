from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def click(at, label):
    next(b for b in at.button if b.label == label).click()
    at.run()


def display(at):
    return next(m.value for m in at.markdown if 'class="current"' in m.value)


def test_app_adds_two_numbers():
    at = AppTest.from_file(APP).run()
    assert not at.exception
    for label in ("2", "+", "3", "="):
        click(at, label)
    assert '<div class="current">5</div>' in display(at)


def test_sin_90_degrees_is_one():
    at = AppTest.from_file(APP).run()
    for label in ("9", "0", "sin"):
        click(at, label)
    assert '<div class="current">1</div>' in display(at)
