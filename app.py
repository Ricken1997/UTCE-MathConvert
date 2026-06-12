import tkinter as tk
from tkinter import ttk
from utce_core_refactor_work import analyze_lines, build_latex_output, build_diagnosis_from_severity_counts

# ---------------------------------------------------
# Temporary converter (will later call utce_core.py)
# ---------------------------------------------------

def convert_text():
    plain_text = input_box.get("1.0", tk.END).strip()

    if not plain_text:
        return

    lines = plain_text.splitlines()

    latex_lines, warnings, severity_counts = analyze_lines(lines)
    latex_output = build_latex_output(latex_lines, "inline")
    diagnosis = build_diagnosis_from_severity_counts(severity_counts)

    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, latex_output)

    if warnings:
        warning_box.config(text="\n".join(warnings))
    else:
        warning_box.config(text="No warnings.")

    confidence_var.set(f"Confidence: {diagnosis.confidence_score:.1f}")
    risk_var.set(f"Predictive Risk: {diagnosis.predictive_risk:.1f}")
    level_var.set(f"Risk Level: {diagnosis.risk_level()}")

# ---------------------------------------------------
# Window
# ---------------------------------------------------

root = tk.Tk()
root.title("UTCE MathConvert v7.0 Alpha")
root.geometry("900x700")

# ---------------------------------------------------
# Input
# ---------------------------------------------------

input_label = ttk.Label(root, text="Input")
input_label.pack(anchor="w", padx=10, pady=5)

input_box = tk.Text(root, height=10)
input_box.pack(fill="both", padx=10)

# ---------------------------------------------------
# Button
# ---------------------------------------------------

convert_button = ttk.Button(
    root,
    text="Convert",
    command=convert_text
)
convert_button.pack(pady=10)

# ---------------------------------------------------
# Output
# ---------------------------------------------------

output_label = ttk.Label(root, text="LaTeX Output")
output_label.pack(anchor="w", padx=10)

output_box = tk.Text(root, height=10)
output_box.pack(fill="both", padx=10)

# ---------------------------------------------------
# Warning
# ---------------------------------------------------

warning_label = ttk.Label(root, text="Warnings")
warning_label.pack(anchor="w", padx=10)

warning_box = ttk.Label(root, text="")
warning_box.pack(anchor="w", padx=10)

# ---------------------------------------------------
# Diagnostic
# ---------------------------------------------------

diag_label = ttk.Label(root, text="Structural Diagnosis")
diag_label.pack(anchor="w", padx=10, pady=10)

confidence_var = tk.StringVar()
risk_var = tk.StringVar()
level_var = tk.StringVar()

confidence_var.set("Confidence:")
risk_var.set("Predictive Risk:")
level_var.set("Risk Level:")

ttk.Label(root, textvariable=confidence_var).pack(anchor="w", padx=20)
ttk.Label(root, textvariable=risk_var).pack(anchor="w", padx=20)
ttk.Label(root, textvariable=level_var).pack(anchor="w", padx=20)

# ---------------------------------------------------

root.mainloop()