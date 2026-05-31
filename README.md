# UTCE MathConvert

UTCE MathConvert is an experimental plain-math-to-LaTeX conversion engine.

## Current Version

v1.0-beta

## Supported Syntax

- frac(a,b) → \frac{a}{b}
- sqrt(x) → \sqrt{x}
- sum(i,1,n,x^i) → \sum_{i=1}^{n} x^{i}
- int(0,1,x^2,x) → \int_{0}^{1} x^{2} \, dx
- lim(x,0,sin(x)/x) → \lim_{x \to 0} sin(x)/x
- partial(f,x) → \frac{\partial f}{\partial x}
- abs(x) → \left|x\right|
- norm(v) → \left\|v\right\|
- sin(x), cos(x), tan(x)
- log(x), ln(x), exp(x)
- Greek letters: alpha, beta, gamma, delta, theta, lambda, sigma, omega
- pi
- exponent notation: x^2 → x^{2}

## Usage

Edit `test_input.txt`, then run:

```bash
python3 utce_core.py

## Clipboard Copy

Use `--copy` to copy the converted LaTeX directly to the macOS clipboard.

```bash
python3 utce_core.py test_input.txt output_latex.txt --inline --copy
python3 utce_core.py test_input.txt output_block.txt --block --copy
python3 utce_core.py test_input.txt output_raw.txt --raw --copy

## Validation Warnings

UTCE MathConvert checks basic function argument counts and prints warnings when the input appears incomplete.

Examples:

```text
frac(1)
sum(1,2)
int(0,1,x)
lim(x,0)
matrix(a,b,c)

Warning: frac requires 2 arguments, got 1
Warning: sum requires 4 arguments, got 2
Warning: int requires 4 arguments, got 3
Warning: lim requires 3 arguments, got 2
Warning: matrix requires 4 arguments, got 3

# Version 5.0

## Diagnostic Engine Milestone

UTCE MathConvert has evolved from a plain-text mathematical converter into a diagnostic conversion engine.

New capabilities include:

* Warning detection for malformed expressions
* Severity classification (ERROR / WARNING / INFO)
* Suggested fix generation
* Highlight Report HTML output
* Warning statistics and summary panel
* Inline diagnostic reporting

Example:

Input:
frac(1)

Output Warning:
[ERROR] Line 34: frac requires 2 arguments, got 1

Suggested Fix:
frac(numerator, denominator)

This version establishes the foundation for future semantic validation and academic writing support.

## v5.0 Diagnostic Engine Milestone

UTCE MathConvert is no longer only a plain-to-LaTeX converter.  
It now functions as a lightweight diagnostic conversion engine.

Core features:

- Plain text to LaTeX conversion
- Inline / block / raw output modes
- Warning detection
- Source line tracking
- HTML highlight report
- Clickable warning links
- Suggested fix panel
- Severity labels: ERROR / WARNING / INFO
- Warning type summary

This version marks the transition from simple conversion to diagnostic-assisted conversion.