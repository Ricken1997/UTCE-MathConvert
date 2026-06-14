import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox

from utce_core_refactor_work import (
    analyze_lines,
    build_latex_output,
    build_diagnosis_from_severity_counts,
)


APP_TITLE = "UTCE MathConvert v8.0 Beta"


def convert_text():
    plain_text = input_box.get("1.0", tk.END).strip()

    if not plain_text:
        messagebox.showwarning("No input", "Please enter text before converting.")
        return

    lines = plain_text.splitlines()

    latex_lines, warnings, severity_counts = analyze_lines(lines)
    latex_output = build_latex_output(latex_lines, output_mode_var.get())
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


def clear_all():
    input_box.delete("1.0", tk.END)
    output_box.delete("1.0", tk.END)

    warning_box.config(text="")
    confidence_var.set("Confidence:")
    risk_var.set("Predictive Risk:")
    level_var.set("Risk Level:")


def save_output():
    output_text = output_box.get("1.0", tk.END).strip()

    if not output_text:
        messagebox.showwarning("No output", "There is no converted output to save.")
        return

    file_path = filedialog.asksaveasfilename(
        title="Save LaTeX Output",
        defaultextension=".tex",
        filetypes=[
            ("LaTeX files", "*.tex"),
            ("Text files", "*.txt"),
            ("All files", "*.*"),
        ],
    )

    if not file_path:
        return

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(output_text)

    messagebox.showinfo("Saved", f"Output saved successfully:\n{file_path}")


def copy_output():
    output_text = output_box.get("1.0", tk.END).strip()

    if not output_text:
        messagebox.showwarning(
            "No output",
            "There is no converted output to copy."
        )
        return

    root.clipboard_clear()
    root.clipboard_append(output_text)
    root.update()

    messagebox.showinfo(
        "Copied",
        "Output copied to clipboard."
    )

def insert_example_input():
    example_text = """frac(1,2)
sum(i,1,n,i^2)
prod(i,1,n,a_i)
matrix(1,2;3,4)
cases(x^2,x>0;0,x<=0)
union(A,B)
forall(x,P(x))"""

    input_box.delete("1.0", tk.END)
    input_box.insert(tk.END, example_text)

def open_text_file():
    file_path = filedialog.askopenfilename(
        title="Open Text File",
        filetypes=[
            ("Text files", "*.txt"),
            ("LaTeX files", "*.tex"),
            ("Markdown files", "*.md"),
            ("All files", "*.*"),
        ],
    )

    if not file_path:
        return

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        messagebox.showerror("Encoding error", "Could not read this file as UTF-8 text.")
        return
    except Exception as e:
        messagebox.showerror("Open error", str(e))
        return

    input_box.delete("1.0", tk.END)
    input_box.insert(tk.END, text)


root = tk.Tk()
root.title(APP_TITLE)
root.geometry("900x760")

main_frame = ttk.Frame(root, padding=12)
main_frame.pack(fill="both", expand=True)

title_label = ttk.Label(
    main_frame,
    text=APP_TITLE,
    font=("Helvetica", 18, "bold"),
)
title_label.pack(anchor="w", pady=(0, 10))

# Input
input_label = ttk.Label(main_frame, text="Input")
input_label.pack(anchor="w")

input_box = tk.Text(main_frame, height=10, wrap="word")
input_box.pack(fill="both", expand=False, pady=(0, 10))

# Controls
control_frame = ttk.Frame(main_frame)
control_frame.pack(fill="x", pady=(0, 10))

convert_button = ttk.Button(control_frame, text="Convert", command=convert_text)
convert_button.pack(side="left", padx=(0, 8))

open_button = ttk.Button(control_frame, text="Open Text File", command=open_text_file)
open_button.pack(side="left", padx=(0, 8))

example_button = ttk.Button(control_frame, text="Example Input", command=insert_example_input)
example_button.pack(side="left", padx=(0, 8))

save_button = ttk.Button(control_frame, text="Save Output", command=save_output)
save_button.pack(side="left", padx=(0, 8))

copy_button = ttk.Button(control_frame, text="Copy Output", command=copy_output)
copy_button.pack(side="left", padx=(0, 8))

clear_button = ttk.Button(control_frame, text="Clear", command=clear_all)
clear_button.pack(side="left", padx=(0, 8))

output_mode_var = tk.StringVar(value="inline")

mode_label = ttk.Label(control_frame, text="Output Mode:")
mode_label.pack(side="left", padx=(20, 6))

inline_radio = ttk.Radiobutton(
    control_frame,
    text="Inline",
    value="inline",
    variable=output_mode_var,
)
inline_radio.pack(side="left")

block_radio = ttk.Radiobutton(
    control_frame,
    text="Block",
    value="block",
    variable=output_mode_var,
)
block_radio.pack(side="left")

# Output
output_label = ttk.Label(main_frame, text="LaTeX Output")
output_label.pack(anchor="w")

output_box = tk.Text(main_frame, height=10, wrap="word")
output_box.pack(fill="both", expand=False, pady=(0, 10))

# Warnings
warning_label = ttk.Label(main_frame, text="Warnings")
warning_label.pack(anchor="w")

warning_box = ttk.Label(main_frame, text="", wraplength=850, justify="left")
warning_box.pack(anchor="w", pady=(0, 10))

# Diagnosis
diagnosis_label = ttk.Label(main_frame, text="Structural Diagnosis")
diagnosis_label.pack(anchor="w")

confidence_var = tk.StringVar(value="Confidence:")
risk_var = tk.StringVar(value="Predictive Risk:")
level_var = tk.StringVar(value="Risk Level:")

ttk.Label(main_frame, textvariable=confidence_var).pack(anchor="w", padx=20)
ttk.Label(main_frame, textvariable=risk_var).pack(anchor="w", padx=20)
ttk.Label(main_frame, textvariable=level_var).pack(anchor="w", padx=20)

root.mainloop()