#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UTCE MathConvert
v2.0 Product Beta Free - OMML Converter

Purpose:
- Convert unified plain-math syntax into Microsoft Word OMML.
- Support recursive expressions.
- Support multi-line align / cases / matrix.
- Avoid breaking on long beta-test formulas.

Supported:
frac, sqrt, pow, sup, sub, subsup,
sum, prod, int, lim,
matrix, cases, align,
Greek symbols,
basic operators.
"""

from __future__ import annotations

import html


# ============================================================
# Symbol Maps
# ============================================================

GREEK_MAP = {
    "alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ",
    "epsilon": "ε", "zeta": "ζ", "eta": "η", "theta": "θ",
    "iota": "ι", "kappa": "κ", "lambda": "λ", "mu": "μ",
    "nu": "ν", "xi": "ξ", "pi": "π", "rho": "ρ",
    "sigma": "σ", "tau": "τ", "upsilon": "υ", "phi": "φ",
    "chi": "χ", "psi": "ψ", "omega": "ω",
    "Delta": "Δ", "Theta": "Θ", "Lambda": "Λ", "Xi": "Ξ",
    "Pi": "Π", "Sigma": "Σ", "Phi": "Φ", "Psi": "Ψ", "Omega": "Ω",
    "inf": "∞",
}

OPERATOR_MAP = {
    "+": "+",
    "-": "−",
    "*": "×",
    "/": "÷",
    "=": "=",
    ">": ">",
    "<": "<",
}


# ============================================================
# XML / OMML Helpers
# ============================================================

def escape_xml(text: str) -> str:
    return html.escape(str(text), quote=False)


def normalize_symbol(text: str) -> str:
    text = text.strip()

    if text.startswith("\\"):
        text = text[1:]

    return GREEK_MAP.get(text, text)


def omml_text(text: str) -> str:
    return (
        "<m:r>"
        "<m:t>"
        + escape_xml(normalize_symbol(text))
        + "</m:t>"
        "</m:r>"
    )


def omml_para(inner: str) -> str:
    return (
        "<m:oMathPara>"
        "<m:oMath>"
        + inner
        + "</m:oMath>"
        "</m:oMathPara>"
    )


def omml_group(inner: str) -> str:
    return inner


# ============================================================
# Depth-aware Parser Utilities
# ============================================================

def paren_delta(text: str) -> int:
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
    return depth


def merge_logical_lines(lines: list[str]) -> list[str]:
    """
    Merge multiline structures such as:

    align(
      ...
    )

    into one logical expression.
    """
    merged: list[str] = []
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

        depth += paren_delta(text)

        if depth <= 0:
            merged.append(buf)
            buf = ""
            depth = 0

    if buf:
        merged.append(buf)

    return merged


def normalize_multiline_functions(lines: list[str]) -> list[str]:
    normalized = []

    for line in lines:
        text = line.strip()

        # remove line breaks and extra spaces created by multiline input
        text = text.replace("\n", "")
        text = text.replace("\r", "")
        text = text.strip()

        normalized.append(text)

    return normalized


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


def split_top_level(text: str, delimiter: str) -> list[str]:
    parts: list[str] = []
    buf = ""
    depth = 0

    for ch in text:
        if ch == "(":
            depth += 1
            buf += ch
        elif ch == ")":
            depth -= 1
            buf += ch
        elif ch == delimiter and depth == 0:
            parts.append(buf.strip())
            buf = ""
        else:
            buf += ch

    if buf.strip():
        parts.append(buf.strip())

    return parts


def split_args(text: str) -> list[str]:
    return split_top_level(text, ",")


def split_rows(text: str) -> list[str]:
    return split_top_level(text, ";")


def parse_function(expr: str) -> tuple[str, list[str]] | None:
    expr = expr.strip()

    if not expr:
        return None

    name_end = 0
    while name_end < len(expr) and (
        expr[name_end].isalpha()
        or expr[name_end] == "_"
        or expr[name_end] == "\\"
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


def split_concatenated_functions(expr: str) -> list[str]:
    """
    Split expressions like:
    frac(a,b)sqrt(c)pow(x,2)

    into:
    [frac(a,b), sqrt(c), pow(x,2)]

    If no safe split is possible, return [expr].
    """
    expr = expr.strip()
    parts: list[str] = []
    i = 0

    while i < len(expr):
        while i < len(expr) and expr[i].isspace():
            i += 1

        start = i

        while i < len(expr) and (
            expr[i].isalpha() or expr[i] == "_" or expr[i] == "\\"
        ):
            i += 1

        if i < len(expr) and expr[i] == "(":
            end = find_matching_paren(expr, i)
            if end != -1:
                parts.append(expr[start:end + 1].strip())
                i = end + 1
                continue

        if start < len(expr):
            if parts:
                parts.append(expr[start:].strip())
                return [p for p in parts if p]
            return [expr]

    return [p for p in parts if p] or [expr]


def split_by_top_level_operators(expr: str) -> list[str] | None:
    """
    Split top-level operators without touching nested function arguments.
    """
    depth = 0
    parts: list[str] = []
    buf = ""

    i = 0
    while i < len(expr):
        ch = expr[i]

        if ch == "(":
            depth += 1
            buf += ch
        elif ch == ")":
            depth -= 1
            buf += ch
        elif depth == 0 and ch in ["+", "-", "*", "=", ">", "<"]:
            if buf.strip():
                parts.append(buf.strip())
            parts.append(ch)
            buf = ""
        else:
            buf += ch

        i += 1

    if buf.strip():
        parts.append(buf.strip())

    if len(parts) >= 3:
        return parts

    return None


# ============================================================
# OMML Builders
# ============================================================

def omml_fraction(num: str, den: str) -> str:
    return (
        "<m:f>"
        "<m:num>" + num + "</m:num>"
        "<m:den>" + den + "</m:den>"
        "</m:f>"
    )


def omml_sqrt(body: str) -> str:
    return (
        "<m:rad>"
        "<m:radPr><m:degHide m:val=\"1\"/></m:radPr>"
        "<m:deg/>"
        "<m:e>" + body + "</m:e>"
        "</m:rad>"
    )


def omml_sup(base: str, sup: str) -> str:
    return (
        "<m:sSup>"
        "<m:e>" + base + "</m:e>"
        "<m:sup>" + sup + "</m:sup>"
        "</m:sSup>"
    )


def omml_sub(base: str, sub: str) -> str:
    return (
        "<m:sSub>"
        "<m:e>" + base + "</m:e>"
        "<m:sub>" + sub + "</m:sub>"
        "</m:sSub>"
    )


def omml_subsup(base: str, sub: str, sup: str) -> str:
    return (
        "<m:sSubSup>"
        "<m:e>" + base + "</m:e>"
        "<m:sub>" + sub + "</m:sub>"
        "<m:sup>" + sup + "</m:sup>"
        "</m:sSubSup>"
    )


def omml_nary(symbol: str, index: str, lower: str, upper: str, body: str) -> str:
    sub_xml = omml_text(index) + omml_text("=") + lower

    return (
        "<m:nary>"
        "<m:naryPr>"
        f"<m:chr m:val=\"{symbol}\"/>"
        "<m:limLoc m:val=\"undOvr\"/>"
        "</m:naryPr>"
        "<m:sub>" + sub_xml + "</m:sub>"
        "<m:sup>" + upper + "</m:sup>"
        "<m:e>" + body + "</m:e>"
        "</m:nary>"
    )


def omml_integral(variable: str, lower: str, upper: str, body: str) -> str:
    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∫\"/>"
        "<m:limLoc m:val=\"subSup\"/>"
        "</m:naryPr>"
        "<m:sub>" + lower + "</m:sub>"
        "<m:sup>" + upper + "</m:sup>"
        "<m:e>"
        + body
        + omml_text(" d")
        + omml_text(variable)
        + "</m:e>"
        "</m:nary>"
    )


def omml_limit(variable: str, target: str, body: str) -> str:
    return (
        omml_sub(
            omml_text("lim"),
            omml_text(variable) + omml_text("→") + target
        )
        + body
    )


def omml_matrix_from_rows(rows: list[list[str]]) -> str:
    row_xml = ""

    for row in rows:
        cell_xml = ""
        for cell in row:
            cell_xml += "<m:e>" + cell + "</m:e>"
        row_xml += "<m:mr>" + cell_xml + "</m:mr>"

    return (
        "<m:m>"
        "<m:mPr>"
        "<m:baseJc m:val=\"centerGroup\"/>"
        "</m:mPr>"
        + row_xml
        + "</m:m>"
    )


def omml_cases_from_rows(rows: list[list[str]]) -> str:
    matrix = omml_matrix_from_rows(rows)

    return (
        "<m:d>"
        "<m:dPr>"
        "<m:begChr m:val=\"{\"/>"
        "<m:endChr m:val=\"\"/>"
        "</m:dPr>"
        "<m:e>" + matrix + "</m:e>"
        "</m:d>"
    )


# ============================================================
# Structure Parsers
# ============================================================

def parse_rows_to_omml_cells(text: str) -> list[list[str]]:
    rows = split_rows(text)
    result: list[list[str]] = []

    for row in rows:
        cells = split_args(row)
        result.append([to_inner_omml(cell) for cell in cells])

    return result


def convert_function_to_omml(name: str, args: list[str]) -> str | None:
    name = name.strip().lstrip("\\")

    if name == "frac" and len(args) == 2:
        return omml_fraction(to_inner_omml(args[0]), to_inner_omml(args[1]))

    if name == "sqrt" and len(args) == 1:
        return omml_sqrt(to_inner_omml(args[0]))

    if name in ("pow", "sup") and len(args) == 2:
        return omml_sup(to_inner_omml(args[0]), to_inner_omml(args[1]))

    if name == "sub" and len(args) == 2:
        return omml_sub(to_inner_omml(args[0]), to_inner_omml(args[1]))

    if name == "subsup" and len(args) == 3:
        return omml_subsup(
            to_inner_omml(args[0]),
            to_inner_omml(args[1]),
            to_inner_omml(args[2]),
        )

    if name == "sum" and len(args) == 4:
        return omml_nary(
            "∑",
            args[0],
            to_inner_omml(args[1]),
            to_inner_omml(args[2]),
            to_inner_omml(args[3]),
        )

    if name == "prod" and len(args) == 4:
        return omml_nary(
            "∏",
            args[0],
            to_inner_omml(args[1]),
            to_inner_omml(args[2]),
            to_inner_omml(args[3]),
        )

    if name == "int" and len(args) == 4:
        return omml_integral(
            args[0],
            to_inner_omml(args[1]),
            to_inner_omml(args[2]),
            to_inner_omml(args[3]),
        )

    if name == "lim" and len(args) == 3:
        return omml_limit(
            args[0],
            to_inner_omml(args[1]),
            to_inner_omml(args[2]),
        )

    if name == "matrix" and len(args) >= 1:
        text = ",".join(args)
        rows = parse_rows_to_omml_cells(text)
        return omml_matrix_from_rows(rows)

    if name == "cases" and len(args) >= 1:
        text = ",".join(args)
        rows = parse_rows_to_omml_cells(text)
        return omml_cases_from_rows(rows)

    if name == "align" and len(args) >= 1:
        text = ",".join(args)
        rows = parse_rows_to_omml_cells(text)
        return omml_matrix_from_rows(rows)

    return None


# ============================================================
# Recursive Conversion
# ============================================================

def to_inner_omml(expr: str) -> str:
    expr = expr.strip()

    if not expr:
        return ""

    # remove redundant outside whitespace
    expr = expr.strip()

    # top-level operator handling
    op_parts = split_by_top_level_operators(expr)
    if op_parts:
        out = ""
        for part in op_parts:
            if part in OPERATOR_MAP:
                out += omml_text(OPERATOR_MAP[part])
            else:
                out += to_inner_omml(part)
        return out

    # concatenated functions
    concat_parts = split_concatenated_functions(expr)
    if len(concat_parts) > 1:
        return "".join(to_inner_omml(part) for part in concat_parts)

    # function
    parsed = parse_function(expr)
    if parsed:
        name, args = parsed
        converted = convert_function_to_omml(name, args)
        if converted is not None:
            return converted

    # fallback
    return omml_text(expr)


# ============================================================
# Public API
# ============================================================

def plain_to_omml(expr: str) -> str:
    return omml_para(to_inner_omml(expr))


def convert_lines_to_omml(lines: list[str]) -> list[str]:
    logical_lines = merge_logical_lines(lines)
    logical_lines = normalize_multiline_functions(logical_lines)

    return [
        plain_to_omml(line)
        for line in logical_lines
        if line.strip()
    ]