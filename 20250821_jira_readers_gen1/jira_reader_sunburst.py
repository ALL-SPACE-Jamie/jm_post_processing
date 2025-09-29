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
    
    # Select all columns that start with 'Labels'
    label_cols = [col for col in df.columns if col.startswith('Labels')]
    
    # Replace NaNs with empty strings before merging
    df[label_cols] = df[label_cols].fillna('')
    
    # Merge them into a single column with semi-colons
    df['Labels'] = df[label_cols].astype(str).apply(lambda row: ';'.join(filter(None, row)), axis=1)
    
    # Add 'XF Work package' column: 'Yes' if 'XF' appears in Labels, else 'No'
    df['XF Work package'] = df['Labels'].str.contains('XF', case=False, na=False).map({True: 'Yes', False: 'No'})
    
    # Filter out closed NCs
    status_keywords = ['NC Complete', 'NC Cancelled']
    for keyword in status_keywords:
        df = df[df['Status'] != keyword]
    
    # Check required columns
    if 'Labels' not in df.columns or 'Issue key' not in df.columns:
        raise ValueError("CSV must contain 'Labels' and 'Issue key' columns.")
    
    # Match target strings
    matched_rows = []
    for target in target_strings:
        pattern = re.escape(target)
        matches = df[df['Labels'].str.contains(pattern, case=False, na=False)].copy()
        matches['label_search'] = target
        matched_rows.append(matches)
    
    if not matched_rows:
        raise ValueError("No matches found for target strings.")
    
    df_filtered = pd.concat(matched_rows, ignore_index=True)
    
    # Create sunburst plot
    fig = px.sunburst(
        df_filtered,
        path=['label_search', 'Issue key'],
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
    # label_list = ['VLAN', 'XF_ASI', 'XF_TLMENV', 'XF_GTC3', 'XF_OTA', 'XF_LOBT']
    # label_list = ['GEN1']
    # label_list = ['XF_']
    label_list = ['']
    df = generate_sunburst_from_labels(r"C:\scratch\20250722\input14.csv", label_list, output_html="sunburst_plot.html")
    filtered_df = df[['Issue Type', 'Issue key', 'ï»¿Summary', 'Assignee', 'Labels', 'Priority', 'Status', 'XF Work package']]
    
    html_table = filtered_df.to_html(index=False, table_id="sortable")

    # Wrap it with HTML and JavaScript for sorting
    html_content = f"""
    <html>
    <head>
      <script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>
      <style>
        th {{
          background-color: navy;
          color: white;
          cursor: pointer;
          position: relative;
          padding-right: 20px;
          text-align: left;
        }}
        th::after {{
          content: '\\25B4\\25BE';  /* ▲▼ */
          position: absolute;
          right: 5px;
          font-size: 0.8em;
          color: #ccc;
        }}
        table {{
          border-collapse: collapse;
          width: 100%;
        }}
        td, th {{
          padding: 8px;
          border: 1px solid #ddd;
        }}
      </style>
    </head>
    <body>
      {html_table}
      <script>
        document.addEventListener("DOMContentLoaded", function() {{
          new Tablesort(document.getElementById('sortable'));
        }});
      </script>
    </body>
    </html>
    """

    
    # Save to file
    with open("xf.html", "w", encoding="utf-8") as f:
        f.write(html_content)


