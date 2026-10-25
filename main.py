import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path

# ---------------------- Program Logic ---------------------------------- /

loaded_df = None
exclusions = []

def load_file(path):
    exclusions.clear()
    update_exclusion_label()
    global loaded_df

    try:
        df = pd.read_csv(path)
        df.columns = df.columns.str.strip().str.replace(" ", "_")
    except Exception as e:
        loaded_df = None
        show_text(f"Could not read file:\n{e}")
        column_menu.configure(values=["Load a file first"], state="disabled")
        column_menu.set("Load a file first")
        value_menu.configure(values=["—"], state="disabled")
        value_menu.set("—")
        return

    loaded_df = df

    column_menu.configure(values=list(df.columns), state="normal")
    show_text(df.head().to_string(index=False))
    column_menu.set("Choose a column")
    value_menu.configure(values=["—"], state="disabled")
    value_menu.set("—")

def show_text(text):
    preview_box.configure(state="normal")
    preview_box.delete("1.0", "end")
    preview_box.insert("1.0", text)
    preview_box.configure(state="disabled")

def on_column_selected(column):
    if loaded_df is None:
        return
    values = sorted(loaded_df[column].dropna().astype(str).unique())

    if not values:
        value_menu.configure(values=["(no values)"], state="disabled")
        value_menu.set("(no values)")
        return

    value_menu.configure(values=values, state="normal")
    value_menu.set("Choose a value")

def choose_file():
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if path:
        path_var.set(path)
        load_file(path)

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)

def on_run():
    if loaded_df is None:
        messagebox.showwarning("No file", "Load a file first.")
    try:
        run_tool(date=date_entry.get(), path=path_var.get(), output_dir=output_var.get())
        messagebox.showinfo("Done", "Files created successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def run_tool(date, path, output_dir=""):
    output_dir = Path(output_dir) if output_dir else Path(path).parent
    date_info = "_" + date
    # Checks if excluded types are in the given exclusion column
    filtered = loaded_df.copy()
    for column, value in exclusions:
        filtered = filtered[filtered[column].astype(str) != value]
    process_data(filtered, date_info, output_dir)
    totals_df = filtered.groupby("Location")["Amount"].sum().reset_index(name="Total")
    totals_df.to_csv(output_dir / ("Totals" + date_info + ".csv"), index=False, float_format="%.2f")

def exclusion_selector():
    column = column_menu.get()
    value = value_menu.get()
    if loaded_df is None:
        messagebox.showwarning("No file", "Load a file first.")
        return

    if column not in loaded_df.columns:
        messagebox.showwarning("No column", "Choose a column to exclude from.")
        return

    valid_values = set(loaded_df[column].dropna().astype(str))
    if value not in valid_values:
        messagebox.showwarning("No value", "Choose a value to exclude.")
        return

    rule = (column, value)
    if rule in exclusions:
        messagebox.showinfo("Already added", f"{column} = {value} is already excluded.")
        return
    
    exclusions.append(rule)
    value_menu.set("Choose a value")
    update_exclusion_label()

def update_exclusion_label():
    if not exclusions:
        text = "Excluded: none"
    else:
        lines = [f"{column} = {value}" for column, value in exclusions]
        text = "Excluded:\n" + "\n".join(lines)
    exclusion_label.configure(text=text)

def process_data(filtered, date_info, output_dir):
    for location, group in filtered.groupby("Location"):
        total_row = pd.DataFrame([{"Donor_Name": "TOTAL", "Amount": group["Amount"].sum()}])
        out = pd.concat([group, total_row], ignore_index=True)
        filename = output_dir / (location.replace(" ", "_") + date_info + ".csv")
        out.to_csv(filename, index=False)


# ---------------------- Tkinter Stuff ---------------------------------- /
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue") 
root = ctk.CTk()
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
root.focus_force()
root.title("Donation Processor")
path_var = tk.StringVar()
output_var = tk.StringVar()

# Row 0: date
ctk.CTkLabel(root, text="Date info:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
date_entry = ctk.CTkEntry(root, width=250, placeholder_text="e.g. C4_October_26")
date_entry.grid(row=0, column=1, padx=10, pady=8)

# Row 1: file
ctk.CTkLabel(root, text="Input file:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
ctk.CTkEntry(root, width=250, textvariable=path_var).grid(row=1, column=1, padx=10, pady=8)
ctk.CTkButton(root, text="Browse...", width=80, command=choose_file).grid(row=1, column=2, padx=10, pady=8)

# Row 2: output folder
ctk.CTkLabel(root, text="Output folder:").grid(row=2, column=0, padx=10, pady=8, sticky="w")
ctk.CTkEntry(root, width=250, textvariable=output_var).grid(row=2, column=1, padx=10, pady=8)
ctk.CTkButton(root, text="Browse...", width=80, command=choose_folder).grid(row=2, column=2, padx=10, pady=8)

# Row 3: run
ctk.CTkButton(root, text="Run", command=on_run).grid(row=3, column=1, pady=(4, 12))

# Row 4 and 5: preview box
ctk.CTkLabel(root, text="Preview:").grid(row=4, column=0, padx=10, pady=8, sticky="w")
preview_box = ctk.CTkTextbox(root, width=600, height=160, font=("Courier", 12), wrap="none")
preview_box.grid(row=5, column=0, columnspan=3, padx=10, pady=(0,12))
preview_box.configure(state="disabled")

# Row 6: exclusion selection
ctk.CTkLabel(root, text="Exclude:").grid(row=6, column=0, padx=10, pady=8, sticky="w")
column_menu = ctk.CTkOptionMenu(
    root,
    values=["Load a file first"],
    command=on_column_selected,
    state="disabled",
    width=250,
)
column_menu.grid(row=6, column=1, padx=10, pady=8)
value_menu = ctk.CTkOptionMenu(root, values=["—"], state="disabled", width=200)
value_menu.grid(row=6, column=2, padx=10, pady=8)

# Row 7: add button
ctk.CTkButton(root, text="Add exclusion", command=exclusion_selector).grid(
    row=7, column=2, padx=10, pady=(0, 8)
)

# Row 8: current exclusions
exclusion_label = ctk.CTkLabel(root, text="Excluded: none", justify="left", anchor="w")
exclusion_label.grid(row=8, column=0, columnspan=3, padx=10, pady=(0, 12), sticky="w")

# ---------------------- Main ------------------------------------------- /

def main():
    root.mainloop()

if __name__ == "__main__":
    main()