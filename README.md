# Temperature Math

Temperature scale conversion arithmetic. 10 C is 50 F, yet a change of 10 C is a change of 18 F.

## What it computes

- **The convert truth** - a reading in C, F or K, as the other two scales, marked "exactly" or "about".
- **The change truth** - a temperature change (a difference) in one scale, as the other two. A change of 10 C is 18 F, not 50 F.
- **The same truth** - where two scales read the same number (C and F at -40, F and K at about 574.59, C and K never).

Values are typed with up to 2 decimals, from -1000000 to 1000000. Readings below absolute zero are refused. Arithmetic is exact with big-integer fractions, using K = C + 273.15 and F = C * 9/5 + 32. Figures are rounded to 2 decimal places, half away from zero.

## Boundary

Arithmetic only. Temperature Math does not know what a temperature means for people, food, equipment or materials. Check those against the source that applies.

## Files

- `index.html` - landing page.
- `app.html` - the interactive calculator.
- `engine.js` - the arithmetic.
- `oracle.py` - the Python mirror (Fractions) that generates `expected.json`.
- `test.js` - compares every engine output against `expected.json` (54 cases).
- `expected.json` - the golden answers.

## Test

```
python3 oracle.py
node test.js
```

Live: https://ilanis-agent.github.io/tempmath/
Repo: https://github.com/iLanis-agent/tempmath
