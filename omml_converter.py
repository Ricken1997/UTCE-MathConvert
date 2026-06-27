import html

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
    return html.escape(text, quote=False)


def omml_text(text: str) -> str:
    text = escape_xml(text)

    return (
        "<m:r>"
        "<m:t>"
        + text
        + "</m:t>"
        "</m:r>"
    )


def omml_raw(xml: str) -> str:
    return xml


def wrap_omml(math_body: str) -> str:
    return (
        "<m:oMathPara>"
        "<m:oMath>"
        + math_body
        + "</m:oMath>"
        "</m:oMathPara>"
    )


def omml_fraction(numerator: str, denominator: str) -> str:

    return (
        "<m:f>"
        "<m:num>"
        + numerator
        + "</m:num>"
        "<m:den>"
        + denominator
        + "</m:den>"
        "</m:f>"
    )


def omml_superscript(base: str, sup: str) -> str:
    base = escape_xml(base)
    sup = escape_xml(sup)

    return (
        "<m:sSup>"
        "<m:e>"
        + omml_text(base)
        + "</m:e>"
        "<m:sup>"
        + omml_text(sup)
        + "</m:sup>"
        "</m:sSup>"
    )


def omml_subscript(base: str, sub: str) -> str:
    base = escape_xml(base)
    sub = escape_xml(sub)

    return (
        "<m:sSub>"
        "<m:e>"
        + omml_text(base)
        + "</m:e>"
        "<m:sub>"
        + omml_text(sub)
        + "</m:sub>"
        "</m:sSub>"
    )


def omml_sqrt(value: str) -> str:

    return (
        "<m:rad>"
        "<m:radPr>"
        "<m:degHide m:val=\"1\"/>"
        "</m:radPr>"
        "<m:deg/>"
        "<m:e>"
        + value
        + "</m:e>"
        "</m:rad>"
    )


def omml_sum(index: str, start: str, end: str, body: str) -> str:
    index = strip_omml_wrapper(index)
    start = strip_omml_wrapper(start)
    end = strip_omml_wrapper(end)
    body = strip_omml_wrapper(body)

    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∑\"/>"
        "<m:limLoc m:val=\"undOvr\"/>"
        "</m:naryPr>"
        "<m:sub>"
        + index
        + "<m:r><m:t>=</m:t></m:r>"
        + start
        + "</m:sub>"
        "<m:sup>"
        + end
        + "</m:sup>"
        "<m:e>"
        + body
        + "</m:e>"
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
        "<m:sup>"
        + end +
        "</m:sup>"
        "<m:e>"
        + body +
        "</m:e>"
        "</m:nary>"
    )


def omml_integral(variable: str, lower: str, upper: str, body: str) -> str:
    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∫\"/>"
        "<m:limLoc m:val=\"subSup\"/>"
        "</m:naryPr>"
        "<m:sub>"
        + lower +
        "</m:sub>"
        "<m:sup>"
        + upper +
        "</m:sup>"
        "<m:e>"
        + body
        + omml_text(" d")
        + variable +
        "</m:e>"
        "</m:nary>"
    )


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


def omml_matrix(matrix_text: str) -> str:
    rows = matrix_text.split(";")

    row_xml = ""

    for row in rows:
        cells = [cell.strip() for cell in row.split(",")]

        cell_xml = ""
        for cell in cells:
            cell_xml += (
                "<m:e>"
                + omml_text(cell)
                + "</m:e>"
            )

        row_xml += (
            "<m:mr>"
            + cell_xml
            + "</m:mr>"
        )

    return (
        "<m:m>"
        "<m:mPr/>"
        + row_xml
        + "</m:m>"
    )


def omml_limit(variable: str, target: str, body: str) -> str:
    variable = escape_xml(variable)
    target = escape_xml(target)
    body = escape_xml(body)

    return (
        "<m:limLow>"
        "<m:e>"
        + omml_text("lim")
        + "</m:e>"
        "<m:lim>"
        + omml_text(variable + "→" + target)
        + "</m:lim>"
        "</m:limLow>"
        + omml_text(body)
    )


def omml_cases(cases_text: str) -> str:
    rows = cases_text.split(";")

    row_xml = ""

    for row in rows:
        parts = [p.strip() for p in row.split(",")]

        if len(parts) == 2:
            value, condition = parts

            row_xml += (
                "<m:mr>"
                "<m:e>"
                + omml_text(value)
                + "</m:e>"
                "<m:e>"
                + omml_text(condition)
                + "</m:e>"
                "</m:mr>"
            )

    return (
        "<m:m>"
        "<m:mPr/>"
        + row_xml
        + "</m:m>"
    )


def omml_subsup(base: str, sub: str, sup: str) -> str:
    base = escape_xml(base)
    sub = escape_xml(sub)
    sup = escape_xml(sup)

    return (
        "<m:sSubSup>"
        "<m:e>"
        + omml_text(base)
        + "</m:e>"
        "<m:sub>"
        + omml_text(sub)
        + "</m:sub>"
        "<m:sup>"
        + omml_text(sup)
        + "</m:sup>"
        "</m:sSubSup>"
    )


def omml_diff(body: str, variable: str) -> str:
    body = escape_xml(body)
    variable = escape_xml(variable)

    return (
        "<m:f>"
        "<m:num>"
        + omml_text("d" + body)
        + "</m:num>"
        "<m:den>"
        + omml_text("d" + variable)
        + "</m:den>"
        "</m:f>"
    )


def omml_run(text):
    return f"<m:r><m:t>{text}</m:t></m:r>"


def strip_omml_wrapper(omml):
    return (
        omml
        .replace("<m:oMathPara><m:oMath>", "")
        .replace("</m:oMath></m:oMathPara>", "")
    )


def find_top_level_operator(text: str):
    """
    Find the rightmost top-level operator outside parentheses.
    Returns (index, raw_operator, display_operator) or None.
    """
    operators = [
        ("+", "+"),
        ("-", "−"),
        ("*", "×"),
        ("×", "×"),
        ("/", "÷"),
        ("÷", "÷"),
    ]

    depth = 0

    for i in range(len(text) - 1, -1, -1):
        ch = text[i]

        if ch == ")":
            depth += 1
            continue

        if ch == "(":
            depth -= 1
            continue

        if depth == 0:
            for raw_op, display_op in operators:
                if text.startswith(raw_op, i):
                    return i, raw_op, display_op

    return None


def omml_shallow_composite(text):
    text = text.strip()

    found = find_top_level_operator(text)
    if not found:
        return None

    index, raw_op, display_op = found

    left = text[:index].strip()
    right = text[index + len(raw_op):].strip()

    if not left or not right:
        return None

    left_result = plain_to_omml(left)
    right_result = plain_to_omml(right)

    left_omml = strip_omml_wrapper(left_result)
    right_omml = strip_omml_wrapper(right_result)

    return (
        "<m:oMathPara><m:oMath>"
        + left_omml
        + omml_run(display_op)
        + right_omml
        + "</m:oMath></m:oMathPara>"
    )


def split_args(s: str) -> list[str]:
    parts = []
    buf = ""
    depth = 0

    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1

        if ch == "," and depth == 0:
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
        return None, []

    name = expr[:expr.find("(")].strip()
    inside = expr[expr.find("(") + 1:-1]

    args = split_args(inside)
    return name, args


def to_inner_omml(expr: str) -> str:
    return strip_omml_wrapper(
        plain_to_omml(expr)
    )


def args_to_omml(args):
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


def plain_to_omml(expr: str) -> str:
    expr = expr.strip()

    if expr.startswith("$") and expr.endswith("$"):
        expr = expr[1:-1].strip()

    if expr.startswith("\\"):
        expr = expr[1:]

    if expr in GREEK_MAP:
        return wrap_omml(
            omml_text(GREEK_MAP[expr])
        )

    name, args = parse_function(expr)

    converted = convert_function_to_omml(name, args)
    if converted is not None:
        return wrap_omml(converted)

    if name == "matrix" and len(args) >= 1:
        return wrap_omml(
            omml_matrix(expr[7:-1])
        )

    if name == "cases" and len(args) >= 1:
        return wrap_omml(
            omml_cases(expr[6:-1])
        )

    return wrap_omml(
        omml_text(expr)
    )


def latex_to_omml_placeholder(latex_line: str) -> str:
    """
    Placeholder for later LaTeX -> true OMML conversion.
    Current v11.0 entrance supports plain frac(a,b) -> OMML fraction.
    """
    return wrap_omml(
        omml_text(latex_line)
    )