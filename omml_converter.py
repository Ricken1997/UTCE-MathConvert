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