#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UTCE MathConvert Core
Version: v6.6-full-refactor-template

Purpose:
- Convert plain math-like expressions into LaTeX.
- Validate common math-command argument errors.
- Generate warning reports.
- Generate HTML highlight report.
- Provide structural diagnostic summary.
"""

import argparse
import html
import os
import re
import subprocess
import sys
from dataclasses import dataclass


# ============================================================
# 1. Data Models
# ============================================================

@dataclass
class WarningInfo:
    line_number: int
    severity: str
    warning_type: str
    message: str
    suggestion: str = ""
    confidence: float = 80.0
    risk_score: float = 20.0

    def to_text(self) -> str:
        base = f"[{self.severity}] Line {self.line_number}: {self.message}"
        if self.suggestion:
            base += f" | Suggestion: {self.suggestion}"
        return base


class StructuralDiagnosis:
    def __init__(
        self,
        observer_clarity=80,
        theory_fit=80,
        reality_compatibility=80,
        target_coherence=80,
        temporal_stability=80,
        residual_risk=20,
        meta_diagnostic_risk=20,
        cross_application_validation=80,
    ):
        self.observer_clarity = observer_clarity
        self.theory_fit = theory_fit
        self.reality_compatibility = reality_compatibility
        self.target_coherence = target_coherence
        self.temporal_stability = temporal_stability
        self.residual_risk = residual_risk
        self.meta_diagnostic_risk = meta_diagnostic_risk
        self.cross_application_validation = cross_application_validation

        self.confidence_score = calculate_confidence_score(
            observer_clarity,
            theory_fit,
            reality_compatibility,
            target_coherence,
            temporal_stability,
        )

        self.predictive_risk = self.calculate_predictive_risk()

    def calculate_predictive_risk(self) -> float:
        return (
            (100 - self.confidence_score)
            + self.residual_risk
            + (100 - self.temporal_stability)
            + self.meta_diagnostic_risk
            + (100 - self.cross_application_validation)
        ) / 5

    def risk_level(self) -> str:
        if self.predictive_risk >= 80:
            return "CRITICAL"
        if self.predictive_risk >= 60:
            return "HIGH"
        if self.predictive_risk >= 40:
            return "MODERATE"
        if self.predictive_risk >= 20:
            return "LOW"
        return "MINIMAL"

    def recommendation(self) -> str:
        level = self.risk_level()
        if level == "CRITICAL":
            return "Immediate structural review required."
        if level == "HIGH":
            return "Review warning source and apply suggested fixes before reuse."
        if level == "MODERATE":
            return "Proceed with caution and verify output manually."
        if level == "LOW":
            return "Output is mostly stable, but minor review is recommended."
        return "Output is structurally stable."

    def to_dict(self) -> dict:
        return {
            "observer_clarity": self.observer_clarity,
            "theory_fit": self.theory_fit,
            "reality_compatibility": self.reality_compatibility,
            "target_coherence": self.target_coherence,
            "temporal_stability": self.temporal_stability,
            "residual_risk": self.residual_risk,
            "meta_diagnostic_risk": self.meta_diagnostic_risk,
            "cross_application_validation": self.cross_application_validation,
            "confidence_score": self.confidence_score,
            "predictive_risk": self.predictive_risk,
            "risk_level": self.risk_level(),
            "recommendation": self.recommendation(),
        }


# ============================================================
# 2. Scoring / Diagnosis Helpers
# ============================================================

def calculate_confidence_score(
    observer_clarity,
    theory_fit,
    reality_compatibility,
    target_coherence,
    temporal_stability,
) -> float:
    return (
        observer_clarity
        + theory_fit
        + reality_compatibility
        + target_coherence
        + temporal_stability
    ) / 5


def calculate_warning_risk_score(severity: str) -> int:
    if severity == "ERROR":
        return 80
    if severity == "WARNING":
        return 50
    return 20


def build_diagnosis_from_severity_counts(severity_counts: dict) -> StructuralDiagnosis:
    error_count = severity_counts.get("ERROR", 0)
    warning_count = severity_counts.get("WARNING", 0)
    info_count = severity_counts.get("INFO", 0)

    risk_load = (error_count * 15) + (warning_count * 8) + (info_count * 3)
    risk_load = min(100, risk_load)

    stability_score = max(0, 100 - risk_load)

    return StructuralDiagnosis(
        observer_clarity=stability_score,
        theory_fit=stability_score,
        reality_compatibility=stability_score,
        target_coherence=stability_score,
        temporal_stability=stability_score,
        residual_risk=risk_load,
        meta_diagnostic_risk=risk_load,
        cross_application_validation=stability_score,
    )


def get_risk_class(risk_level: str) -> str:
    if risk_level in ("MINIMAL", "LOW"):
        return "risk-low"
    if risk_level == "MODERATE":
        return "risk-moderate"
    return "risk-high"


# ============================================================
# 3. Warning / Validation Engine
# ============================================================

def classify_warning(warning: str) -> str:
    if "requires" in warning:
        return "ERROR"
    if "unsupported" in warning:
        return "WARNING"
    return "INFO"


def parse_warning_type(warning: str) -> str:
    match = re.search(r"Warning:\s*([A-Za-z_]+)", warning)
    if match:
        return match.group(1)
    return "unknown"


def suggest_fix(expr: str) -> str:
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


def validate_plain_math(expr: str) -> list[str]:
    warnings = []

    checks = {
        "frac": 2,
        "sum": 4,
        "int": 4,
        "lim": 3,
        "matrix": 2,
    }

    for name, required_count in checks.items():
        if expr.startswith(name + "(") and expr.endswith(")"):
            inside = expr[len(name) + 1 : -1]

            if name == "matrix":
                rows = [r.strip() for r in inside.split(";")]
                if len(rows) < required_count:
                    warnings.append(
                        f"Warning: matrix requires at least 2 rows separated by ';': {expr}"
                    )
                continue

            parts = [p.strip() for p in inside.split(",") if p.strip()]
            if len(parts) < required_count:
                warnings.append(
                    f"Warning: {name} requires {required_count} arguments, got {len(parts)}: {expr}"
                )

    return warnings


def create_warning_info(line_number: int, warning: str, text: str) -> WarningInfo:
    severity = classify_warning(warning)
    warning_type = parse_warning_type(warning)
    suggestion = suggest_fix(text)
    risk_score = calculate_warning_risk_score(severity)

    return WarningInfo(
        line_number=line_number,
        severity=severity,
        warning_type=warning_type,
        message=warning,
        suggestion=suggestion,
        confidence=80.0,
        risk_score=risk_score,
    )


# ============================================================
# 4. Conversion Engine
# ============================================================

def plain_to_latex(text: str) -> str:
    expr = text.strip()

    if not expr:
        return ""

    # Main structural commands
    result = convert_structural_expression(expr)

    if result is not None:
        return f"${result}$"

    expr = plain_to_latex_inner(expr)

    return f"${expr}$"


def plain_to_latex_inner(expr: str) -> str:
    expr = expr.strip()

    greek = {
        "alpha": r"\alpha",
        "beta": r"\beta",
        "gamma": r"\gamma",
        "delta": r"\delta",
        "theta": r"\theta",
        "lambda": r"\lambda",
        "mu": r"\mu",
        "nu": r"\nu",
        "rho": r"\rho",
        "sigma": r"\sigma",
        "phi": r"\phi",
        "omega": r"\omega",
        "pi": r"\pi",
    }

    for plain, latex in greek.items():
        expr = expr.replace(plain, latex)

    expr = expr.replace("<=", r"\le ")
    expr = expr.replace(">=", r"\ge ")
    expr = expr.replace("!=", r"\ne ")
    expr = expr.replace("<->", r"\leftrightarrow ")
    expr = expr.replace("->", r"\to ")
    expr = expr.replace("*", r"\cdot ")

    expr = re.sub(r"sqrt\((.*?)\)", r"\\sqrt{\1}", expr)
    expr = re.sub(r"sin\((.*?)\)", r"\\sin(\1)", expr)
    expr = re.sub(r"cos\((.*?)\)", r"\\cos(\1)", expr)
    expr = re.sub(r"tan\((.*?)\)", r"\\tan(\1)", expr)
    expr = re.sub(r"log\((.*?)\)", r"\\log(\1)", expr)
    expr = re.sub(r"ln\((.*?)\)", r"\\ln(\1)", expr)

    expr = re.sub(r"([A-Za-z0-9\\]+)_([A-Za-z0-9]+)", r"\1_{\2}", expr)
    expr = re.sub(r"([A-Za-z0-9\\]+)\^([A-Za-z0-9]+)", r"\1^{\2}", expr)

    return expr


def convert_structural_expression(expr: str) -> str | None:
    expr = expr.strip()

    if expr.startswith("frac(") and expr.endswith(")"):
        parts = split_args(expr[5:-1])
        if len(parts) == 2:
            return rf"\frac{{{plain_to_latex_inner(parts[0])}}}{{{plain_to_latex_inner(parts[1])}}}"

    if expr.startswith("sum(") and expr.endswith(")"):
        parts = split_args(expr[4:-1])
        if len(parts) == 4:
            index, start, end, body = parts
            return rf"\sum_{{{index}={start}}}^{{{end}}} {plain_to_latex_inner(body)}"

    if expr.startswith("prod(") and expr.endswith(")"):
        parts = split_args(expr[5:-1])
        if len(parts) == 4:
            index, start, end, body = parts
            return rf"\prod_{{{index}={start}}}^{{{end}}} {plain_to_latex_inner(body)}"

    if expr.startswith("int(") and expr.endswith(")"):
        parts = split_args(expr[4:-1])
        if len(parts) == 3:
            start, end, body = parts
            return rf"\int_{{{start}}}^{{{end}}} {plain_to_latex_inner(body)}"

    if expr.startswith("lim(") and expr.endswith(")"):
        parts = split_args(expr[4:-1])
        if len(parts) == 2:
            variable, target = parts
            return rf"\lim_{{{variable} \to {target}}}"

    if expr.startswith("matrix(") and expr.endswith(")"):
        rows = expr[7:-1].split(";")
        matrix_rows = []
        for row in rows:
            cols = [plain_to_latex_inner(c.strip()) for c in row.split(",")]
            matrix_rows.append(" & ".join(cols))
        return r"\begin{bmatrix}" + r" \\ ".join(matrix_rows) + r"\end{bmatrix}"

    if expr.startswith("vec(") and expr.endswith(")"):
        items = [plain_to_latex_inner(x.strip()) for x in expr[4:-1].split(",")]
        return r"\begin{pmatrix}" + r" \\ ".join(items) + r"\end{pmatrix}"

    if expr.startswith("det(") and expr.endswith(")"):
        rows = expr[4:-1].split(";")
        det_rows = []
        for row in rows:
            cols = [plain_to_latex_inner(c.strip()) for c in row.split(",")]
            det_rows.append(" & ".join(cols))
        return r"\begin{vmatrix}" + r" \\ ".join(det_rows) + r"\end{vmatrix}"

    if expr.startswith("cases(") and expr.endswith(")"):
        rows = expr[6:-1].split(";")
        case_rows = []
        for row in rows:
            parts = split_args(row)
            if len(parts) == 2:
                value, condition = parts
                case_rows.append(
                    f"{plain_to_latex_inner(value)} & {plain_to_latex_inner(condition)}"
                )
        return r"\begin{cases}" + r" \\ ".join(case_rows) + r"\end{cases}"

    if expr.startswith("abs(") and expr.endswith(")"):
        inside = plain_to_latex_inner(expr[4:-1])
        return rf"\left|{inside}\right|"

    if expr.startswith("norm(") and expr.endswith(")"):
        inside = plain_to_latex_inner(expr[5:-1])
        return rf"\left\|{inside}\right\|"

    if expr.startswith("diff(") and expr.endswith(")"):
        parts = split_args(expr[5:-1])
        if len(parts) == 2:
            expression, variable = parts
            return rf"\frac{{d}}{{d{variable}}}{plain_to_latex_inner(expression)}"

    if expr.startswith("pdiff(") and expr.endswith(")"):
        parts = split_args(expr[6:-1])
        if len(parts) == 2:
            expression, variable = parts
            return rf"\frac{{\partial {plain_to_latex_inner(expression)}}}{{\partial {variable}}}"

    if expr.startswith("exp(") and expr.endswith(")"):
        inside = plain_to_latex_inner(expr[4:-1])
        return rf"e^{{{inside}}}"

    if expr.startswith("factorial(") and expr.endswith(")"):
        inside = plain_to_latex_inner(expr[10:-1])
        return rf"{inside}!"

    if expr.startswith("binom(") and expr.endswith(")"):
        parts = split_args(expr[6:-1])
        if len(parts) == 2:
            n, r = parts
            return rf"\binom{{{plain_to_latex_inner(n)}}}{{{plain_to_latex_inner(r)}}}"

    if expr.startswith("union(") and expr.endswith(")"):
        parts = split_args(expr[6:-1])
        if len(parts) == 2:
            return rf"{parts[0]} \cup {parts[1]}"

    if expr.startswith("inter(") and expr.endswith(")"):
        parts = split_args(expr[6:-1])
        if len(parts) == 2:
            return rf"{parts[0]} \cap {parts[1]}"

    if expr.startswith("subset(") and expr.endswith(")"):
        parts = split_args(expr[7:-1])
        if len(parts) == 2:
            return rf"{parts[0]} \subset {parts[1]}"

    if expr.startswith("in(") and expr.endswith(")"):
        parts = split_args(expr[3:-1])
        if len(parts) == 2:
            return rf"{parts[0]} \in {parts[1]}"

    if expr.startswith("notin(") and expr.endswith(")"):
        parts = split_args(expr[6:-1])
        if len(parts) == 2:
            return rf"{parts[0]} \notin {parts[1]}"

    if expr.startswith("forall(") and expr.endswith(")"):
        parts = split_args(expr[7:-1], maxsplit=1)
        if len(parts) == 2:
            variable, statement = parts
            return rf"\forall {variable}\, {plain_to_latex_inner(statement)}"

    if expr.startswith("exists(") and expr.endswith(")"):
        parts = split_args(expr[7:-1], maxsplit=1)
        if len(parts) == 2:
            variable, statement = parts
            return rf"\exists {variable}\, {plain_to_latex_inner(statement)}"

    return None


def split_args(text: str, maxsplit: int = -1) -> list[str]:
    if maxsplit == -1:
        return [p.strip() for p in text.split(",")]
    return [p.strip() for p in text.split(",", maxsplit)]

def build_latex_output(latex_lines: list[str], mode: str) -> str:
    if mode == "block":
        return "\n".join([r"\[" + line.strip("$") + r"\]" for line in latex_lines])
    return "\n".join(latex_lines)


# ============================================================
# 5. Analysis Engine
# ============================================================

def analyze_lines(lines: list[str]):
    latex_lines = []
    warnings = []
    severity_counts = {}

    for line_number, line in enumerate(lines, start=1):
        text = line.strip()

        if not text:
            continue
        
        line_warnings = []

        # Argument validation for common Beta 1.0 structures
        if text.startswith("frac(") and text.endswith(")"):
            inner = text[5:-1]
            parts = [p.strip() for p in inner.split(",")]
            if len(parts) != 2 or not parts[0] or not parts[1]:
                line_warnings.append(
                    "frac requires exactly 2 non-empty arguments: frac(numerator, denominator)."
                )

        if text.startswith("sqrt(") and text.endswith(")"):
            inner = text[5:-1].strip()
            if not inner:
                line_warnings.append(
                    "sqrt requires 1 non-empty argument: sqrt(value)."
                )

        if text.startswith("matrix(") and text.endswith(")"):
            inner = text[7:-1]
            rows = inner.split(";")
            row_lengths = [len([c for c in row.split(",")]) for row in rows]

            if len(set(row_lengths)) > 1:
                line_warnings.append(
                    "Matrix row lengths differ. Each row should have the same number of columns."
                )

        # Direct LaTeX detection
        if "\\" in text:
            line_warnings.append(
                "Direct LaTeX input is not supported in Beta 1.0."
            )

        # Composite expression detection
        if any(op in text for op in [" + ", " - ", " * ", " = "]):
            line_warnings.append(
                "Composite expressions are not supported in Beta 1.0."
            )

        # Nested expression detection
        function_names = [
            "frac(", "sqrt(", "sup(", "pow(", "sub(",
            "subsup(", "sum(", "prod(", "int(",
            "diff(", "lim(", "matrix(", "cases("
        ]

        hit_count = sum(text.count(fn) for fn in function_names)

        if hit_count >= 2:
            line_warnings.append(
                "Nested expressions are not supported in Beta 1.0."
            )

        # 既存の警告を追加
        line_warnings.extend(validate_plain_math(text))

        for warning in line_warnings:
            warning_info = create_warning_info(line_number, warning, text)
            warnings.append(warning_info.to_text())
            severity_counts[warning_info.severity] = (
                severity_counts.get(warning_info.severity, 0) + 1
            )

        latex_lines.append(plain_to_latex(text))

    return latex_lines, warnings, severity_counts


# ============================================================
# 6. HTML Report Engine
# ============================================================

def build_html_head() -> list[str]:
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append("<html>")
    lines.append("<head>")
    lines.append('<meta charset="utf-8">')
    lines.append("<title>UTCE MathConvert Highlight Report</title>")
    lines.append("<style>")
    lines.append("body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin:24px; }")
    lines.append("h1 { font-size:24px; }")
    lines.append(".ok { background:#e8f5e9; padding:6px; margin:4px 0; }")
    lines.append(".error { background:#ffe6e6; border-left:4px solid #cc0000; padding:6px; margin:4px 0; }")
    lines.append(".warning { background:#fff8d6; border-left:4px solid #e6b800; padding:6px; margin:4px 0; }")
    lines.append(".info { background:#eef7ff; border-left:4px solid #3399ff; padding:6px; margin:4px 0; }")
    lines.append(".risk-low { background:#e8f5e9; border-left:4px solid #2e7d32; padding:6px; margin:4px 0; }")
    lines.append(".risk-moderate { background:#fff8d6; border-left:4px solid #e6b800; padding:6px; margin:4px 0; }")
    lines.append(".risk-high { background:#ffe6e6; border-left:4px solid #cc0000; padding:6px; margin:4px 0; }")
    lines.append(".recommendation { background:#f5f5f5; border-left:4px solid #555; padding:6px; margin:4px 0; }")
    lines.append(".summary { background:#f5f5f5; padding:12px; margin:12px 0; border-radius:6px; }")
    lines.append(".summary div { margin:4px 0; }")
    lines.append(".line { font-family:monospace; }")
    lines.append(".latex { color:#333; font-family:monospace; }")
    lines.append(".lineno { color:#777; display:inline-block; width:48px; }")
    lines.append(".suggestion { margin-top:6px; padding:6px; background:#eef7ff; border-left:4px solid #3399ff; }")
    lines.append(".suggestion-label { font-weight:bold; }")
    lines.append("button { margin-right:4px; padding:3px 8px; }")
    lines.append("</style>")
    lines.append("</head>")
    lines.append("<body>")
    return lines


def build_summary_section(lines, latex_lines, warnings, severity_counts) -> list[str]:
    diagnosis = build_diagnosis_from_severity_counts(severity_counts)
    risk_level = diagnosis.risk_level()
    risk_class = get_risk_class(risk_level)

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

    html_lines.append("<div><strong>Diagnostic Summary:</strong></div>")
    html_lines.append(f"<div>Confidence: {diagnosis.confidence_score:.1f}</div>")
    html_lines.append(f"<div>Predictive Risk: {diagnosis.predictive_risk:.1f}</div>")
    html_lines.append(
        f'<div class="{risk_class}"><strong>Risk Level:</strong> {risk_level}</div>'
    )
    html_lines.append(
        f'<div class="recommendation"><strong>Recommendation:</strong> {diagnosis.recommendation()}</div>'
    )

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


def build_warning_controls() -> list[str]:
    return [
        "<h2>Warnings</h2>",
        '<div style="margin:12px 0;">',
        '<button data-filter="all">All</button>',
        '<button data-filter="error">Error</button>',
        '<button data-filter="warning">Warning</button>',
        '<button data-filter="info">Info</button>',
        "</div>",
        '<div style="margin:8px 0 12px 0;">',
        '<input id="warningSearch" type="text" placeholder="Search warnings..." style="padding:6px; width:240px;">',
        "</div>",
    ]


def build_warning_section(warnings: list[str]) -> list[str]:
    html_lines = []

    if not warnings:
        html_lines.append('<div class="ok">No warnings.</div>')
        return html_lines

    for index, warning in enumerate(warnings, start=1):
        severity = classify_warning(warning)
        css_class = severity.lower()
        escaped = html.escape(warning)
        suggestion = ""

        if "| Suggestion:" in warning:
            main, suggestion = warning.split("| Suggestion:", 1)
            escaped_main = html.escape(main.strip())
            escaped_suggestion = html.escape(suggestion.strip())
        else:
            escaped_main = escaped
            escaped_suggestion = ""

        html_lines.append(
            f'<div class="{css_class}" data-severity="{css_class}">'
            f'<span class="lineno">{index}</span> {escaped_main}'
            f"</div>"
        )

        if escaped_suggestion:
            html_lines.append(
                f'<div class="suggestion">'
                f'<span class="suggestion-label">Suggested Fix:</span> {escaped_suggestion}'
                f"</div>"
            )

    return html_lines


def build_latex_section(latex: str) -> list[str]:
    html_lines = []
    html_lines.append("<h2>LaTeX Output</h2>")
    html_lines.append('<pre class="latex">')
    html_lines.append(html.escape(latex))
    html_lines.append("</pre>")
    return html_lines


def build_html_script() -> list[str]:
    return [
        "<script>",
        "const buttons = document.querySelectorAll('button[data-filter]');",
        "const search = document.getElementById('warningSearch');",
        "function applyFilters(){",
        "  const active = document.querySelector('button.active');",
        "  const filter = active ? active.dataset.filter : 'all';",
        "  const q = search ? search.value.toLowerCase() : '';",
        "  document.querySelectorAll('[data-severity]').forEach(el => {",
        "    const sev = el.dataset.severity;",
        "    const text = el.textContent.toLowerCase();",
        "    const showByFilter = filter === 'all' || sev === filter;",
        "    const showBySearch = !q || text.includes(q);",
        "    el.style.display = (showByFilter && showBySearch) ? '' : 'none';",
        "  });",
        "}",
        "buttons.forEach(btn => btn.addEventListener('click', () => {",
        "  buttons.forEach(b => b.classList.remove('active'));",
        "  btn.classList.add('active');",
        "  applyFilters();",
        "}));",
        "if (search) search.addEventListener('input', applyFilters);",
        "</script>",
    ]


def build_html_report(
    lines,
    latex_lines,
    warnings,
    severity_counts,
    latex,
    html_report_file,
):
    html_lines = []
    html_lines.extend(build_html_head())
    html_lines.append("<h1>UTCE MathConvert Highlight Report</h1>")
    html_lines.extend(build_summary_section(lines, latex_lines, warnings, severity_counts))
    html_lines.extend(build_warning_controls())
    html_lines.extend(build_warning_section(warnings))
    html_lines.extend(build_latex_section(latex))
    html_lines.extend(build_html_script())
    html_lines.append("</body>")
    html_lines.append("</html>")

    with open(html_report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(html_lines))


# ============================================================
# 7. CLI / Main
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(description="UTCE MathConvert")
    parser.add_argument("input_file", nargs="?", default="test_input.txt")
    parser.add_argument("output_file", nargs="?", default="output_latex.txt")
    parser.add_argument("--mode", choices=["inline", "block"], default="inline")
    parser.add_argument("--inline", action="store_true")
    parser.add_argument("--block", action="store_true")
    parser.add_argument("--warnings-file", default="output_warnings.txt")
    parser.add_argument("--html-report", default="highlight_report.html")
    parser.add_argument("--copy", action="store_true")
    parser.add_argument("--version", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.version:
        print("UTCE MathConvert v6.6-full-refactor-template")
        return

    input_file = args.input_file
    output_file = args.output_file
    warnings_file = args.warnings_file
    html_report_file = args.html_report

    mode = args.mode
    if args.inline:
        mode = "inline"
    if args.block:
        mode = "block"

    if not os.path.exists(input_file):
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

    build_html_report(
        lines=lines,
        latex_lines=latex_lines,
        warnings=warnings,
        severity_counts=severity_counts,
        latex=latex,
        html_report_file=html_report_file,
    )

    print(f"HTML report saved to: {html_report_file}")

    if args.copy:
        subprocess.run("pbcopy", text=True, input=latex)
        print("Output copied to clipboard.")


if __name__ == "__main__":
    main()