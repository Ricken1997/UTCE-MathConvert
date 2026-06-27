import html


# ============================================================
# UTCE MathConvert v2.0 RC
# OMML Converter Core
#
# Design:
# - Parser parses expressions.
# - Dispatcher routes functions.
# - Builder generates OMML.
# - Recursive conversion is handled through to_inner_omml().
# ============================================================


# ============================================================
# XML Utilities / Basic OMML Builders
# ============================================================

GREEK_MAP = {
    "alpha": "α",
    "beta": "β",
    "gamma": "γ",
    "delta": "δ",
    "theta": "θ",
    "lambda": "λ",
    "mu": "μ",
    "pi": "π",
    "sigma": "σ",
    "omega": "ω",
}


def escape_xml(text: str) -> str:
    return html.escape(str(text), quote=False)


def normalize_symbol(text: str) -> str:
    text = text.strip()
    return GREEK_MAP.get(text, text)


def omml_text(text: str) -> str:
    text = escape_xml(normalize_symbol(text))
    return (
        "<m:r>"
        "<m:t>"
        + text +
        "</m:t>"
        "</m:r>"
    )


def wrap_omml(inner: str) -> str:
    return (
        "<m:oMathPara>"
        "<m:oMath>"
        + inner +
        "</m:oMath>"
        "</m:oMathPara>"
    )


def strip_omml_wrapper(xml: str) -> str:
    xml = xml.strip()

    xml = xml.replace("<m:oMathPara>", "")
    xml = xml.replace("</m:oMathPara>", "")
    xml = xml.replace("<m:oMath>", "")
    xml = xml.replace("</m:oMath>", "")

    return xml.strip()


def omml_fraction(num: str, den: str) -> str:
    return (
        "<m:f>"
        "<m:num>" + num + "</m:num>"
        "<m:den>" + den + "</m:den>"
        "</m:f>"
    )


def omml_sqrt(value: str) -> str:
    return (
        "<m:rad>"
        "<m:radPr>"
        "<m:degHide m:val=\"1\"/>"
        "</m:radPr>"
        "<m:deg/>"
        "<m:e>" + value + "</m:e>"
        "</m:rad>"
    )


def omml_superscript(base: str, sup: str) -> str:
    return (
        "<m:sSup>"
        "<m:e>" + base + "</m:e>"
        "<m:sup>" + sup + "</m:sup>"
        "</m:sSup>"
    )


def omml_subscript(base: str, sub: str) -> str:
    return (
        "<m:sSub>"
        "<m:e>" + base + "</m:e>"
        "<m:sub>" + sub + "</m:sub>"
        "</m:sSub>"
    )


# ============================================================
# N-ary OMML Builders
# ============================================================

def omml_sum(index: str, start: str, end: str, body: str) -> str:
    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∑\"/>"
        "<m:limLoc m:val=\"undOvr\"/>"
        "</m:naryPr>"
        "<m:sub>"
        + index + omml_text("=") + start +
        "</m:sub>"
        "<m:sup>" + end + "</m:sup>"
        "<m:e>" + body + "</m:e>"
        "</m:nary>"
    )


def omml_prod(index: str, start: str, end: str, body: str) -> str:
    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∏\"/>"
        "<m:limLoc m:val=\"undOvr\"/>"
        "</m:naryPr>"
        "<m:sub>"
        + index + omml_text("=") + start +
        "</m:sub>"
        "<m:sup>" + end + "</m:sup>"
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
        + variable
        + "</m:e>"
        "</m:nary>"
    )


def omml_limit(variable: str, target: str, body: str) -> str:
    return (
        "<m:limLow>"
        "<m:e>" + omml_text("lim") + "</m:e>"
        "<m:lim>"
        + variable + omml_text("→") + target +
        "</m:lim>"
        "</m:limLow>"
        + body
    )


# ============================================================
# Matrix / Table OMML Builders
# ============================================================

def omml_matrix_cells(rows: list[list[str]]) -> str:
    row_xml = ""

    for row in rows:
        cell_xml = ""

        for cell in row:
            cell_xml += (
                "<m:e>"
                + cell
                + "</m:e>"
            )

        row_xml += (
            "<m:mr>"
            + cell_xml
            + "</m:mr>"
        )

    return (
        "<m:m>"
        "<m:mPr>"
        "<m:baseJc m:val=\"centerGroup\"/>"
        "</m:mPr>"
        + row_xml +
        "</m:m>"
    )


# ============================================================
# Parser Utilities
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


def parse_matrix_cells(text: str) -> list[list[str]]:
    rows = split_rows(text)
    return [split_args(row) for row in rows]


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


# ============================================================
# Recursive Conversion Helpers
# ============================================================

def to_inner_omml(expr: str) -> str:
    return strip_omml_wrapper(
        plain_to_omml(expr)
    )


def args_to_omml(args: list[str]) -> list[str]:
    return [to_inner_omml(arg) for arg in args]


# ============================================================
# Dispatcher
# ============================================================

def convert_function_to_omml(name: str, args: list[str]) -> str | None:
    name = name.strip()

    if name == "frac" and len(args) == 2:
        a = args_to_omml(args)
        return omml_fraction(a[0], a[1])

    if name == "sqrt" and len(args) == 1:
        a = args_to_omml(args)
        return omml_sqrt(a[0])

    if name in ("pow", "sup") and len(args) == 2:
        a = args_to_omml(args)
        return omml_superscript(a[0], a[1])

    if name == "sub" and len(args) == 2:
        a = args_to_omml(args)
        return omml_subscript(a[0], a[1])

    if name == "sum" and len(args) == 4:
        a = args_to_omml(args)
        return omml_sum(a[0], a[1], a[2], a[3])

    if name == "prod" and len(args) == 4:
        a = args_to_omml(args)
        return omml_prod(a[0], a[1], a[2], a[3])

    if name == "int" and len(args) == 4:
        a = args_to_omml(args)
        return omml_integral(a[0], a[1], a[2], a[3])

    if name == "lim" and len(args) == 3:
        a = args_to_omml(args)
        return omml_limit(a[0], a[1], a[2])

    if name == "matrix" and len(args) >= 1:
        matrix_text = ",".join(args)
        rows = parse_matrix_cells(matrix_text)

        omml_rows = [
            [to_inner_omml(cell) for cell in row]
            for row in rows
        ]

        return omml_matrix_cells(omml_rows)

    return None


# ============================================================
# Public API
# ============================================================

def plain_to_omml(expr: str) -> str:
    expr = expr.strip()

    parsed = parse_function(expr)

    if parsed:
        name, args = parsed
        converted = convert_function_to_omml(name, args)

        if converted is not None:
            return wrap_omml(converted)

    return wrap_omml(omml_text(expr))