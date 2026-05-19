import re

def plain_to_latex(expr):
    expr = re.sub(r'([A-Za-z])\^([0-9A-Za-z])', r'\1^{\2}', expr)
    return "$" + expr + "$"

with open("test_input.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

latex = plain_to_latex(text)

print("Plain:")
print(text)

print()
print("LaTeX:")
print(latex)