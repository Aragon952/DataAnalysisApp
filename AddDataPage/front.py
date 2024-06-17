import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import numpy as np
import sqlite3
from PrepareDataPage.front import open_prepare_data_page  # Ensure this import is correctly pointing to your module

def open_add_data_page(user_id):
    add_data_window = tk.Toplevel()
    add_data_window.title("Adaugare date")
    add_data_window.geometry("800x600")

    # Create a frame for TreeView and Scrollbars
    frame = ttk.Frame(add_data_window, padding="3 3 12 12")
    frame.pack(fill=tk.BOTH, expand=True)

    # TreeView setup
    tree = ttk.Treeview(frame, show="headings")
    tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    # Vertical Scrollbar
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=vsb.set)

    # Horizontal Scrollbar
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.configure(xscrollcommand=hsb.set)

    # Initialize an empty DataFrame
    dataframe = pd.DataFrame()

    def update_treeview(dataframe):
        tree["columns"] = dataframe.columns.tolist()
        for col in dataframe.columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        # Clear existing rows before adding new
        tree.delete(*tree.get_children())
        for index, row in dataframe.iterrows():
            tree.insert("", tk.END, values=row.tolist())

    def load_csv():
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if filepath:
            nonlocal dataframe
            dataframe = pd.read_csv(filepath)
            update_treeview(dataframe)
            filename = filepath.split('/')[-1]
            save_file_info_to_database(user_id, filename, filepath)

    # Button to add data and preprocess
    add_button = ttk.Button(add_data_window, text="Adaugare set de date", command=load_csv)
    add_button.pack(pady=10, fill=tk.X)

    # Button to open data preprocessing page
    prep_button = ttk.Button(add_data_window, text="Preprocesare Date", command=lambda: open_prepare_data_page(user_id, dataframe))
    prep_button.pack(pady=10, fill=tk.X)

    add_data_window.mainloop()

def save_file_info_to_database(user_id, filename, filepath):
    # Connect to SQLite database
    conn = sqlite3.connect('DataAnalysisApp/database.db')  # Ensure this path is correct
    cur = conn.cursor()
    
    # Insert data about the file into the database
    cur.execute('''
        INSERT INTO user_history (user_id, file_history, file_name)
        VALUES (?, ?, ?)
    ''', (user_id, filepath, filename))
    
    # Commit and close
    conn.commit()
    conn.close()