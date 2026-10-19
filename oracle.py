#!/usr/bin/env python3
# Temperature Math oracle - mirrors engine.js using Fraction instead of hand-rolled big integer fractions.
import json, re
from fractions import Fraction

UNITS = ["C", "F", "K"]

def _unit(u):
    if u not in UNITS:
        raise ValueError("unit must be one of C, F, K")
    return u

def _val(text):
    t = text.strip() if isinstance(text, str) else ""
    m = re.fullmatch(r"(-?)([0-9]+)(?:\.([0-9]{1,2}))?", t)
    err = "temperature must be a number with at most 2 decimals, between -1000000 and 1000000"
    if not m:
        raise ValueError(err)
    h = int(m.group(2)) * 100 + int((m.group(3) or "").ljust(2, "0"))
    if h > 100000000:
        raise ValueError(err)
    return t, (-h if m.group(1) else h)

def to_k(u, h):
    h = Fraction(h)
    if u == "C": return h + 27315
    if u == "F": return (h + 45967) * Fraction(5, 9)
    return h

def from_k(u, k):
    if u == "C": return k - 27315
    if u == "F": return k * Fraction(9, 5) - 45967
    return k

def fmt(f):
    neg = f < 0
    a = abs(f)
    s = int((2 * a + 1) // 2)  # half away from zero on the magnitude
    whole, frac = divmod(s, 100)
    fr = f"{frac:02d}".rstrip("0")
    body = str(whole) + ("." + fr if fr else "")
    return ("-" if neg and s != 0 else "") + body

def mark(f):
    return ("exactly " if f.denominator == 1 else "about ") + fmt(f)

def note(parts):
    return " Figures marked about are rounded to 2 decimal places." if any(p.startswith("about ") for p in parts) else ""

def convert_truth(value, unit):
    t, h = _val(value); u = _unit(unit)
    k = to_k(u, h)
    if k < 0:
        raise ValueError("that temperature is below absolute zero (0 K, -273.15 C, -459.67 F)")
    parts = [mark(from_k(x, k)) + " " + x for x in UNITS if x != u]
    return f"{t} {u} is {' and '.join(parts)}." + note(parts)

def change_truth(value, unit):
    t, h = _val(value); u = _unit(unit)
    c = Fraction(h) * Fraction(5, 9) if u == "F" else Fraction(h)
    parts = []
    for x in UNITS:
        if x == u: continue
        o = c * Fraction(9, 5) if x == "F" else c
        parts.append(mark(o) + " " + x)
    return f"A change of {t} {u} is a change of {' and '.join(parts)}." + note(parts)

def same_truth(a, b):
    _unit(a); _unit(b)
    if a == b:
        raise ValueError("pick two different scales")
    # Brute force the fixed point by solving the two affine maps with Fractions.
    def f(u, x):  # u-reading x (hundredths) -> reading in b
        return from_k(b, to_k(u, x))
    f0 = f(a, Fraction(0)); f1 = f(a, Fraction(100))
    slope = (f1 - f0) / 100
    if slope == 1:
        return f"{a} and {b} never read the same number: they always differ by a fixed amount."
    x = f0 / (1 - slope)  # x = slope*x + f0
    assert f(a, x) == x
    return f"{a} and {b} read the same number at {mark(x)}."

FNS = {"convertTruth": convert_truth, "changeTruth": change_truth, "sameTruth": same_truth}
CASES = [
    ("convertTruth", ["20", "C"]), ("convertTruth", ["0", "C"]), ("convertTruth", ["-40", "C"]), ("convertTruth", ["100", "C"]),
    ("convertTruth", ["37", "C"]), ("convertTruth", ["98.6", "F"]), ("convertTruth", ["32", "F"]), ("convertTruth", ["-459.67", "F"]),
    ("convertTruth", ["0", "K"]), ("convertTruth", ["273.15", "K"]), ("convertTruth", ["300", "K"]), ("convertTruth", ["1000000", "C"]),
    ("convertTruth", ["1000000", "F"]), ("convertTruth", ["0.01", "F"]), ("convertTruth", ["-17.78", "C"]), ("convertTruth", ["-273.15", "C"]),
    ("convertTruth", [" 5 ", "C"]), ("convertTruth", ["-0", "C"]), ("convertTruth", ["72", "F"]), ("convertTruth", ["350", "F"]),
    ("convertTruth", ["-459.68", "F"]), ("convertTruth", ["-273.16", "C"]), ("convertTruth", ["-0.01", "K"]), ("convertTruth", ["-1000000", "C"]),
    ("convertTruth", ["1000000.01", "C"]), ("convertTruth", ["abc", "C"]), ("convertTruth", ["1.234", "C"]), ("convertTruth", ["", "C"]),
    ("convertTruth", ["5", "X"]), ("convertTruth", ["1e3", "C"]), ("convertTruth", [".5", "C"]), ("convertTruth", ["5.", "C"]),
    ("changeTruth", ["10", "C"]), ("changeTruth", ["18", "F"]), ("changeTruth", ["1", "K"]), ("changeTruth", ["-5", "C"]),
    ("changeTruth", ["0.01", "F"]), ("changeTruth", ["1000000", "F"]), ("changeTruth", ["-1000000", "C"]), ("changeTruth", ["1.5", "F"]),
    ("changeTruth", ["0", "C"]), ("changeTruth", ["abc", "C"]), ("changeTruth", ["5", "R"]), ("changeTruth", ["1000001", "C"]),
    ("sameTruth", ["C", "F"]), ("sameTruth", ["F", "C"]), ("sameTruth", ["C", "K"]), ("sameTruth", ["K", "C"]),
    ("sameTruth", ["F", "K"]), ("sameTruth", ["K", "F"]), ("sameTruth", ["C", "C"]), ("sameTruth", ["F", "F"]),
    ("sameTruth", ["X", "C"]), ("sameTruth", ["C", "Y"]),
]

out = []
for fn, args in CASES:
    try:
        exp = FNS[fn](*args)
    except ValueError as e:
        exp = "ERR:" + str(e)
    out.append({"fn": fn, "args": args, "expected": exp})
with open("expected.json", "w") as f:
    json.dump(out, f, indent=1)
    f.write("\n")
print(len(out), "cases")
