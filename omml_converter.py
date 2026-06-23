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


def wrap_omml(math_body: str) -> str:
    return (
        "<m:oMathPara>"
        "<m:oMath>"
        + math_body
        + "</m:oMath>"
        "</m:oMathPara>"
    )


def omml_fraction(numerator: str, denominator: str) -> str:
    numerator = escape_xml(numerator)
    denominator = escape_xml(denominator)

    return (
        "<m:f>"
        "<m:num>"
        + omml_text(numerator)
        + "</m:num>"
        "<m:den>"
        + omml_text(denominator)
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
    value = escape_xml(value)

    return (
        "<m:rad>"
        "<m:radPr>"
        "<m:degHide m:val=\"1\"/>"
        "</m:radPr>"
        "<m:deg/>"
        "<m:e>"
        + omml_text(value)
        + "</m:e>"
        "</m:rad>"
    )


def omml_sum(index: str, start: str, end: str, body: str) -> str:
    index = escape_xml(index)
    start = escape_xml(start)
    end = escape_xml(end)
    body = escape_xml(body)

    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∑\"/>"
        "<m:limLoc m:val=\"undOvr\"/>"
        "</m:naryPr>"
        "<m:sub>"
        + omml_text(index + "=" + start)
        + "</m:sub>"
        "<m:sup>"
        + omml_text(end)
        + "</m:sup>"
        "<m:e>"
        + omml_text(body)
        + "</m:e>"
        "</m:nary>"
    )


def omml_prod(index: str, start: str, end: str, body: str) -> str:
    index = escape_xml(index)
    start = escape_xml(start)
    end = escape_xml(end)
    body = escape_xml(body)

    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∏\"/>"
        "<m:limLoc m:val=\"undOvr\"/>"
        "</m:naryPr>"
        "<m:sub>"
        + omml_text(index + "=" + start)
        + "</m:sub>"
        "<m:sup>"
        + omml_text(end)
        + "</m:sup>"
        "<m:e>"
        + omml_text(body)
        + "</m:e>"
        "</m:nary>"
    )


def omml_integral(variable: str, lower: str, upper: str, body: str) -> str:
    variable = escape_xml(variable)
    lower = escape_xml(lower)
    upper = escape_xml(upper)
    body = escape_xml(body)

    return (
        "<m:nary>"
        "<m:naryPr>"
        "<m:chr m:val=\"∫\"/>"
        "<m:limLoc m:val=\"subSup\"/>"
        "</m:naryPr>"
        "<m:sub>"
        + omml_text(lower)
        + "</m:sub>"
        "<m:sup>"
        + omml_text(upper)
        + "</m:sup>"
        "<m:e>"
        + omml_text(body + " d" + variable)
        + "</m:e>"
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


def plain_to_omml(expr: str) -> str:
    expr = expr.strip()

    # Remove inline/block LaTeX markers if they arrive here
    if expr.startswith("$") and expr.endswith("$"):
        expr = expr[1:-1].strip()

    # Convert LaTeX command form: \alpha -> alpha
    if expr.startswith("\\"):
        expr = expr[1:]

    # Greek symbol conversion
    if expr in GREEK_MAP:
        return wrap_omml(
            omml_text(GREEK_MAP[expr])
        )

    if expr.startswith("frac(") and expr.endswith(")"):
        inside = expr[5:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 2:
            numerator, denominator = parts
            return wrap_omml(
                omml_fraction(numerator, denominator)
            )

        if expr.startswith("pow(") and expr.endswith(")"):
            inside = expr[4:-1]
            parts = [p.strip() for p in inside.split(",")]

            if len(parts) == 2:
                base, sup = parts
                return wrap_omml(
                    omml_superscript(base, sup)
                )

    if expr.startswith("sup(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 2:
            base, sup = parts
            return wrap_omml(
                omml_superscript(base, sup)
            )

    if expr.startswith("sub(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 2:
            base, sub = parts
            return wrap_omml(
                omml_subscript(base, sub)
            )
    
    if expr.startswith("sqrt(") and expr.endswith(")"):
        inside = expr[5:-1].strip()
        return wrap_omml(
            omml_sqrt(inside)
        )

    if expr.startswith("sum(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 4:
            index, start, end, body = parts
            return wrap_omml(
                omml_sum(index, start, end, body)
            )
    
    if expr.startswith("prod(") and expr.endswith(")"):
        inside = expr[5:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 4:
            index, start, end, body = parts
            return wrap_omml(
                omml_prod(index, start, end, body)
            )
    
    if expr.startswith("int(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 4:
            variable, lower, upper, body = parts
            return wrap_omml(
                omml_integral(variable, lower, upper, body)
            )
    
    if expr.startswith("matrix(") and expr.endswith(")"):
        inside = expr[7:-1]
        return wrap_omml(
            omml_matrix(inside)
        )
    
    if expr.startswith("lim(") and expr.endswith(")"):
        inside = expr[4:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 3:
            variable, target, body = parts
            return wrap_omml(
                omml_limit(variable, target, body)
            )
    
    if expr.startswith("cases(") and expr.endswith(")"):
        inside = expr[6:-1]
        return wrap_omml(
            omml_cases(inside)
        )
    
    if expr.startswith("subsup(") and expr.endswith(")"):
        inside = expr[7:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 3:
            base, sub, sup = parts
            return wrap_omml(
                omml_subsup(base, sub, sup)
            )

    if expr.startswith("diff(") and expr.endswith(")"):
        inside = expr[5:-1]
        parts = [p.strip() for p in inside.split(",")]

        if len(parts) == 2:
            body, variable = parts
            return wrap_omml(
                omml_diff(body, variable)
            )
    
    composite = omml_shallow_composite(expr)
    if composite:
        return composite

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