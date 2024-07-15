import sqlite3
from tkinter import messagebox, ttk
import tkinter as tk
import pandas as pd

def connect_db():
    return sqlite3.connect('DataAnalysisApp/database.db')

def fetch_datasets(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_name FROM user_history WHERE user_informationid = ?", (int(user_id),))
        return [row[0] for row in cursor.fetchall()]

def fetch_results(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT result_name, result_path FROM user_result_history WHERE user_informationid = ?", (int(user_id),))
        return cursor.fetchall()

def display_results(window_title, data, user_id):
    results_win = tk.Toplevel()
    results_win.title(window_title)

    columns = data.columns.tolist()
    
    tree = ttk.Treeview(results_win, columns=columns, show="headings", height=10)
    tree.pack(padx=10, pady=10, fill='both', expand=True)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=80)
    
    for index, row in data.iterrows():
        values = [row[col] for col in columns]
        tree.insert("", "end", values=values)

    response_text = tk.Text(results_win, height=10, width=50)
    response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

def display_selected_result(user_id, results_listbox):
    selection = results_listbox.curselection()
    if selection:
        _, result_path = fetch_results(user_id)[selection[0]]
        try:
            data = pd.read_csv(result_path)
            display_results("Result Details", data, user_id)
        except Exception as e:
            messagebox.showerror("Error Loading File", str(e))

def load_data(user_id, filename):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT file_path FROM user_history WHERE user_informationid = ? AND file_name = ?", (int(user_id), filename))
        result = cursor.fetchone()
        return result[0] if result else None

def open_data_page(user_id, listbox, page_function):
    selection = listbox.curselection()
    if selection:
        filename = listbox.get(selection[0])
        file_path = load_data(user_id, filename)
        if file_path:
            dataframe = pd.read_csv(file_path)
            page_function(user_id, dataframe)