import re

def plain_to_latex(expr):
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

    expr = re.sub(r"sqrt\((.*?)\)", r"\\sqrt{\1}", expr)
    expr = re.sub(r"sin\((.*?)\)", r"\\sin(\1)", expr)
    expr = re.sub(r"cos\((.*?)\)", r"\\cos(\1)", expr)
    expr = re.sub(r"log\((.*?)\)", r"\\log(\1)", expr)

    greek = {
        "alpha": r"\alpha",
        "beta": r"\beta",
        "gamma": r"\gamma",
        "delta": r"\delta",
        "theta": r"\theta",
        "lambda": r"\lambda",
        "sigma": r"\sigma",
        "omega": r"\omega",
    }

    for plain, latex in greek.items():
        expr = re.sub(rf"\b{plain}\b", lambda m: latex, expr)

    expr = re.sub(
        r"([A-Za-z])\^([0-9A-Za-z])",
        r"\1^{\2}",
        expr
    )

    expr = expr.replace("*", r"\cdot ")

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