import subprocess
import re
import sys
import os
import html

VERSION = "3.0-beta"

def classify_warning(warning):
    if "requires" in warning:
        return "ERROR"

    if "unsupported" in warning:
        return "WARNING"

    return "INFO"

def suggest_fix(expr):
    if expr.startswith("frac("):
        return "frac(numerator, denominator)"

    if expr.startswith("sum("):
        return "sum(index, start, end, expression)"

    if expr.startswith("int("):
        return "int(start, end, expression, variable)"

    if expr.startswith("lim("):
        return "lim(variable, target, expression)"

    if expr.startswith("matrix("):
        return "matrix(a,b;c,d)"

    return ""

def validate_plain_math(expr):
    warnings = []

    checks = {
        "frac": 2,
        "sum": 4,
        "int": 4,
        "lim": 3,
        "partial": 2,
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

    matrix_match = re.search(r"matrix\(([^)]*)\)", expr)

    if matrix_match:
        content = matrix_match.group(1)
        rows = [row.strip() for row in content.split(";") if row.strip()]

        if len(rows) < 2:
            warnings.append(
                f"Warning: matrix requires at least 2 rows separated by ';': {expr}"
            )
        else:
            column_counts = []

            for row in rows:
                cols = [c.strip() for c in row.split(",") if c.strip()]
                column_counts.append(len(cols))

            if len(set(column_counts)) != 1:
                warnings.append(
                    f"Warning: matrix rows have inconsistent column counts: {expr}"
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
severity_counts = {}

for line_number, line in enumerate(lines, start=1):
    text = line.strip()

    if text:
        line_warnings = validate_plain_math(text)

        for warning in line_warnings:
            suggestion = suggest_fix(text)

            severity = classify_warning(warning)
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

            if suggestion:
                warnings.append(
                    f"[{severity}] Line {line_number}: {warning} | Suggestion: {suggestion}"
                )
            else:
                warnings.append(
                    f"[{severity}] Line {line_number}: {warning}"
                )

        latex_lines.append(
            plain_to_latex(text)
        )

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
html_lines.append(".error { background:#ffe6e6; border-left:4px solid #cc0000; padding:6px; margin:4px 0; }")
html_lines.append(".warning { background:#fff8d6; border-left:4px solid #e6b800; padding:6px; margin:4px 0; }")
html_lines.append(".info { background:#eef7ff; border-left:4px solid #3399ff; padding:6px; margin:4px 0; }")
html_lines.append(".summary { background: #f5f5f5; padding: 12px; margin: 12px 0; border-radius: 6px; }")
html_lines.append(".summary div { margin: 4px 0; }")
html_lines.append(".line { font-family: monospace; }")
html_lines.append(".latex { color: #333; font-family: monospace; }")
html_lines.append(".lineno { color: #777; display: inline-block; width: 48px; }")
html_lines.append(".suggestion { margin-top: 6px; padding: 6px; background: #eef7ff; border-left: 4px solid #2196f3; font-family: monospace; }")
html_lines.append(".suggestion-label { font-weight: bold; }")
html_lines.append("</style>")
html_lines.append("</head>")
html_lines.append("<body>")
html_lines.append("<h1>UTCE MathConvert Highlight Report</h1>")

input_line_count = len(lines)
output_line_count = len(latex_lines)
warning_count = len(warnings)

for warning in warnings:
    match = re.search(r"\[([A-Z]+)\]", warning)
    if match:
        severity = match.group(1)

warning_type_counts = {}

for warning in warnings:
    match = re.search(r"Warning: ([a-zA-Z_]+)", warning)
    if match:
        warning_type = match.group(1)
        warning_type_counts[warning_type] = warning_type_counts.get(warning_type, 0) + 1

html_lines.append("<h2>Summary</h2>")
html_lines.append('<div class="summary">')
html_lines.append(f"<div>Input Lines: {input_line_count}</div>")
html_lines.append(f"<div>Output Lines: {output_line_count}</div>")
html_lines.append(f"<div>Warnings: {warning_count}</div>")

if severity_counts:
    html_lines.append("<div><strong>Severity:</strong></div>")
    for severity, count in severity_counts.items():
        html_lines.append(f"<div>{html.escape(severity)}: {count}</div>")

if warning_type_counts:
    html_lines.append("<div><strong>Warning Types:</strong></div>")
    for warning_type, count in warning_type_counts.items():
        html_lines.append(f"<div>{html.escape(warning_type)}: {count}</div>")

html_lines.append("</div>")

html_lines.append("<h2>Warnings</h2>")

html_lines.append("""
<script>
document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll("button[data-filter]").forEach(function (button) {
        button.addEventListener("click", function () {
            const level = button.getAttribute("data-filter");

            document.querySelectorAll("[data-severity]").forEach(function (el) {
                const show = level === "all" || el.getAttribute("data-severity") === level;
                el.style.display = show ? "" : "none";

                const next = el.nextElementSibling;
                if (next && next.classList.contains("suggestion")) {
                    next.style.display = show ? "" : "none";
                }
            });
        });
    });
});
</script>
""")

html_lines.append("""
<div style="margin:12px 0;">
<button data-filter="all">All</button>
<button data-filter="error">Error</button>
<button data-filter="warning">Warning</button>
<button data-filter="info">Info</button>
</div>

<div style="margin:8px 0 12px 0;">
<input id="warningSearch"
       type="text"
       placeholder="Search warnings..."
       style="padding:4px; width:240px;">
</div>
""")

if warnings:
    for idx, warning in enumerate(warnings, start=1):
        css_class = "warn"
        if "[ERROR]" in warning:
            css_class = "error"
        elif "[WARNING]" in warning:
            css_class = "warning"
        elif "[INFO]" in warning:
            css_class = "info"
        line_match = re.search(r"Line (\d+):", warning)
        if line_match:
            source_line = line_match.group(1)
            warning_text = warning
            suggestion_text = ""

            if " | Suggestion: " in warning:
                warning_text, suggestion_text = warning.split(" | Suggestion: ", 1)

            html_lines.append(
                f'<div class="{css_class}" data-severity="{css_class}"><span class="lineno">{idx}</span>'
                f'<a href="#line-{source_line}">{html.escape(warning_text)}</a>'
                f'</div>'
            )

            if suggestion_text:
                html_lines.append(
                    f'<div class="suggestion"><span class="suggestion-label">Suggested Fix:</span> '
                    f'{html.escape(suggestion_text)}</div>'
                )

            html_lines.append("</div>")

        else:
            html_lines.append(
                f'<div class="{css_class}" data-severity="{css_class}"><span class="lineno">{idx}</span>{html.escape(warning)}</div>'
            )
else:
    html_lines.append('<div class="ok">No warnings.</div>')

html_lines.append("<h2>LaTeX Output</h2>")
for idx, line in enumerate(latex_lines, start=1):
    html_lines.append(
        f'<div class="line latex" id="line-{idx}">'
        f'<span class="lineno">{idx}</span>{html.escape(line)}</div>'
    )

html_lines.append("</body>")
html_lines.append("</html>")

with open(html_report_file, "w", encoding="utf-8") as f:
    f.write("\n".join(html_lines))

print(f"HTML report saved to: {html_report_file}")

if copy_to_clipboard:
    subprocess.run("pbcopy", text=True, input=latex)
    print("Output copied to clipboard.")