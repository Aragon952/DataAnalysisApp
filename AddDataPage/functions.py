import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
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

def get_value_from_user(prompt):
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    user_value = simpledialog.askstring("Input", prompt, parent=root)

    root.destroy()  # Destroy the hidden main window

    return user_value

def save_file_info_to_database(user_id, filename, filepath):
    conn = sqlite3.connect('DataAnalysisApp/database.db')
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO user_history (user_informationid, file_path, file_name)
            VALUES (?, ?, ?)
        ''', (user_id, filepath, filename))
        conn.commit()
        messagebox.showinfo("Success", "File info saved successfully to database.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()

def save_csv(dataframe, user_id):
    if dataframe.empty:
        messagebox.showwarning("Warning", "There is no data to save.")
        return

    file_name = get_value_from_user("Enter the name for the CSV file:")
    if file_name:
        if not file_name.endswith(".csv"):
            file_name += ".csv"

        directory = f"C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults\\{user_id}\\DataSets"

        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, file_name)

        dataframe.to_csv(file_path, index=False)

        save_file_info_to_database(user_id, file_name, file_path)

        messagebox.showinfo("Success", f"The dataset was successfully saved to {file_path}")
    else:
        messagebox.showwarning("Warning", "Filename was not provided. Data was not saved.")
