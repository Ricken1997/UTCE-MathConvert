import subprocess
import re
import sys
import os
import html

VERSION = "5.8-refactor-core"

STRUCTURAL_CORE = {
    "observer": "User intention / conversion purpose",
    "theory": "Plain math to LaTeX conversion and validation rules",
    "reality": "LaTeX constraints, document constraints, journal constraints",
    "target": "Input mathematical expression or document structure",
    "time": "Input → warning → fix → reconversion",
}

class WarningInfo:
    def __init__(
        self,
        line_number,
        severity,
        warning_type,
        message,
        suggestion=""
    ):
        self.line_number = line_number
        self.severity = severity
        self.warning_type = warning_type
        self.message = message
        self.suggestion = suggestion

    def to_dict(self):
        return {
            "line_number": self.line_number,
            "severity": self.severity,
            "warning_type": self.warning_type,
            "message": self.message,
            "suggestion": self.suggestion,
        }

    def calculate_confidence_score(
    observer_clarity,
    theory_fit,
    reality_compatibility,
    target_coherence,
    temporal_stability
    ):
        return (
            observer_clarity
            + theory_fit
            + reality_compatibility
            + target_coherence
            + temporal_stability
        ) / 5    

# ============================================================
# Diagnosis Engine
# ============================================================

def classify_warning(warning):
    if "requires" in warning:
        return "ERROR"
    if "unsupported" in warning:
        return "WARNING"
    return "INFO"


def suggest_fix(expr):
    suggestions = {
        "frac(": "frac(numerator, denominator)",
        "sum(": "sum(index, start, end, expression)",
        "int(": "int(start, end, expression, variable)",
        "lim(": "lim(variable, target, expression)",
        "matrix(": "matrix(a,b;c,d)",
    }

    for prefix, suggestion in suggestions.items():
        if expr.startswith(prefix):
            return suggestion

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


def parse_warning_type(warning):
    match = re.search(r"Warning: ([a-zA-Z_]+)", warning)
    return match.group(1) if match else "unknown"


def parse_source_line(warning):
    match = re.search(r"Line (\d+):", warning)
    return match.group(1) if match else ""


# ============================================================
# Conversion Engine
# ============================================================

def plain_to_latex(expr):
    expr = re.sub(r"frac\((\d+),(\d+)\)", r"\\frac{\1}{\2}", expr)

    expr = re.sub(
        r"sum\(([^,]+),([^,]+),([^,]+),([^)]+)\)",
        r"\\sum_{\1=\2}^{\3} \4",
        expr,
    )

    expr = re.sub(
        r"int\(([^,]+),([^,]+),([^,]+),([^)]+)\)",
        r"\\int_{\1}^{\2} \3 \\, d\4",
        expr,
    )

    expr = re.sub(
        r"lim\(([^,]+),([^,]+),([^)]+)\)",
        r"\\lim_{\1 \\to \2} \3",
        expr,
    )

    expr = re.sub(
        r"partial\(([^,]+),([^)]+)\)",
        r"\\frac{\\partial \1}{\\partial \2}",
        expr,
    )

    expr = re.sub(
        r"cases\((.*?);(.*?)\)",
        r"\\begin{cases} \1 \\\\ \2 \\end{cases}",
        expr,
    )

    expr = re.sub(
        r"matrix\(([^,;]+),([^;]+);([^,;]+),([^)]+)\)",
        r"\\begin{bmatrix} \1 & \2 \\\\ \3 & \4 \\end{bmatrix}",
        expr,
    )

    expr = re.sub(r"det\((.*?)\)", r"\\det(\1)", expr)
    expr = re.sub(r"floor\((.*?)\)", r"\\left\\lfloor \1 \\right\\rfloor", expr)
    expr = re.sub(r"ceil\((.*?)\)", r"\\left\\lceil \1 \\right\\rceil", expr)

    expr = re.sub(r"dot\((.*?),(.*?)\)", r"\1 \\cdot \2", expr)
    expr = re.sub(r"cross\((.*?),(.*?)\)", r"\1 \\times \2", expr)

    expr = re.sub(r"sqrt\((.*?)\)", r"\\sqrt{\1}", expr)
    expr = re.sub(r"abs\((.*?)\)", r"\\left|\1\\right|", expr)
    expr = re.sub(r"vec\((.*?)\)", r"\\vec{\1}", expr)
    expr = re.sub(r"hat\((.*?)\)", r"\\hat{\1}", expr)
    expr = re.sub(r"bar\((.*?)\)", r"\\bar{\1}", expr)
    expr = re.sub(r"max\((.*?)\)", r"\\max(\1)", expr)
    expr = re.sub(r"min\((.*?)\)", r"\\min(\1)", expr)
    expr = re.sub(r"norm\((.*?)\)", r"\\left\\|\1\\right\\|", expr)

    expr = re.sub(r"sin\((.*?)\)", r"\\sin(\1)", expr)
    expr = re.sub(r"cos\((.*?)\)", r"\\cos(\1)", expr)
    expr = re.sub(r"tan\((.*?)\)", r"\\tan(\1)", expr)
    expr = re.sub(r"log\((.*?)\)", r"\\log(\1)", expr)
    expr = re.sub(r"ln\((.*?)\)", r"\\ln(\1)", expr)
    expr = re.sub(r"exp\((.*?)\)", r"e^{\1}", expr)

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
        expr = re.sub(rf"\b{plain}\b", latex, expr)

    expr = re.sub(r"\bpi\b", r"\\pi", expr)

    expr = expr.replace("<=", r"\le ")
    expr = expr.replace(">=", r"\ge ")
    expr = expr.replace("!=", r"\ne ")
    expr = expr.replace("<->", r"\leftrightarrow ")
    expr = expr.replace("->", r"\to ")
    expr = expr.replace("*", r"\cdot ")

    expr = re.sub(r"([A-Za-z])_([0-9A-Za-z])", r"\1_{\2}", expr)
    expr = re.sub(r"([A-Za-z])_\(([^()]*)\)", r"\1_{\2}", expr)
    expr = re.sub(r"([A-Za-z])\^([0-9A-Za-z])", r"\1^{\2}", expr)

    return "$" + expr + "$"


def build_latex_output(latex_lines, mode):
    if mode == "--block":
        return "\n".join([r"\[" + line.strip("$") + r"\]" for line in latex_lines])
    if mode == "--raw":
        return "\n".join([line.strip("$") for line in latex_lines])
    return "\n".join(latex_lines)


# ============================================================
# Analysis Engine
# ============================================================

def analyze_lines(lines):
    latex_lines = []
    warnings = []
    severity_counts = {}

    for line_number, line in enumerate(lines, start=1):
        text = line.strip()

        if not text:
            continue

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

        latex_lines.append(plain_to_latex(text))

    return latex_lines, warnings, severity_counts


# ============================================================
# Report Engine
# ============================================================

def build_html_head():
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html>")
    lines.append("<head>")
    lines.append('<meta charset="utf-8">')
    lines.append("<title>UTCE MathConvert Highlight Report</title>")
    lines.append("<style>")
    lines.append("body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 24px; }")
    lines.append("h1 { font-size: 24px; }")
    lines.append(".ok { background: #e8f5e9; padding: 6px; margin: 4px 0; }")
    lines.append(".error { background:#ffe6e6; border-left:4px solid #cc0000; padding:6px; margin:4px 0; }")
    lines.append(".warning { background:#fff8d6; border-left:4px solid #e6b800; padding:6px; margin:4px 0; }")
    lines.append(".info { background:#eef7ff; border-left:4px solid #3399ff; padding:6px; margin:4px 0; }")
    lines.append(".summary { background:#f5f5f5; padding:12px; margin:12px 0; border-radius:6px; }")
    lines.append(".summary div { margin:4px 0; }")
    lines.append(".line { font-family:monospace; }")
    lines.append(".latex { color:#333; font-family:monospace; }")
    lines.append(".lineno { color:#777; display:inline-block; width:48px; }")
    lines.append(".suggestion { margin-top:6px; padding:6px; background:#eef7ff; border-left:4px solid #2196f3; font-family:monospace; }")
    lines.append(".suggestion-label { font-weight:bold; }")
    lines.append("button { margin-right:4px; padding:3px 8px; }")
    lines.append("</style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("<h1>UTCE MathConvert Highlight Report</h1>")
    return lines


def build_summary_section(lines, latex_lines, warnings, severity_counts):
    warning_type_counts = {}

    for warning in warnings:
        warning_type = parse_warning_type(warning)
        warning_type_counts[warning_type] = warning_type_counts.get(warning_type, 0) + 1

    html_lines = []
    html_lines.append("<h2>Summary</h2>")
    html_lines.append('<div class="summary">')
    html_lines.append(f"<div>Input Lines: {len(lines)}</div>")
    html_lines.append(f"<div>Output Lines: {len(latex_lines)}</div>")
    html_lines.append(f"<div>Warnings: {len(warnings)}</div>")

    if severity_counts:
        html_lines.append("<div><strong>Severity:</strong></div>")
        for severity, count in severity_counts.items():
            html_lines.append(f"<div>{html.escape(severity)}: {count}</div>")

    if warning_type_counts:
        html_lines.append("<div><strong>Warning Types:</strong></div>")
        for warning_type, count in warning_type_counts.items():
            html_lines.append(f"<div>{html.escape(warning_type)}: {count}</div>")

    html_lines.append("</div>")
    return html_lines


def build_warning_controls():
    return ["""
<h2>Warnings</h2>

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
"""]


def build_warning_list(warnings):
    html_lines = []

    if not warnings:
        html_lines.append('<div class="ok">No warnings.</div>')
        return html_lines

    for idx, warning in enumerate(warnings, start=1):
        css_class = "info"

        if "[ERROR]" in warning:
            css_class = "error"
        elif "[WARNING]" in warning:
            css_class = "warning"
        elif "[INFO]" in warning:
            css_class = "info"

        source_line = parse_source_line(warning)
        warning_type = parse_warning_type(warning)

        warning_text = warning
        suggestion_text = ""

        if " | Suggestion: " in warning:
            warning_text, suggestion_text = warning.split(" | Suggestion: ", 1)

        if source_line:
            html_lines.append(
                f'<div class="{css_class}" '
                f'data-severity="{css_class}" '
                f'data-warning-type="{html.escape(warning_type)}">'
                f'<span class="lineno">{idx}</span>'
                f'<a href="#line-{source_line}">{html.escape(warning_text)}</a>'
                f'</div>'
            )
        else:
            html_lines.append(
                f'<div class="{css_class}" '
                f'data-severity="{css_class}" '
                f'data-warning-type="{html.escape(warning_type)}">'
                f'<span class="lineno">{idx}</span>{html.escape(warning_text)}'
                f'</div>'
            )

        if suggestion_text:
            html_lines.append(
                f'<div class="suggestion"><span class="suggestion-label">Suggested Fix:</span> '
                f'{html.escape(suggestion_text)}</div>'
            )

    return html_lines


def build_latex_output_panel(latex_lines):
    html_lines = []
    html_lines.append("<h2>LaTeX Output</h2>")

    for idx, line in enumerate(latex_lines, start=1):
        html_lines.append(
            f'<div class="line latex" id="line-{idx}">'
            f'<span class="lineno">{idx}</span>{html.escape(line)}</div>'
        )

    return html_lines


def build_javascript():
    return ["""
<script>
function applyFilters() {
    const keywordInput = document.getElementById("warningSearch");
    const keyword = keywordInput ? keywordInput.value.toLowerCase() : "";
    const active = window.currentSeverity || "all";

    document.querySelectorAll("[data-severity]").forEach(function (el) {
        const severity = el.getAttribute("data-severity");
        const warningType = el.getAttribute("data-warning-type") || "";
        const text = (
            el.textContent + " " +
            severity + " " +
            warningType + " " +
            el.className
        ).toLowerCase();

        const severityMatch = active === "all" || severity === active;
        const keywordMatch = keyword === "" || text.includes(keyword);

        const show = severityMatch && keywordMatch;

        el.style.display = show ? "" : "none";

        const next = el.nextElementSibling;
        if (next && next.classList.contains("suggestion")) {
            next.style.display = show ? "" : "none";
        }
    });
}

document.querySelectorAll("button[data-filter]").forEach(function (button) {
    button.addEventListener("click", function () {
        window.currentSeverity = button.getAttribute("data-filter");
        applyFilters();
    });
});

const searchInput = document.getElementById("warningSearch");
if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
}
</script>
"""]


def build_html_report(lines, latex_lines, warnings, severity_counts, html_report_file):
    html_lines = []
    html_lines.extend(build_html_head())
    html_lines.extend(build_summary_section(lines, latex_lines, warnings, severity_counts))
    html_lines.extend(build_warning_controls())
    html_lines.extend(build_warning_list(warnings))
    html_lines.extend(build_latex_output_panel(latex_lines))
    html_lines.extend(build_javascript())
    html_lines.append("</body>")
    html_lines.append("</html>")

    with open(html_report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))


# ============================================================
# CLI
# ============================================================

def print_usage():
    print()
    print(f"UTCE MathConvert {VERSION}")
    print()
    print("Usage:")
    print("  python3 utce_core.py input.txt output.txt --inline")
    print("  python3 utce_core.py input.txt output.txt --block")
    print("  python3 utce_core.py input.txt output.txt --raw")
    print("  python3 utce_core.py input.txt output.txt --inline --copy")
    print()


def main():
    if "--version" in sys.argv or "-v" in sys.argv:
        print(f"UTCE MathConvert {VERSION}")
        sys.exit(0)

    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        sys.exit(0)

    if len(sys.argv) < 3:
        print_usage()
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    mode = "--inline"
    valid_modes = ["--inline", "--block", "--raw"]

    for arg in sys.argv[3:]:
        if arg in valid_modes:
            mode = arg

    if mode not in valid_modes:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

    copy_to_clipboard = "--copy" in sys.argv

    warnings_file = "output_warnings.txt"
    html_report_file = "highlight_report.html"

    if not os.path.exists(input_file):
        print()
        print(f"Input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    latex_lines, warnings, severity_counts = analyze_lines(lines)

    latex = build_latex_output(latex_lines, mode)

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
        f.write("\n".join(warnings) if warnings else "No warnings.")

    print(f"Warnings saved to: {warnings_file}")

    build_html_report(lines, latex_lines, warnings, severity_counts, html_report_file)
    print(f"HTML report saved to: {html_report_file}")

    if copy_to_clipboard:
        subprocess.run("pbcopy", text=True, input=latex)
        print("Output copied to clipboard.")


if __name__ == "__main__":
    main()