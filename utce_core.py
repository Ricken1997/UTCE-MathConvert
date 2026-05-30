import subprocess
import re
import sys
import os
import html

VERSION = "3.0-beta"

def validate_plain_math(expr):
    warnings = []

    checks = {
        "frac": 2,
        "sum": 4,
        "int": 4,
        "lim": 3,
        "partial": 2,
        "matrix": 4,
        "dot": 2,
        "cross": 2,
        "max": 2,
        "min": 2,
    }

    for name, required_count in checks.items():
        if expr.startswith(name + "(") and expr.endswith(")"):
            inside = expr[len(name) + 1:-1]
            parts = [p.strip() for p in inside.split(",")]
            if len(parts) < required_count:
                warnings.append(
                    f"Warning: {name} requires {required_count} arguments, got {len(parts)}: {expr}"
                )

    return warnings

def plain_to_latex(expr):
    # Basic structured functions
    expr = re.sub(r"frac\((\d+),(\d+)\)", r"\\frac{\1}{\2}", expr)

    expr = re.sub(
        r"sum\(([^,]+),([^,]+),([^,]+),([^)]+)\)",
        r"\\sum_{\1=\2}^{\3} \4",
        expr
    )

    expr = re.sub(
        r"int\(([^,]+),([^,]+),([^,]+),([^)]+)\)",
        r"\\int_{\1}^{\2} \3 \\, d\4",
        expr
    )

    expr = re.sub(
        r"lim\(([^,]+),([^,]+),([^)]+)\)",
        r"\\lim_{\1 \\to \2} \3",
        expr
    )

    expr = re.sub(
        r"partial\(([^,]+),([^)]+)\)",
        r"\\frac{\\partial \1}{\\partial \2}",
        expr
    )

    expr = re.sub(
        r"cases\((.*?);(.*?)\)",
        r"\\begin{cases} \1 \\\\ \2 \\end{cases}",
        expr
    )

    expr = re.sub(
        r"matrix\(([^,;]+),([^;]+);([^,;]+),([^)]+)\)",
        r"\\begin{bmatrix} \1 & \2 \\\\ \3 & \4 \\end{bmatrix}",
        expr
    )

    expr = re.sub(r"det\((.*?)\)", r"\\det(\1)", expr)
    expr = re.sub(r"floor\((.*?)\)", r"\\left\\lfloor \1 \\right\\rfloor", expr)
    expr = re.sub(r"ceil\((.*?)\)", r"\\left\\lceil \1 \\right\\rceil", expr)

    expr = re.sub(
    r"dot\((.*?),(.*?)\)",
    r"\1 \\cdot \2",
    expr
    )

    expr = re.sub(
    r"cross\((.*?),(.*?)\)",
    r"\1 \\times \2",
    expr
    )

    # Wrappers
    expr = re.sub(r"sqrt\((.*?)\)", r"\\sqrt{\1}", expr)
    expr = re.sub(r"abs\((.*?)\)", r"\\left|\1\\right|", expr)
    expr = re.sub(r"vec\((.*?)\)", r"\\vec{\1}", expr)
    expr = re.sub(r"hat\((.*?)\)", r"\\hat{\1}", expr)
    expr = re.sub(r"bar\((.*?)\)", r"\\bar{\1}", expr)
    expr = re.sub(r"max\((.*?)\)", r"\\max(\1)", expr)
    expr = re.sub(r"min\((.*?)\)", r"\\min(\1)", expr)
    expr = re.sub(r"norm\((.*?)\)", r"\\left\\|\1\\right\\|", expr)

    # Functions
    expr = re.sub(r"sin\((.*?)\)", r"\\sin(\1)", expr)
    expr = re.sub(r"cos\((.*?)\)", r"\\cos(\1)", expr)
    expr = re.sub(r"tan\((.*?)\)", r"\\tan(\1)", expr)
    expr = re.sub(r"log\((.*?)\)", r"\\log(\1)", expr)
    expr = re.sub(r"ln\((.*?)\)", r"\\ln(\1)", expr)
    expr = re.sub(r"exp\((.*?)\)", r"e^{\1}", expr)

    # Greek letters
    greek = {
    "alpha": r"\alpha",
    "beta": r"\beta",
    "gamma": r"\gamma",
    "delta": r"\delta",
    "epsilon": r"\epsilon",
    "theta": r"\theta",
    "lambda": r"\lambda",
    "mu": r"\mu",
    "nu": r"\nu",
    "rho": r"\rho",
    "sigma": r"\sigma",
    "phi": r"\phi",
    "omega": r"\omega",
}

    for plain, latex in greek.items():
        expr = re.sub(rf"\b{plain}\b", lambda m: latex, expr)

    # Constants and operators
    expr = re.sub(r"\bpi\b", r"\\pi", expr)
    expr = expr.replace("<=", r"\le ")
    expr = expr.replace(">=", r"\ge ")
    expr = expr.replace("!=", r"\ne ")
    expr = expr.replace("->", r"\to ")
    expr = expr.replace("<->", r"\leftrightarrow ")
    expr = expr.replace("*", r"\cdot ")

    # Subscripts
    expr = re.sub(
    r"([A-Za-z])_([0-9A-Za-z])",
    r"\1_{\2}",
    expr
    )

    expr = re.sub(
    r"([A-Za-z])_\(([^()]*)\)",
    r"\1_{\2}",
    expr
    )
    
    # Exponents
    expr = re.sub(
        r"([A-Za-z])\^([0-9A-Za-z])",
        r"\1^{\2}",
        expr
    )

    return "$" + expr + "$"

if len(sys.argv) < 3 and "--help" not in sys.argv and "-h" not in sys.argv and "--version" not in sys.argv and "-v" not in sys.argv:
    print()
    print(f"UTCE MathConvert {VERSION}")
    print()
    print("Usage:")
    print("  python3 utce_core.py input.txt output.txt --inline")
    print("  python3 utce_core.py input.txt output.txt --block")
    print("  python3 utce_core.py input.txt output.txt --raw")
    print("  python3 utce_core.py input.txt output.txt --inline --copy")
    print()
    sys.exit(1)

input_file = "test_input.txt"
output_file = "output_latex.txt"
warnings_file = "output_warnings.txt"
html_report_file = "highlight_report.html"

if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
    input_file = sys.argv[1]

if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
    output_file = sys.argv[2]

if not os.path.exists(input_file):
    print()
    print(f"Input file not found: {input_file}")
    sys.exit(1)

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

latex_lines = []

warnings = []

for line in lines:
    text = line.strip()
    if text:
        warnings.extend(validate_plain_math(text))
        latex_lines.append(plain_to_latex(text))

if "--version" in sys.argv or "-v" in sys.argv:
    print(f"UTCE MathConvert {VERSION}")
    sys.exit(0)

if "--help" in sys.argv or "-h" in sys.argv:
    print(f"UTCE MathConvert {VERSION}")
    print()
    print("Usage:")
    print("  python3 utce_core.py input.txt output.txt --inline")
    print("  python3 utce_core.py input.txt output.txt --block")
    print("  python3 utce_core.py input.txt output.txt --raw")
    print()
    print("Modes:")
    print("  --inline   Output as $...$")
    print("  --block    Output as \\[...\\]")
    print("  --raw      Output LaTeX without math delimiters")
    sys.exit(0)

copy_to_clipboard = "--copy" in sys.argv

mode = "--inline"

if len(sys.argv) >= 4:
    mode = sys.argv[3]

    valid_modes = ["--inline", "--block", "--raw"]

if mode not in valid_modes:
    print()
    print(f"Unknown mode: {mode}")
    print("Use --inline, --block, or --raw")
    sys.exit(1)   

if mode == "--block":
    latex = "\n".join([r"\[" + line.strip("$") + r"\]" for line in latex_lines])
elif mode == "--raw":
    latex = "\n".join([line.strip("$") for line in latex_lines])
else:
    latex = "\n".join(latex_lines)

print("Plain:")
for line in lines:
    print(line.strip())

if warnings:
    print()
    print("Warnings:")
    for warning in warnings:
        print(warning)

print()
print("LaTeX:")
print(latex)

with open(output_file, "w", encoding="utf-8") as f:
    f.write(latex)

print()
print(f"Output saved to: {output_file}")

with open(warnings_file, "w", encoding="utf-8") as f:
    if warnings:
        f.write("\n".join(warnings))
    else:
        f.write("No warnings.")

print(f"Warnings saved to: {warnings_file}")

html_lines = []
html_lines.append("<!DOCTYPE html>")
html_lines.append("<html>")
html_lines.append("<head>")
html_lines.append('<meta charset="utf-8">')
html_lines.append("<title>UTCE MathConvert Highlight Report</title>")
html_lines.append("<style>")
html_lines.append("body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; }")
html_lines.append("h1 { font-size: 24px; }")
html_lines.append(".ok { background: #e8f5e9; padding: 6px; margin: 4px 0; }")
html_lines.append(".warn { background: #fff3cd; padding: 6px; margin: 4px 0; border-left: 4px solid #ff9800; }")
html_lines.append(".line { font-family: monospace; }")
html_lines.append(".latex { color: #333; font-family: monospace; }")
html_lines.append("</style>")
html_lines.append("</head>")
html_lines.append("<body>")
html_lines.append("<h1>UTCE MathConvert Highlight Report</h1>")

html_lines.append("<h2>Warnings</h2>")
if warnings:
    for warning in warnings:
        html_lines.append(f'<div class="warn">{html.escape(warning)}</div>')
else:
    html_lines.append('<div class="ok">No warnings.</div>')

html_lines.append("<h2>LaTeX Output</h2>")
for line in latex_lines:
    html_lines.append(f'<div class="line latex">{html.escape(line)}</div>')

html_lines.append("</body>")
html_lines.append("</html>")

with open(html_report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))

print(f"HTML report saved to: {html_report_file}")

if copy_to_clipboard:
    subprocess.run("pbcopy", text=True, input=latex)
    print("Output copied to clipboard.")