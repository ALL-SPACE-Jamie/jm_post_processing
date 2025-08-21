# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 12:27:46 2025

@author: jmitchell
"""

import pandas as pd
import plotly.express as px
import tkinter as tk
from tkinter import filedialog, messagebox
import re

def generate_sunburst_from_labels(file_path, target_strings, output_html="sunburst_plot.html"):
    """
    Generate a sunburst plot from a CSV file by filtering entries based on label strings.

    Parameters
    ----------
    file_path : str
        Path to the input CSV file. The file must contain 'Labels' and 'Key' columns.
    target_strings : list of str
        List of label keywords to search for within the 'Labels' column.
    output_html : str, optional
        Path to save the generated sunburst plot as an HTML file. Default is 'sunburst_plot.html'.

    Returns
    -------
    None
    """
    df = pd.read_csv(file_path, encoding='ISO-8859-1')

    if 'Labels' not in df.columns or 'Key' not in df.columns:
        raise ValueError("CSV must contain 'Labels' and 'Key' columns.")

    matched_rows = []
    for target in target_strings:
        pattern = r'\b' + re.escape(target) + r'\b'
        matches = df[df['Labels'].str.contains(pattern, case=False, na=False)].copy()
        matches['label_search'] = target
        matched_rows.append(matches)

    if not matched_rows:
        raise ValueError("No matches found for target strings.")

    df_filtered = pd.concat(matched_rows, ignore_index=True)

    fig = px.sunburst(
        df_filtered,
        path=['label_search', 'Key'],
        title='Sunburst Plot: Label Exists → Entry Name',
        width=700,
        height=700,
        branchvalues='total'
    )

    fig.write_html(output_html)
    fig.show()
    
    return df_filtered

def run_gui():
    def browse_file():
        filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        file_entry.delete(0, tk.END)
        file_entry.insert(0, filename)

    def generate_plot():
        file_path = file_entry.get()
        labels_raw = labels_entry.get()
        output_file = output_entry.get()

        if not file_path or not labels_raw:
            messagebox.showerror("Missing Input", "Please provide both file and labels.")
            return

        labels = labels_raw.split()

        try:
            generate_sunburst_from_labels(file_path, labels, output_file)
            messagebox.showinfo("Success", f"Plot saved to {output_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Sunburst Plot Generator")
    root.geometry("600x200")

    tk.Label(root, text="CSV File:").grid(row=0, column=0, sticky="e", padx=10, pady=5)
    file_entry = tk.Entry(root, width=50)
    file_entry.grid(row=0, column=1, padx=5)
    tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2, padx=5)

    tk.Label(root, text="Labels (space-separated):").grid(row=1, column=0, sticky="e", padx=10, pady=5)
    labels_entry = tk.Entry(root, width=50)
    labels_entry.grid(row=1, column=1, columnspan=2, padx=5)

    tk.Label(root, text="Output File:").grid(row=2, column=0, sticky="e", padx=10, pady=5)
    output_entry = tk.Entry(root, width=50)
    output_entry.insert(0, "sunburst_plot.html")
    output_entry.grid(row=2, column=1, columnspan=2, padx=5)

    tk.Button(root, text="Generate Plot", command=generate_plot).grid(row=3, column=1, pady=15)

    root.mainloop()

if __name__ == "__main__":
    df = generate_sunburst_from_labels(r"C:\scratch\20250722\input9.csv", ['Customer', 'VLAN', 'XF_ASI', 'XF_TLMENV', 'XF_GTC3', 'XF_OTA', 'XF_LOBT'], output_html="sunburst_plot.html")
    filtered_df = df[['Issue Type', 'Key', 'Summary', 'Assignee', 'Labels', 'Priority']]
# %%
    filtered_df.to_html('xf.html', index=False)

