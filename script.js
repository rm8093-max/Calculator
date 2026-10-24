const currentEl = document.getElementById("current");
const historyEl = document.getElementById("history");
const SYMBOLS = { "+": "+", "-": "−", "*": "×", "/": "÷" };

let current = "0";
let previous = null;
let operator = null;
let overwrite = true;

function compute(a, b, op) {
  switch (op) {
    case "+": return a + b;
    case "-": return a - b;
    case "*": return a * b;
    case "/": return b === 0 ? NaN : a / b;
  }
}

function format(value) {
  if (!Number.isFinite(value)) return "Error";
  return String(parseFloat(value.toPrecision(12)));
}

function render() {
  currentEl.textContent = current;
  historyEl.textContent =
    previous !== null && operator ? `${previous} ${SYMBOLS[operator]}` : "";
  document.querySelectorAll("button.op[data-op]").forEach((btn) => {
    btn.classList.toggle("active", btn.dataset.op === operator && overwrite);
  });
}

function inputDigit(d) {
  if (current === "Error") clearAll();
  if (overwrite) {
    current = d;
    overwrite = false;
  } else {
    current = current === "0" ? d : current + d;
  }
}

function inputDecimal() {
  if (current === "Error") clearAll();
  if (overwrite) {
    current = "0.";
    overwrite = false;
  } else if (!current.includes(".")) {
    current += ".";
  }
}

function chooseOperator(op) {
  if (current === "Error") return;
  if (operator && !overwrite) {
    current = format(compute(Number(previous), Number(current), operator));
  }
  previous = current;
  operator = op;
  overwrite = true;
}

function equals() {
  if (!operator || current === "Error") return;
  current = format(compute(Number(previous), Number(current), operator));
  previous = null;
  operator = null;
  overwrite = true;
}

function clearAll() {
  current = "0";
  previous = null;
  operator = null;
  overwrite = true;
}

function toggleSign() {
  if (current === "Error" || current === "0") return;
  current = current.startsWith("-") ? current.slice(1) : "-" + current;
}

function percent() {
  if (current === "Error") return;
  current = format(Number(current) / 100);
  overwrite = true;
}

document.querySelector(".keys").addEventListener("click", (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const { digit, op, action } = btn.dataset;
  if (digit !== undefined) inputDigit(digit);
  else if (op) chooseOperator(op);
  else if (action === "decimal") inputDecimal();
  else if (action === "equals") equals();
  else if (action === "clear") clearAll();
  else if (action === "sign") toggleSign();
  else if (action === "percent") percent();
  render();
});

document.addEventListener("keydown", (e) => {
  if (e.ctrlKey || e.metaKey || e.altKey) return;
  if (/^[0-9]$/.test(e.key)) inputDigit(e.key);
  else if (e.key === ".") inputDecimal();
  else if ("+-*/".includes(e.key)) chooseOperator(e.key);
  else if (e.key === "Enter" || e.key === "=") { e.preventDefault(); equals(); }
  else if (e.key === "Escape") clearAll();
  else if (e.key === "Backspace") {
    if (!overwrite && current.length > 1) current = current.slice(0, -1);
    else if (!overwrite) { current = "0"; overwrite = true; }
  } else return;
  render();
});

render();
