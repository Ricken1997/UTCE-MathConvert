# UTCE MathConvert Free Beta 1.0

UTCE MathConvert is a plain-math to LaTeX / MathML / Word OMML converter.

## Main Features

- Greek symbols
- Fractions
- Square roots
- Superscripts
- Subscripts
- Summation
- Product
- Integral
- Derivative
- Limit
- Matrix
- Cases
- Basic operators (+ − × ÷)
- Native Word equation (.docx) export

## Recommended Use

- Reports
- Undergraduate theses
- Graduate reports
- Office documents
- Academic drafts

## Known Limitations

- Nested expressions are partially supported.
- Very complex formulas may not render correctly.
- Operator precedence is still under development.
- Beta version: please verify output before important use.

## Outputs

- LaTeX
- MathML
- True OMML
- Word .docx with native equations

## Version

Free Beta 1.0

Future:

- v1.1 Recursive nesting
- v2.0 Full parser engine



# UTCE-MathConvert

Plain Math → Word OMML Converter

---

## Application Icon

![Application Icon](images/main.png)

---

## Main Window

![Main Window](images/main_window.png)

---

## Word Output

![Word Output](images/word_output.png)

---

## Complex Formula Example

![Complex Formula](images/complex_formula.png)

---

## Features

- Greek symbols
- Fractions
- Square roots
- Superscripts
- Subscripts
- Summation
- Product
- Integral
- Limits
- Matrix
- Cases
- Derivatives
- + − × ÷ operators
- Native Word OMML output

---

## Outputs

- LaTeX
- MathML
- Word OMML
- .docx with native equations

---

## Platform

macOS (Apple Silicon)

---

## Author

Yuichi Fujiki

---

## License

MIT License


# UTCE MathConvert

UTCE MathConvert is a lightweight mathematical expression converter for transforming plain math-like syntax into LaTeX, MathML, and Word OMML.

## Current Version

v2.0 RC

## Core Features

- Plain text math input
- LaTeX output
- MathML output
- Word OMML output
- Recursive nested expression support
- Matrix support
- Structural diagnostic summary
- Confidence / predictive risk display

## Supported Functions

```text
frac(a,b)
sqrt(a)
pow(a,b)
sum(i,1,n,a)
prod(i,1,n,a)
int(x,0,1,a)
lim(t,0,a)
matrix(a,b;c,d)

app.py
omml_converter.py
utce_core.py
utce_core_refactor_work.py
docs/
tests/
output/
archive/backups/

Release Notes はこれ。

```md
# Release Notes v2.0 RC

Date: 2026-06-28

## Summary

This release stabilizes the UTCE MathConvert v2.0 RC core.

## Major Changes

- Reorganized project folder structure.
- Archived legacy backup files.
- Added recursive conversion support.
- Stabilized LaTeX, MathML, and OMML generation.
- Improved diagnostic output.
- Removed obsolete Beta 1.0 warning logic.

## Confirmed Working

- frac
- sqrt
- pow
- sum
- prod
- int
- lim
- matrix
- nested composite expressions

## Known Remaining Work

- cases support
- align support
- advanced Word OMML layout refinement
- Greek symbol expansion
- UI polish