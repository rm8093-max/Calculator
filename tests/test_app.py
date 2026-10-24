from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def click(at, label):
    next(b for b in at.button if b.label == label).click()
    at.run()


def test_app_adds_two_numbers():
    at = AppTest.from_file(APP).run()
    assert not at.exception
    for label in ("2", "+", "3", "="):
        click(at, label)
    assert '<div class="current">5</div>' in at.markdown[1].value
