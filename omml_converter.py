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


def plain_to_omml(expr: str) -> str:
    expr = expr.strip()

    # Remove inline/block LaTeX markers
    if expr.startswith("$") and expr.endswith("$"):
        expr = expr[1:-1].strip()

    # Convert LaTeX command form: \alpha -> alpha
    if expr.startswith("\\"):
        expr = expr[1:]

    # Greek symbol
    if expr in GREEK_MAP:
        return wrap_omml(
            omml_text(GREEK_MAP[expr])
        )

    # frac(numerator, denominator)
    if expr.startswith("frac(") and expr.endswith(")"):
        inside = expr[5:-1]
        parts = split_args(inside)

        if len(parts) == 2:
            numerator, denominator = parts

            num_omml = strip_omml_wrapper(plain_to_omml(numerator))
            den_omml = strip_omml_wrapper(plain_to_omml(denominator))

            return wrap_omml(
                omml_fraction(num_omml, den_omml)
            )

    # sqrt(value)
    if expr.startswith("sqrt(") and expr.endswith(")"):
        inside = expr[5:-1]
        inside_omml = strip_omml_wrapper(plain_to_omml(inside))

        return wrap_omml(
            omml_sqrt(inside_omml)
        )

    # pow(base, exponent)
    if expr.startswith("pow(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = split_args(inside)

        if len(parts) == 2:
            base, sup = parts

            base_omml = strip_omml_wrapper(plain_to_omml(base))
            sup_omml = strip_omml_wrapper(plain_to_omml(sup))

            return wrap_omml(
                omml_superscript(base_omml, sup_omml)
            )

    # sup(base, exponent)
    if expr.startswith("sup(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = split_args(inside)

        if len(parts) == 2:
            base, sup = parts

            base_omml = strip_omml_wrapper(plain_to_omml(base))
            sup_omml = strip_omml_wrapper(plain_to_omml(sup))

            return wrap_omml(
                omml_superscript(base_omml, sup_omml)
            )

    # sub(base, subscript)
    if expr.startswith("sub(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = split_args(inside)

        if len(parts) == 2:
            base, sub = parts

            base_omml = strip_omml_wrapper(plain_to_omml(base))
            sub_omml = strip_omml_wrapper(plain_to_omml(sub))

            return wrap_omml(
                omml_subscript(base_omml, sub_omml)
            )

    # sum(index, start, end, body)
    if expr.startswith("sum(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = split_args(inside)

        if len(parts) == 4:
            index, start, end, body = parts

            index_omml = strip_omml_wrapper(plain_to_omml(index))
            start_omml = strip_omml_wrapper(plain_to_omml(start))
            end_omml = strip_omml_wrapper(plain_to_omml(end))
            body_omml = strip_omml_wrapper(plain_to_omml(body))

            return wrap_omml(
                omml_sum(index_omml, start_omml, end_omml, body_omml)
            )

    # prod(index, start, end, body)
    if expr.startswith("prod(") and expr.endswith(")"):
        inside = expr[5:-1]
        parts = split_args(inside)

        if len(parts) == 4:
            index, start, end, body = parts

            index_omml = strip_omml_wrapper(plain_to_omml(index))
            start_omml = strip_omml_wrapper(plain_to_omml(start))
            end_omml = strip_omml_wrapper(plain_to_omml(end))
            body_omml = strip_omml_wrapper(plain_to_omml(body))

            return wrap_omml(
                omml_prod(index_omml, start_omml, end_omml, body_omml)
            )

    # int(variable, lower, upper, body)
    if expr.startswith("int(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = split_args(inside)

        if len(parts) == 4:
            variable, lower, upper, body = parts

            variable_omml = strip_omml_wrapper(plain_to_omml(variable))
            lower_omml = strip_omml_wrapper(plain_to_omml(lower))
            upper_omml = strip_omml_wrapper(plain_to_omml(upper))
            body_omml = strip_omml_wrapper(plain_to_omml(body))

            return wrap_omml(
                omml_integral(variable_omml, lower_omml, upper_omml, body_omml)
            )

    # lim(variable, target, body)
    if expr.startswith("lim(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = split_args(inside)

        if len(parts) == 3:
            variable, target, body = parts

            variable_omml = strip_omml_wrapper(plain_to_omml(variable))
            target_omml = strip_omml_wrapper(plain_to_omml(target))
            body_omml = strip_omml_wrapper(plain_to_omml(body))

            return wrap_omml(
                omml_limit(variable_omml, target_omml, body_omml)
            )

    # matrix(...)
    if expr.startswith("matrix(") and expr.endswith(")"):
        inside = expr[7:-1]
        return wrap_omml(
            omml_matrix(inside)
        )

    # cases(...)
    if expr.startswith("cases(") and expr.endswith(")"):
        inside = expr[6:-1]
        return wrap_omml(
            omml_cases(inside)
        )

    # fallback plain text
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