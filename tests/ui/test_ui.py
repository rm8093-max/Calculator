"""Playwright UI tests against a real running Streamlit app.

Screenshots go to a temp dir that is deleted when the session ends. Set
UI_KEEP_SHOTS=1 to keep it (the path is printed) so you can look at them, then
delete it yourself.
"""

import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
PORT = 8599
URL = f"http://localhost:{PORT}"


def _wait_for_server(timeout=60):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{URL}/_stcore/health", timeout=2) as r:
                if r.read() == b"ok":
                    return
        except OSError:
            time.sleep(0.5)
    raise RuntimeError("Streamlit did not start")


@pytest.fixture(scope="session")
def shots():
    path = Path(tempfile.mkdtemp(prefix="calc-shots-"))
    yield path
    if os.environ.get("UI_KEEP_SHOTS") == "1":
        print(f"\nscreenshots kept in {path}")
    else:
        shutil.rmtree(path, ignore_errors=True)


@pytest.fixture(scope="session")
def server():
    with socket.socket() as s:
        if s.connect_ex(("localhost", PORT)) == 0:
            pytest.fail(f"port {PORT} already in use")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true",
         "--server.port", str(PORT), "--browser.gatherUsageStats", "false"],
        cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_server()
        yield URL
    finally:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)
        else:
            proc.terminate()


@pytest.fixture(scope="session")
def browser(server):
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture()
def page(browser, server):
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    pg.goto(server)
    expect(pg.locator(".calc-display .current")).to_have_text("0", timeout=30000)
    expect(pg.get_by_role("button", name="=", exact=True)).to_be_visible(timeout=30000)  # keypad fully drawn
    yield pg
    pg.close()


def key(page, label):
    return page.get_by_role("button", name=label, exact=True)


def press(page, *labels):
    for label in labels:
        key(page, label).click()
        page.wait_for_timeout(150)  # let Streamlit rerun before the next click


def shown(page):
    return page.locator(".calc-display .current")


def test_basic_addition(page):
    press(page, "2", "+", "3", "=")
    expect(shown(page)).to_have_text("5")


def test_scientific_functions(page):
    press(page, "9", "0", "sin")
    expect(shown(page)).to_have_text("1")
    press(page, "AC", "2", "xʸ", "1", "0", "=")
    expect(shown(page)).to_have_text("1024")
    press(page, "AC", "5", "x!")
    expect(shown(page)).to_have_text("120")
    press(page, "AC", "1", "4", "4", "√x")
    expect(shown(page)).to_have_text("12")


def test_radian_mode(page):
    page.locator("label", has_text="RAD").click()
    page.wait_for_timeout(300)
    press(page, "π", "cos")
    expect(shown(page)).to_have_text("-1")


def test_division_by_zero_shows_error(page):
    press(page, "5", "÷", "0", "=")
    expect(shown(page)).to_have_text("Error")


def _rgb(text):
    nums = [float(n) for n in re.findall(r"[\d.]+", text)[:3]]
    return nums


def _lum(rgb):
    lin = [(c / 255) / 12.92 if c / 255 <= 0.03928 else (((c / 255) + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def _contrast(a, b):
    hi, lo = sorted((_lum(a), _lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def test_rendered_text_contrast_and_weight(page):
    """Measure what the browser actually renders, not what the CSS says."""
    results = page.evaluate(
        """() => {
          const out = [];
          const effectiveBg = (el) => {
            for (; el; el = el.parentElement) {
              const c = getComputedStyle(el).backgroundColor;
              if (c !== 'rgba(0, 0, 0, 0)' && c !== 'transparent') return c;
            }
            return 'rgb(255, 255, 255)';
          };
          for (const b of document.querySelectorAll('button')) {
            if (!b.innerText.trim()) continue;  // icon-only chrome has no lettering
            const t = b.querySelector('p') || b;
            out.push({name: b.innerText.trim(), bg: effectiveBg(b),
                      fg: getComputedStyle(t).color, weight: getComputedStyle(t).fontWeight});
          }
          const d = document.querySelector('.calc-display');
          for (const el of d.querySelectorAll('.current, .meta span')) {
            out.push({name: 'display:' + el.className, bg: getComputedStyle(d).backgroundColor,
                      fg: getComputedStyle(el).color, weight: getComputedStyle(el).fontWeight});
          }
          return out;
        }"""
    )
    assert len(results) >= 40
    failures = []
    for r in results:
        ratio = _contrast(_rgb(r["fg"]), _rgb(r["bg"]))
        if ratio < 4.5:
            failures.append(f'{r["name"]!r}: {ratio:.2f}:1 ({r["fg"]} on {r["bg"]})')
        if int(r["weight"]) < 700:
            failures.append(f'{r["name"]!r}: font-weight {r["weight"]} < 700')
    assert not failures, "\n".join(failures)


@pytest.mark.parametrize("label", ["=", "sin", "7", "÷", "AC"])
def test_contrast_holds_while_hovered_and_focused(page, label):
    """Streamlit restyles a button after a click; the text must stay readable then."""
    press(page, label)  # leaves the pointer over the button and focuses it
    page.wait_for_timeout(300)
    r = page.evaluate(
        """(label) => {
          const b = [...document.querySelectorAll('button')].find(x => x.innerText.trim() === label);
          const t = b.querySelector('p') || b;
          const bg = getComputedStyle(b).backgroundColor;
          const inner = getComputedStyle(t).backgroundColor;
          return {bg, inner, fg: getComputedStyle(t).color, hovered: b.matches(':hover')};
        }""",
        label,
    )
    assert r["hovered"]
    assert r["inner"] in ("rgba(0, 0, 0, 0)", r["bg"]), f"inner box paints over the button: {r}"
    assert _contrast(_rgb(r["fg"]), _rgb(r["bg"])) >= 4.5, r


def test_screenshots(page, shots):
    press(page, "2", "xʸ", "8", "=")
    page.screenshot(path=str(shots / "desktop.png"), full_page=True)
    page.set_viewport_size({"width": 820, "height": 900})
    page.screenshot(path=str(shots / "narrow.png"), full_page=True)
    assert (shots / "desktop.png").exists()
