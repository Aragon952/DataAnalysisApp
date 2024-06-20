import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import os
import sqlite3

def update_entry_and_methods(listbox, entry, method_cb, methods):
    selection = listbox.curselection()
    if selection:
        entry.delete(0, tk.END)
        entry.insert(0, listbox.get(selection[0]))
        method_cb['values'] = methods  # Update the methods in the combobox

import os
import tkinter as tk
from tkinter import simpledialog, messagebox

def save_file_info_to_database(user_id, filename, filepath):
    conn = sqlite3.connect('DataAnalysisApp/database.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO user_history (user_id, file_history, file_name)
        VALUES (?, ?, ?)
    ''', (user_id, filepath, filename))
    conn.commit()
    conn.close()

def save_csv(dataframe, user_id):
    # Initialize a new Tkinter root for the dialog
    dialog_root = tk.Toplevel()
    dialog_root.withdraw()  # Hide the dialog main window

    # Prompt the user for the filename
    file_name = simpledialog.askstring("Input", "Enter the name for the CSV file:", parent=dialog_root)
    if file_name:
        # Ensure the filename ends with .csv
        if not file_name.endswith(".csv"):
            file_name += ".csv"
        
        # Construct the directory path based on user_id
        directory = f"C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults\\{user_id}"
        
        # Ensure the directory exists
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        # Construct the full file path
        file_path = os.path.join(directory, file_name)
        
        # Save the dataframe to CSV
        dataframe.to_csv(file_path, index=False)
        
        # Save the file location to the database
        save_file_info_to_database(user_id, file_name, file_path)
        
        # Notify the user
        messagebox.showinfo("Success", f"Data saved successfully to {file_path}", parent=dialog_root)
    else:
        messagebox.showwarning("Warning", "Filename was not provided. Data was not saved.", parent=dialog_root)
    
    dialog_root.destroy()  # Close only the dialog window

def update_treeview(dataframe, tree):
    tree["columns"] = dataframe.columns.tolist()
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.delete(*tree.get_children())
    for index, row in dataframe.iterrows():
        tree.insert("", tk.END, values=row.tolist())


def apply_method(dataframe, method, col_type):
    # Definim switch-urile ca dicționare în cadrul funcției
    numeric_methods = {
        'Selectare Coloane': select_columns,
        'FillNa cu mediana': fill_na_with_median,
        'FillNa cu medie': fill_na_with_mean,
        'FillNa cu valoare specifică': lambda df, col: fill_na_with_value(df, col, value),
        'MICE': mice_imputation,
        'Replace': replace_values,
        'Standardizare': standardize,
        'Normalizare': normalize,
        'Tratare outlieri': handle_outliers,
        'Grupare': group_data,
        'Redenumire coloană': rename_column,
        'Eliminare coloană': drop_column
    }

    alfanumeric_methods = {
        'Selectare Coloane': select_columns,
        'FillNa cu valoare specifică': lambda df, col: fill_na_with_value(df, col, value),
        'Replace': replace_values,
        'String Slicing': string_slicing,
        'Codare binara pe pozitii': binary_encoding,
        'Codificare numerica': numeric_encoding,
        'Grupare': group_data,
        'Redenumire coloană': rename_column,
        'Eliminare coloană': drop_column
    }

    # Selectăm switch-ul corect pe baza tipului de coloană
    methods = numeric_methods if col_type == 'numeric' else alfanumeric_methods
    
    if method in methods:
        columns = dataframe.select_dtypes(include='number').columns if col_type == 'numeric' else dataframe.select_dtypes(exclude='number').columns
        for column in columns:
            methods[method](dataframe, column)
        print(f"Applied {method} to all {col_type} columns: {', '.join(columns)}")
    else:
        raise ValueError(f"Metoda selectată '{method}' nu este recunoscută pentru coloanele {col_type}.")
    

def select_columns(dataframe, column):
    pass

def fill_na_with_median(dataframe, column):
    dataframe[column].fillna(dataframe[column].median(), inplace=True)

def fill_na_with_mean(dataframe, column):
    dataframe[column].fillna(dataframe[column].mean(), inplace=True)

def fill_na_with_value(dataframe, column, value):
    dataframe[column].fillna(value, inplace=True)

def mice_imputation(dataframe, column):
    pass

def replace_values(dataframe, column):
    pass

def standardize(dataframe, column):
    pass

def normalize(dataframe, column):
    pass

def handle_outliers(dataframe, column):
    pass

def group_data(dataframe, column):
    pass

def rename_column(dataframe, column):
    pass

def drop_column(dataframe, column):
    dataframe.drop(column, axis=1, inplace=True)