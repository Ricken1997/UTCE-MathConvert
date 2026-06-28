#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UTCE MathConvert Core
v2.0 Product Beta

Role:
- Build LaTeX preview output.
- Provide lightweight diagnostics.
- Avoid false warnings for concatenated expressions.
- Keep GUI-side logic simple.
"""

from dataclasses import dataclass


SUPPORTED_FUNCTIONS = {
    "frac": 2,
    "sqrt": 1,
    "pow": 2,
    "sup": 2,
    "sub": 2,
    "subsup": 3,
    "sum": 4,
    "prod": 4,
    "int": 4,
    "lim": 3,
    "matrix": None,
    "cases": None,
    "align": None,
}


GREEK_LATEX = {
    "alpha": "\\alpha",
    "beta": "\\beta",
    "gamma": "\\gamma",
    "delta": "\\delta",
    "epsilon": "\\epsilon",
    "theta": "\\theta",
    "lambda": "\\lambda",
    "mu": "\\mu",
    "pi": "\\pi",
    "sigma": "\\sigma",
    "omega": "\\omega",
    "Delta": "\\Delta",
    "Theta": "\\Theta",
    "Lambda": "\\Lambda",
    "Pi": "\\Pi",
    "Sigma": "\\Sigma",
    "Omega": "\\Omega",
}


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
    warning_text: str = ""


def find_matching_paren(text: str, open_index: int) -> int:
    depth = 0

    for i in range(open_index, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i

    return -1


def split_args(text: str) -> list[str]:
    parts = []
    buf = ""
    depth = 0

    for ch in text:
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


def merge_logical_lines(lines: list[str]) -> list[str]:
    merged = []
    buf = ""
    depth = 0

    for line in lines:
        text = line.strip()
        if not text:
            continue

        if buf:
            buf += text
        else:
            buf = text

        for ch in text:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1

        if depth <= 0:
            merged.append(buf)
            buf = ""
            depth = 0

    if buf:
        merged.append(buf)

    return merged


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


def split_top_level_expressions(text: str) -> list[str]:
    text = text.strip()
    parts = []
    i = 0

    while i < len(text):
        while i < len(text) and text[i].isspace():
            i += 1

        start = i

        while i < len(text) and (
            text[i].isalpha() or text[i] == "_" or text[i] == "\\"
        ):
            i += 1

        if i < len(text) and text[i] == "(":
            end = find_matching_paren(text, i)
            if end != -1:
                parts.append(text[start:end + 1].strip())
                i = end + 1
                continue

        if start < len(text):
            parts.append(text[start:].strip())
        break

    return [p for p in parts if p]


def parse_function(expr: str):
    expr = expr.strip()

    name_end = 0
    while name_end < len(expr) and (
        expr[name_end].isalpha() or expr[name_end] == "_" or expr[name_end] == "\\"
    ):
        name_end += 1

    if name_end == 0:
        return None

    name = expr[:name_end].lstrip("\\")

    if name_end >= len(expr) or expr[name_end] != "(":
        return None

    close_index = find_matching_paren(expr, name_end)

    if close_index != len(expr) - 1:
        return None

    inside = expr[name_end + 1:close_index].strip()
    return name, split_args(inside)


def normalize_symbol(text: str) -> str:
    text = text.strip().lstrip("\\")
    return GREEK_LATEX.get(text, text)


def plain_to_latex(expr: str) -> str:
    expr = expr.strip()

    if not expr:
        return ""

    parts = split_top_level_expressions(expr)
    if len(parts) > 1:
        return "".join(plain_to_latex(part) for part in parts)

    parsed = parse_function(expr)

    if not parsed:
        return normalize_symbol(expr)

    name, args = parsed

    if name == "frac" and len(args) == 2:
        return f"\\frac{{{plain_to_latex(args[0])}}}{{{plain_to_latex(args[1])}}}"

    if name == "sqrt" and len(args) == 1:
        return f"\\sqrt{{{plain_to_latex(args[0])}}}"

    if name in ("pow", "sup") and len(args) == 2:
        return f"{plain_to_latex(args[0])}^{{{plain_to_latex(args[1])}}}"

    if name == "sub" and len(args) == 2:
        return f"{plain_to_latex(args[0])}_{{{plain_to_latex(args[1])}}}"

    if name == "subsup" and len(args) == 3:
        return f"{plain_to_latex(args[0])}_{{{plain_to_latex(args[1])}}}^{{{plain_to_latex(args[2])}}}"

    if name == "sum" and len(args) == 4:
        return f"\\sum_{{{args[0]}={plain_to_latex(args[1])}}}^{{{plain_to_latex(args[2])}}} {plain_to_latex(args[3])}"

    if name == "prod" and len(args) == 4:
        return f"\\prod_{{{args[0]}={plain_to_latex(args[1])}}}^{{{plain_to_latex(args[2])}}} {plain_to_latex(args[3])}"

    if name == "int" and len(args) == 4:
        return f"\\int_{{{plain_to_latex(args[1])}}}^{{{plain_to_latex(args[2])}}} {plain_to_latex(args[3])}\\, d{args[0]}"

    if name == "lim" and len(args) == 3:
        return f"\\lim_{{{args[0]}\\to {plain_to_latex(args[1])}}} {plain_to_latex(args[2])}"

    if name == "matrix" and len(args) >= 1:
        rows = split_rows(",".join(args))
        latex_rows = []
        for row in rows:
            cells = split_args(row)
            latex_rows.append(" & ".join(plain_to_latex(cell) for cell in cells))
        return "\\begin{matrix}" + r" \\ ".join(latex_rows) + "\\end{matrix}"

    if name == "cases" and len(args) >= 1:
        rows = split_rows(",".join(args))
        latex_rows = []
        for row in rows:
            cells = split_args(row)
            latex_rows.append(" & ".join(plain_to_latex(cell) for cell in cells))
        return "\\begin{cases}" + r" \\ ".join(latex_rows) + "\\end{cases}"

    if name == "align" and len(args) >= 1:
        rows = split_rows(",".join(args))
        latex_rows = []
        for row in rows:
            cells = split_args(row)
            latex_rows.append(" & ".join(plain_to_latex(cell) for cell in cells))
        return "\\begin{aligned}" + r" \\ ".join(latex_rows) + "\\end{aligned}"

    return expr


def build_latex_output(lines: list[str], output_mode: str = "inline") -> str:
    converted = [plain_to_latex(line) for line in lines if line.strip()]

    if output_mode == "block":
        return "\n".join(f"\\[{line}\\]" for line in converted)

    return "\n".join(f"${line}$" for line in converted)


def validate_expression(expr: str) -> list[str]:
    warnings = []

    if expr.count("(") != expr.count(")"):
        warnings.append("Parentheses are not balanced.")

    return warnings


def analyze_lines(lines: list[str]):
    lines = merge_logical_lines(lines)
    
    latex_lines = []
    warnings = []
    severity_counts = {}

    for line_number, line in enumerate(lines, start=1):
        text = line.strip()

        if not text:
            continue

        for message in validate_expression(text):
            info = WarningInfo(
                line_number=line_number,
                message=message,
                text=text,
                severity="WARNING",
            )
            warnings.append(info.to_text())
            severity_counts["WARNING"] = severity_counts.get("WARNING", 0) + 1

        latex_lines.append(plain_to_latex(text))

    return latex_lines, warnings, severity_counts


def build_diagnosis_from_severity_counts(severity_counts: dict) -> Diagnosis:
    total = sum(severity_counts.values())

    if total == 0:
        return Diagnosis(
            confidence_score=99.0,
            predictive_risk=1.0,
            risk_level="MINIMAL",
            warning_text="",
        )

    confidence = max(70.0, 99.0 - total * 5.0)
    risk = min(30.0, 1.0 + total * 5.0)

    if total <= 1:
        level = "LOW"
    elif total <= 3:
        level = "MEDIUM"
    else:
        level = "HIGH"

    warning_text = "\n".join(
        f"{key}: {value}" for key, value in severity_counts.items()
    )

    return Diagnosis(
        confidence_score=confidence,
        predictive_risk=risk,
        risk_level=level,
        warning_text=warning_text,
    )