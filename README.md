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