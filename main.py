import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path


# Function for processing data from sheet
def process_data(filtered, date_info, output_dir):
    for location, group in filtered.groupby("Location"):
        total_row = pd.DataFrame([{"Donor_Name": "TOTAL", "Amount": group["Amount"].sum()}])
        out = pd.concat([group, total_row], ignore_index=True)
        filename = output_dir / (location.replace(" ", "_") + date_info + ".csv")
        out.to_csv(filename, index=False)

# Program logic for running tool on given fields from GUI
# Also preprocesses data to exclude fields. This is hardcoded.
# TODO: Make this not hardcoded



def run_tool(date, path, output_dir=""):
    output_dir = Path(output_dir) if output_dir else Path(path).parent
    date_info = "_" + date
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip().str.replace(" ", "_")
    excluded_types = ["recurring donation pledge"]
    filtered = df[~df["Donation_Type"].isin(excluded_types)].copy()
    process_data(filtered, date_info, output_dir)

# Tkinter logic
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue") 
root = ctk.CTk()
root.lift()
root.attributes("-topmost", True)
root.after_idle(root.attributes, "-topmost", False)
root.focus_force()
root.title("Donation Processor")
path_var = tk.StringVar()

def choose_file():
    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if path:  # empty if the user cancels
        path_var.set(path)

output_var = tk.StringVar()

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_var.set(folder)

def on_run():
    try:
        run_tool(date=date_entry.get(), path=path_var.get(), output_dir=output_var.get())
        messagebox.showinfo("Done", "Files created successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))
        

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

def main():
    root.mainloop()

    
if __name__ == "__main__":
    main()