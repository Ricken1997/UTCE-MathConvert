#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UTCE MathConvert Core
v2.0 RC Diagnostic / LaTeX Support Layer

Role:
- Validate plain math input lightly.
- Generate LaTeX preview text.
- Provide structural diagnosis summary.
- Do NOT block recursive OMML conversion.
"""

from dataclasses import dataclass
import html


@dataclass
class WarningInfo:
    line_number: int
    message: str
    text: str
    severity: str = "INFO"

    def to_text(self) -> str:
        return f"[{self.severity}] Line {self.line_number}: {self.message}"


@dataclass
class Diagnosis:
    confidence_score: float
    predictive_risk: float
    risk_level: str
    warning_text: str


# ============================================================
# LaTeX Builder
# ============================================================

def split_args(s: str) -> list[str]:
    parts = []
    buf = ""
    depth = 0

    for ch in s:
        if ch == "(":
            depth += 1
            buf += ch
        elif ch == ")":
            depth -= 1
            buf += ch
        elif ch == "," and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch

    if buf.strip():
        parts.append(buf.strip())

    return parts


def split_rows(text: str) -> list[str]:
    rows = []
    buf = ""
    depth = 0

    for ch in text:
        if ch == "(":
            depth += 1
            buf += ch
        elif ch == ")":
            depth -= 1
            buf += ch
        elif ch == ";" and depth == 0:
            rows.append(buf.strip())
            buf = ""
        else:
            buf += ch

    if buf.strip():
        rows.append(buf.strip())

    return rows


def parse_function(expr: str):
    expr = expr.strip()

    if "(" not in expr or not expr.endswith(")"):
        return None

    idx = expr.find("(")
    name = expr[:idx].strip()
    inside = expr[idx + 1:-1].strip()

    if not name:
        return None

    return name, split_args(inside)


def plain_to_latex(expr: str) -> str:
    expr = expr.strip()
    parsed = parse_function(expr)

    if not parsed:
        return expr

    name, args = parsed
    a = [plain_to_latex(x) for x in args]

    if name == "frac" and len(a) == 2:
        return rf"\frac{{{a[0]}}}{{{a[1]}}}"

    if name == "sqrt" and len(a) == 1:
        return rf"\sqrt{{{a[0]}}}"

    if name in ("pow", "sup") and len(a) == 2:
        return rf"{a[0]}^{{{a[1]}}}"

    if name == "sub" and len(a) == 2:
        return rf"{a[0]}_{{{a[1]}}}"

    if name == "sum" and len(a) == 4:
        return rf"\sum_{{{a[0]}={a[1]}}}^{{{a[2]}}} {a[3]}"

    if name == "prod" and len(a) == 4:
        return rf"\prod_{{{a[0]}={a[1]}}}^{{{a[2]}}} {a[3]}"

    if name == "int" and len(a) == 4:
        return rf"\int_{{{a[1]}}}^{{{a[2]}}} {a[3]} \, d{a[0]}"

    if name == "lim" and len(a) == 3:
        return rf"\lim_{{{a[0]}\to {a[1]}}} {a[2]}"

    if name == "matrix" and len(args) >= 1:
        matrix_text = ",".join(args)
        rows = split_rows(matrix_text)
        latex_rows = []

        for row in rows:
            cells = split_args(row)
            latex_rows.append(" & ".join(plain_to_latex(c) for c in cells))

        return r"\begin{matrix}" + r" \\ ".join(latex_rows) + r"\end{matrix}"

    return expr


def build_latex_output(lines: list[str], output_mode: str = "inline") -> str:
    converted = [plain_to_latex(line) for line in lines if line.strip()]

    if output_mode == "block":
        return "\n".join(f"\\[{line}\\]" for line in converted)

    return "\n".join(f"${line}$" for line in converted)


# ============================================================
# Validator
# ============================================================

def validate_plain_math(expr: str) -> list[str]:
    warnings = []
    expr = expr.strip()

    checks = {
        "frac": 2,
        "sqrt": 1,
        "sum": 4,
        "prod": 4,
        "int": 4,
        "lim": 3,
    }

    parsed = parse_function(expr)

    if not parsed:
        return warnings

    name, args = parsed

    if name in checks and len(args) != checks[name]:
        warnings.append(
            f"{name} requires {checks[name]} arguments, got {len(args)}."
        )

    if name == "matrix":
        matrix_text = ",".join(args)
        rows = split_rows(matrix_text)

        if len(rows) < 1:
            warnings.append("matrix requires at least 1 row.")

        row_lengths = [len(split_args(row)) for row in rows]

        if row_lengths and len(set(row_lengths)) > 1:
            warnings.append(
                "Matrix row lengths differ. Each row should have the same number of columns."
            )

    return warnings


# ============================================================
# Analysis Engine
# ============================================================

def analyze_lines(lines: list[str]):
    latex_lines = []
    warnings = []
    severity_counts = {}

    for line_number, line in enumerate(lines, start=1):
        text = line.strip()

        if not text:
            continue

        line_warnings = validate_plain_math(text)

        for warning in line_warnings:
            warning_info = WarningInfo(
                line_number=line_number,
                message=warning,
                text=text,
                severity="INFO",
            )
            warnings.append(warning_info.to_text())
            severity_counts["INFO"] = severity_counts.get("INFO", 0) + 1

        latex_lines.append(plain_to_latex(text))

    return latex_lines, warnings, severity_counts


def build_diagnosis_from_severity_counts(severity_counts: dict) -> Diagnosis:
    total = sum(severity_counts.values())

    if total == 0:
        confidence = 99.0
        risk = 1.0
        level = "MINIMAL"
        warning_text = ""
    else:
        confidence = max(70.0, 99.0 - total * 5)
        risk = min(30.0, total * 5.0)
        level = "LOW" if total <= 2 else "MEDIUM"
        warning_text = "\n".join(
            f"{key}: {value}" for key, value in severity_counts.items()
        )

    return Diagnosis(
        confidence_score=confidence,
        predictive_risk=risk,
        risk_level=level,
        warning_text=warning_text,
    )


# ============================================================
# HTML Report Support
# ============================================================

def escape_html(text: str) -> str:
    return html.escape(str(text), quote=True)