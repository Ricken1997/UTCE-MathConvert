import html


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


def wrap_omml(math_body: str) -> str:
    return (
        "<m:oMathPara>"
        "<m:oMath>"
        + math_body
        + "</m:oMath>"
        "</m:oMathPara>"
    )


def plain_to_omml(expr: str) -> str:
    expr = expr.strip()

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