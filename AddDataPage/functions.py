import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import os
import sqlite3

def update_treeview(dataframe, tree):
    tree["columns"] = dataframe.columns.tolist()
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.delete(*tree.get_children())
    for index, row in dataframe.iterrows():
        tree.insert("", tk.END, values=row.tolist())

def load_file(data_container, tree, file_type):
    # Set up file dialog based on the file_type parameter
    file_types = {
        'csv': [("CSV files", "*.csv;*.CSV")],
        'excel': [("Excel files", "*.xls;*.xlsx;*.XLS;*.XLSX")],
        'json': [("JSON files", "*.json;*.JSON")]
    }

    filepath = filedialog.askopenfilename(filetypes=file_types[file_type])
    
    if filepath:
        # Process the file based on its type
        if file_type == 'csv':
            data_container["dataframe"] = pd.read_csv(filepath)
        elif file_type == 'excel':
            data_container["dataframe"] = pd.read_excel(filepath)
        elif file_type == 'json':
            data_container["dataframe"] = pd.read_json(filepath)

        # Update the data container with the file name
        data_container["file_name"] = os.path.basename(filepath)

        # Update the treeview with the new dataframe
        update_treeview(data_container["dataframe"], tree)

def save_csv(dataframe, file_name, user_id):
    if dataframe.empty:
        messagebox.showwarning("Atenție", "Nu există date de salvat.")
        return
    if not file_name:
        messagebox.showwarning("Atenție", "Nu a fost încărcat niciun fișier.")
        return
    folder_path = os.path.join("C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults", str(user_id),"DataSets")
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    filepath = os.path.join(folder_path, file_name)
    dataframe.to_csv(filepath, index=False)
    save_file_info_to_database(user_id, file_name, filepath)
    messagebox.showinfo("Succes", "Setul de date a fost salvat cu succes în " + filepath)

def save_file_info_to_database(user_id, filename, filepath):
    conn = sqlite3.connect('DataAnalysisApp/database.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO user_history (user_id, file_history, file_name)
        VALUES (?, ?, ?)
    ''', (user_id, filepath, filename))
    conn.commit()
    conn.close()