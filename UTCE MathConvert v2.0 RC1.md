# UTCE MathConvert v2.0 RC1

Release Date
2026-06-28

Status
Release Candidate

## Overview

UTCE MathConvert v2.0 RC1 is the first release candidate of the True OMML conversion engine.

The project converts simplified mathematical expressions into:

- LaTeX
- MathML
- Microsoft Word OMML

using a recursive parsing engine.

---

## New Features

- Recursive nested parser
- Matrix support
- Fraction support
- Square root support
- Power support
- Summation
- Product
- Integral
- Limit
- Structural diagnostics
- Confidence estimation
- Predictive risk estimation

---

## Project Reorganization

- archive/
- docs/
- output/
- tests/

Legacy backup files were moved into archive/backups.

---

## Tested

Successfully verified:

- Simple expressions
- Nested expressions
- Deep recursive expressions
- Matrix expressions
- Composite expressions

---

## Remaining Work

- cases environment
- Greek symbols
- Advanced OMML layout optimization
- UI refinement

---

## Status

Ready for broader testing before the official v2.0 release.