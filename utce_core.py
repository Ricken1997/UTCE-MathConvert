import re

def plain_to_latex(expr):
    # Basic structured functions
    expr = re.sub(r"frac\((\d+),(\d+)\)", r"\\frac{\1}{\2}", expr)

    expr = re.sub(
        r"sum\(([^,]+),([^,]+),([^,]+),([^)]+)\)",
        r"\\sum_{\1=\2}^{\3} \4",
        expr
    )

    expr = re.sub(
        r"int\(([^,]+),([^,]+),([^,]+),([^)]+)\)",
        r"\\int_{\1}^{\2} \3 \\, d\4",
        expr
    )

    expr = re.sub(
        r"lim\(([^,]+),([^,]+),([^)]+)\)",
        r"\\lim_{\1 \\to \2} \3",
        expr
    )

    expr = re.sub(
        r"partial\(([^,]+),([^)]+)\)",
        r"\\frac{\\partial \1}{\\partial \2}",
        expr
    )

    expr = re.sub(
        r"cases\((.*?);(.*?)\)",
        r"\\begin{cases} \1 \\\\ \2 \\end{cases}",
        expr
    )

    expr = re.sub(
        r"matrix\(([^,;]+),([^;]+);([^,;]+),([^)]+)\)",
        r"\\begin{bmatrix} \1 & \2 \\\\ \3 & \4 \\end{bmatrix}",
        expr
    )

    expr = re.sub(r"det\((.*?)\)", r"\\det(\1)", expr)
    expr = re.sub(r"floor\((.*?)\)", r"\\lfloor \1 \\rfloor", expr)
    expr = re.sub(r"ceil\((.*?)\)", r"\\lceil \1 \\rceil", expr)

    expr = re.sub(
    r"dot\((.*?),(.*?)\)",
    r"\1 \\cdot \2",
    expr
    )

    expr = re.sub(
    r"cross\((.*?),(.*?)\)",
    r"\1 \\times \2",
    expr
    )

    # Wrappers
    expr = re.sub(r"sqrt\((.*?)\)", r"\\sqrt{\1}", expr)
    expr = re.sub(r"abs\((.*?)\)", r"\\left|\1\\right|", expr)
    expr = re.sub(r"vec\((.*?)\)", r"\\vec{\1}", expr)
    expr = re.sub(r"hat\((.*?)\)", r"\\hat{\1}", expr)
    expr = re.sub(r"bar\((.*?)\)", r"\\bar{\1}", expr)
    expr = re.sub(r"max\((.*?)\)", r"\\max(\1)", expr)
    expr = re.sub(r"min\((.*?)\)", r"\\min(\1)", expr)
    expr = re.sub(r"norm\((.*?)\)", r"\\left\\|\1\\right\\|", expr)

    # Functions
    expr = re.sub(r"sin\((.*?)\)", r"\\sin(\1)", expr)
    expr = re.sub(r"cos\((.*?)\)", r"\\cos(\1)", expr)
    expr = re.sub(r"tan\((.*?)\)", r"\\tan(\1)", expr)
    expr = re.sub(r"log\((.*?)\)", r"\\log(\1)", expr)
    expr = re.sub(r"ln\((.*?)\)", r"\\ln(\1)", expr)
    expr = re.sub(r"exp\((.*?)\)", r"e^{\1}", expr)

    # Greek letters
    greek = {
    "alpha": r"\alpha",
    "beta": r"\beta",
    "gamma": r"\gamma",
    "delta": r"\delta",
    "epsilon": r"\epsilon",
    "theta": r"\theta",
    "lambda": r"\lambda",
    "mu": r"\mu",
    "nu": r"\nu",
    "rho": r"\rho",
    "sigma": r"\sigma",
    "phi": r"\phi",
    "omega": r"\omega",
}

    for plain, latex in greek.items():
        expr = re.sub(rf"\b{plain}\b", lambda m: latex, expr)

    # Constants and operators
    expr = re.sub(r"\bpi\b", r"\\pi", expr)
    expr = expr.replace("<=", r"\le ")
    expr = expr.replace(">=", r"\ge ")
    expr = expr.replace("!=", r"\ne ")
    expr = expr.replace("->", r"\to ")
    expr = expr.replace("<->", r"\leftrightarrow ")
    expr = expr.replace("*", r"\cdot ")

    # Subscripts
    expr = re.sub(
    r"([A-Za-z])_([0-9A-Za-z])",
    r"\1_{\2}",
    expr
    )

    expr = re.sub(
    r"([A-Za-z])_\(([^()]*)\)",
    r"\1_{\2}",
    expr
    )
    
    # Exponents
    expr = re.sub(
        r"([A-Za-z])\^([0-9A-Za-z])",
        r"\1^{\2}",
        expr
    )

    return "$" + expr + "$"


with open("test_input.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()

latex_lines = []

for line in lines:
    text = line.strip()
    if text:
        latex_lines.append(plain_to_latex(text))

latex = "\n".join(latex_lines)

print("Plain:")
for line in lines:
    print(line.strip())

print()
print("LaTeX:")
print(latex)

with open("output_latex.txt", "w", encoding="utf-8") as f:
    f.write(latex)