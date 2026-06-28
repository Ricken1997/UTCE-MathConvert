#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
UTCE MathConvert OMML Converter
v2.0 Full Core Candidate

Supported:
- frac
- sqrt
- pow / sup
- sub
- subsup
- sum
- prod
- int
- lim
- matrix
- cases
- align
- Greek symbols
"""

import html


GREEK_MAP = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "epsilon": "ε",
    "theta": "θ",
    "lambda": "λ",
    "mu": "μ",
    "pi": "π",
    "sigma": "σ",
    "omega": "ω",
    "Delta": "Δ",
    "Theta": "Θ",
    "Lambda": "Λ",
    "Pi": "Π",
    "Sigma": "Σ",
    "Omega": "Ω",
}


def escape_xml(text: str) -> str:
    return html.escape(str(text), quote=False)


def omml_text(text: str) -> str:
    text = GREEK_MAP.get(text, text)
    return (
        "<m:r>"
        "<m:t>"
        + escape_xml(text)
        + "</m:t>"
        "</m:r>"
    )


def omml_para(body: str) -> str:
    return (
        "<m:oMathPara>"
        "<m:oMath>"
        + body +
        "</m:oMath>"
        "</m:oMathPara>"
    )


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


def split_top_level_expressions(text: str) -> list[str]:
    text = text.strip()
    parts = []
    i = 0

    while i < len(text):
        while i < len(text) and text[i].isspace():
            i += 1

        start = i

        while i < len(text) and (text[i].isalpha() or text[i] == "_"):
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
    while name_end < len(expr) and (expr[name_end].isalpha() or expr[name_end] == "_"):
        name_end += 1

    if name_end == 0:
        return None

    name = expr[:name_end]

    if name_end >= len(expr) or expr[name_end] != "(":
        return None

    close_index = find_matching_paren(expr, name_end)

    if close_index != len(expr) - 1:
        return None

    inside = expr[name_end + 1:close_index].strip()
    return name, split_args(inside)


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
        "<m:deg></m:deg>"
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
    sub = omml_text(index + "=") + lower

    return (
        "<m:nary>"
        "<m:naryPr>"
        f"<m:chr m:val=\"{symbol}\"/>"
        "<m:limLoc m:val=\"undOvr\"/>"
        "</m:naryPr>"
        "<m:sub>" + sub + "</m:sub>"
        "<m:sup>" + upper + "</m:sup>"
        "<m:e>" + body + "</m:e>"
        "</m:nary>"
    )


def omml_sum(index: str, lower: str, upper: str, body: str) -> str:
    return omml_nary("∑", index, lower, upper, body)


def omml_prod(index: str, lower: str, upper: str, body: str) -> str:
    return omml_nary("∏", index, lower, upper, body)


def omml_integral(variable: str, lower: str, upper: str, body: str) -> str:
    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∫\"/>"
        "<m:limLoc m:val=\"subSup\"/>"
        "</m:naryPr>"
        "<m:sub>" + lower + "</m:sub>"
        "<m:sup>" + upper + "</m:sup>"
        "<m:e>" + body + omml_text(" d") + omml_text(variable) + "</m:e>"
        "</m:nary>"
    )


def omml_limit(variable: str, target: str, body: str) -> str:
    lim_text = omml_text("lim")
    sub_text = omml_text(variable + "→") + target
    return omml_sub(lim_text, sub_text) + body


def omml_matrix_cells(rows: list[list[str]]) -> str:
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
        + row_xml +
        "</m:m>"
    )


def parse_matrix_cells(matrix_text: str) -> list[list[str]]:
    rows = split_rows(matrix_text)
    return [split_args(row) for row in rows]


def omml_matrix(matrix_text: str) -> str:
    rows = parse_matrix_cells(matrix_text)

    omml_rows = []
    for row in rows:
        omml_rows.append([to_inner_omml(cell) for cell in row])

    return omml_matrix_cells(omml_rows)


def omml_cases(matrix_text: str) -> str:
    matrix_body = omml_matrix(matrix_text)

    return (
        "<m:d>"
        "<m:dPr>"
        "<m:begChr m:val=\"{\"/>"
        "<m:endChr m:val=\"\"/>"
        "</m:dPr>"
        "<m:e>" + matrix_body + "</m:e>"
        "</m:d>"
    )


def omml_align(matrix_text: str) -> str:
    return omml_matrix(matrix_text)


def args_to_omml(args: list[str]) -> list[str]:
    return [to_inner_omml(arg) for arg in args]


def convert_function_to_omml(name: str, args: list[str]) -> str | None:
    if name == "frac" and len(args) == 2:
        a = args_to_omml(args)
        return omml_fraction(a[0], a[1])

    if name == "sqrt" and len(args) == 1:
        a = args_to_omml(args)
        return omml_sqrt(a[0])

    if name in ("pow", "sup") and len(args) == 2:
        a = args_to_omml(args)
        return omml_sup(a[0], a[1])

    if name == "sub" and len(args) == 2:
        a = args_to_omml(args)
        return omml_sub(a[0], a[1])

    if name == "subsup" and len(args) == 3:
        a = args_to_omml(args)
        return omml_subsup(a[0], a[1], a[2])

    if name == "sum" and len(args) == 4:
        a = args_to_omml(args)
        return omml_sum(args[0], a[1], a[2], a[3])

    if name == "prod" and len(args) == 4:
        a = args_to_omml(args)
        return omml_prod(args[0], a[1], a[2], a[3])

    if name == "int" and len(args) == 4:
        a = args_to_omml(args)
        return omml_integral(args[0], a[1], a[2], a[3])

    if name == "lim" and len(args) == 3:
        a = args_to_omml(args)
        return omml_limit(args[0], a[1], a[2])

    if name == "matrix" and len(args) >= 1:
        return omml_matrix(",".join(args))

    if name == "cases" and len(args) >= 1:
        return omml_cases(",".join(args))

    if name == "align" and len(args) >= 1:
        return omml_align(",".join(args))

    return None


def to_inner_omml(expr: str) -> str:
    expr = expr.strip()

    multi_parts = split_top_level_expressions(expr)

    if len(multi_parts) > 1:
        return "".join(to_inner_omml(part) for part in multi_parts)

    parsed = parse_function(expr)

    if not parsed:
        return omml_text(expr)

    name, args = parsed
    converted = convert_function_to_omml(name, args)

    if converted is not None:
        return converted

    return omml_text(expr)


def plain_to_omml(expr: str) -> str:
    return omml_para(to_inner_omml(expr))


def convert_lines_to_omml(lines: list[str]) -> list[str]:
    return [plain_to_omml(line) for line in lines if line.strip()]