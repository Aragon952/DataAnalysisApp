import sqlite3
from tkinter import messagebox
import tkinter as tk
import pandas as pd

def connect_db():
    return sqlite3.connect('DataAnalysisApp/database.db')

def fetch_datasets(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_name FROM user_history WHERE user_id = ?", (user_id,))
    datasets = [row[0] for row in cursor.fetchall()]
    conn.close()
    return datasets

def load_data(user_id, filename):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_history FROM user_history WHERE user_id = ? AND file_name = ?", (user_id, filename))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def select_item(event, listbox, user_id):
    if listbox.curselection():
        index = int(listbox.curselection()[0])
        selected = listbox.get(index)
        file_path = load_data(user_id, selected)
        return selected, file_path
    return None, None


def on_select(event, user_id, listbox, selected_file_entry, dataframe_container):
    selected, file_path = select_item(event, listbox, user_id)
    if selected:
        selected_file_entry.delete(0, tk.END)
        selected_file_entry.insert(0, selected)
        # Update the DataFrame inside the container
        dataframe_container["dataframe"] = send_data(file_path)

def send_data(file_path):
    if file_path:
        try:
            dataframe = pd.read_csv(file_path)
            return dataframe  # Return the new DataFrame
        except Exception as e:
            messagebox.showerror("Eroare la încărcarea fișierului", str(e))
            return pd.DataFrame()  # Return an empty DataFrame on failure
    else:
        messagebox.showinfo("Informație", "Calea fișierului nu a fost găsită în baza de date.")
        return pd.DataFrame()  # Return an empty DataFrame if not found