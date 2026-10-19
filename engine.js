// Temperature Math engine - converts a reading, converts a change, and finds where two scales agree.
// Mirrored by oracle.py; keep the op order identical.
// Values are typed with up to 2 decimals, from -1000000 to 1000000. Arithmetic is exact (big integer fractions).
// Definitions: K = C + 273.15 and F = C * 9/5 + 32. Figures are rounded to 2 decimals, half away from zero.

var UNITS = ["C", "F", "K"];

function _unit(u) {
  if (UNITS.indexOf(u) < 0) throw new Error("unit must be one of C, F, K");
  return u;
}

// A typed value as hundredths of its unit.
function _val(text) {
  var t = typeof text === "string" ? text.trim() : "";
  var m = /^(-?)([0-9]+)(?:\.([0-9]{1,2}))?$/.exec(t);
  var err = "temperature must be a number with at most 2 decimals, between -1000000 and 1000000";
  if (!m) throw new Error(err);
  var h = BigInt(m[2]) * 100n + BigInt((m[3] || "") + "00".slice((m[3] || "").length));
  if (h > 100000000n) throw new Error(err);
  return { text: t, h: m[1] ? -h : h };
}

// Fractions are {n, d} with d > 0, counting hundredths of the unit.
function _toK(u, h) {
  if (u === "C") return { n: h + 27315n, d: 1n };
  if (u === "F") return { n: (h + 45967n) * 5n, d: 9n };
  return { n: h, d: 1n };
}
function _fromK(u, k) {
  if (u === "C") return { n: k.n - 27315n * k.d, d: k.d };
  if (u === "F") return { n: k.n * 9n - 45967n * 5n * k.d, d: 5n * k.d };
  return { n: k.n, d: k.d };
}

// A fraction of hundredths as text rounded to 2 decimals, half away from zero.
function _fmt(f) {
  var neg = f.n < 0n;
  var a = neg ? -f.n : f.n;
  var s = (2n * a + f.d) / (2n * f.d);
  var frac = String(s % 100n);
  while (frac.length < 2) frac = "0" + frac;
  while (frac.length > 0 && frac.charAt(frac.length - 1) === "0") frac = frac.slice(0, -1);
  var body = (s / 100n) + (frac ? "." + frac : "");
  return (neg && s !== 0n ? "-" : "") + body;
}
function _mark(f) { return (f.n % f.d === 0n ? "exactly " : "about ") + _fmt(f); }
function _roundNote(parts) {
  for (var i = 0; i < parts.length; i++) if (parts[i].indexOf("about ") === 0) return " Figures marked about are rounded to 2 decimal places.";
  return "";
}

// The convert truth: a reading in one scale, as the other two.
function convertTruth(value, unit) {
  var v = _val(value), u = _unit(unit);
  var k = _toK(u, v.h);
  if (k.n < 0n) throw new Error("that temperature is below absolute zero (0 K, -273.15 C, -459.67 F)");
  var parts = [];
  for (var i = 0; i < UNITS.length; i++) {
    if (UNITS[i] === u) continue;
    parts.push(_mark(_fromK(UNITS[i], k)) + " " + UNITS[i]);
  }
  return v.text + " " + u + " is " + parts.join(" and ") + "." + _roundNote(parts);
}

// The change truth: a temperature difference in one scale, as the other two.
function changeTruth(value, unit) {
  var v = _val(value), u = _unit(unit);
  var c = u === "F" ? { n: v.h * 5n, d: 9n } : { n: v.h, d: 1n };
  var parts = [];
  for (var i = 0; i < UNITS.length; i++) {
    if (UNITS[i] === u) continue;
    var o = UNITS[i] === "F" ? { n: c.n * 9n, d: c.d * 5n } : c;
    parts.push(_mark(o) + " " + UNITS[i]);
  }
  return "A change of " + v.text + " " + u + " is a change of " + parts.join(" and ") + "." + _roundNote(parts);
}

// The same truth: where two scales read the same number.
var _P = { C: [1n, 1n], F: [5n, 9n], K: [1n, 1n] };
var _Q = { C: [27315n, 100n], F: [229835n, 900n], K: [0n, 1n] };
function sameTruth(a, b) {
  _unit(a); _unit(b);
  if (a === b) throw new Error("pick two different scales");
  var pa = _P[a], pb = _P[b], qa = _Q[a], qb = _Q[b];
  var dn = pb[0] * pa[1] - pa[0] * pb[1], dd = pa[1] * pb[1];
  if (dn === 0n) return a + " and " + b + " never read the same number: they always differ by a fixed amount.";
  var nn = qa[0] * qb[1] - qb[0] * qa[1], nd = qa[1] * qb[1];
  var n = nn * dd, d = nd * dn;
  if (d < 0n) { n = -n; d = -d; }
  return a + " and " + b + " read the same number at " + _mark({ n: n * 100n, d: d }) + ".";
}
