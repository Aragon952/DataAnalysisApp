import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import os
import sqlite3

def update_entry_and_methods(listbox, entry, method_cb, methods):
    selection = listbox.curselection()
    if selection:
        entry.delete(0, tk.END)
        entry.insert(0, listbox.get(selection[0]))
        method_cb['values'] = methods  # Update the methods in the combobox

def update_treeview(dataframe, tree):
    tree.configure(columns=dataframe.columns.tolist())
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.delete(*tree.get_children())
    for index, row in dataframe.iterrows():
        tree.insert("", tk.END, values=row.tolist())

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
    dialog_root = tk.Toplevel()
    dialog_root.withdraw()  # Hide the dialog main window

    file_name = simpledialog.askstring("Input", "Enter the name for the CSV file:", parent=dialog_root)
    if file_name:
        if not file_name.endswith(".csv"):
            file_name += ".csv"
        
        directory = f"C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults\\{user_id}"
        
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        file_path = os.path.join(directory, file_name)
        
        dataframe.to_csv(file_path, index=False)
        
        save_file_info_to_database(user_id, file_name, file_path)
        
        messagebox.showinfo("Success", f"Data saved successfully to {file_path}", parent=dialog_root)
    else:
        messagebox.showwarning("Warning", "Filename was not provided. Data was not saved.", parent=dialog_root)
    
    dialog_root.destroy()

def apply_method(dataframe, method, col_type, main_tree):
    if col_type == 'numeric':
        columns = dataframe.select_dtypes(include='number').columns
    else:
        columns = dataframe.select_dtypes(exclude='number').columns

    for column in columns:
        if method == 'Selectare Coloane':
            select_columns(dataframe, column, main_tree)
        elif method == 'FillNa cu mediana':
            fill_na_with_median(dataframe, column)
        elif method == 'FillNa cu medie':
            fill_na_with_mean(dataframe, column)
        elif method == 'FillNa cu valoare specifică':
            value = get_value_from_user("Enter the value to fill NA:")
            fill_na_with_value(dataframe, column, value)
        elif method == 'MICE':
            mice_imputation(dataframe, column)
        elif method == 'Replace':
            replace_values(dataframe, column)
        elif method == 'Standardizare':
            standardize(dataframe, column)
        elif method == 'Normalizare':
            normalize(dataframe, column)
        elif method == 'Tratare outlieri':
            handle_outliers(dataframe, column)
        elif method == 'Grupare':
            group_data(dataframe, column)
        elif method == 'Redenumire coloană':
            rename_column(dataframe, column)
        elif method == 'Eliminare coloană':
            drop_column(dataframe, column)
        elif col_type == 'alpha' and method == 'String Slicing':
            string_slicing(dataframe, column)
        elif col_type == 'alpha' and method == 'Codare binara pe pozitii':
            binary_encoding(dataframe, column)
        elif col_type == 'alpha' and method == 'Codificare numerica':
            numeric_encoding(dataframe, column)
        else:
            print(f"Method '{method}' is not recognized for columns of type '{col_type}'. No action taken.")

    print(f"Applied {method} to all {col_type} columns: {', '.join(columns)}")
    update_treeview(dataframe, main_tree)


def get_value_from_user(prompt):
    dialog_root = tk.Toplevel()
    dialog_root.grab_set()
    dialog_root.withdraw()
    value = simpledialog.askstring("Input", prompt, parent=dialog_root)
    dialog_root.destroy()
    return value

def select_columns(dataframe, column, main_tree):
    top = tk.Toplevel()
    top.title("Select Columns")
    top.grab_set()

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    available_label = ttk.Label(main_frame, text="Available Columns")
    available_label.grid(row=0, column=0, padx=10)
    listbox_available = tk.Listbox(main_frame, selectmode=tk.MULTIPLE)
    listbox_available.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

    selected_label = ttk.Label(main_frame, text="Selected Columns")
    selected_label.grid(row=0, column=1, padx=10)
    listbox_selected = tk.Listbox(main_frame)
    listbox_selected.grid(row=1, column=1, padx=10, pady=10, sticky="ns")

    for col in dataframe.columns:
        listbox_available.insert(tk.END, col)

    selected_columns = []

    def move_to_selected():
        selected_items = listbox_available.curselection()
        for item in selected_items:
            col = listbox_available.get(item)
            if col not in selected_columns:
                selected_columns.append(col)
                listbox_selected.insert(tk.END, col)

    def clear_selected():
        selected_columns.clear()
        listbox_selected.delete(0, tk.END)

    def save_changes():
        global original_dataframe
        original_dataframe = dataframe[selected_columns]
        update_treeview(original_dataframe, main_tree)
        top.destroy()

    button_frame = ttk.Frame(main_frame)
    button_frame.grid(row=1, column=2, padx=10, pady=10, sticky="ns")

    add_button = ttk.Button(button_frame, text="Add ->", command=move_to_selected)
    add_button.pack(side=tk.TOP, pady=5)

    clear_button = ttk.Button(button_frame, text="Clear", command=clear_selected)
    clear_button.pack(side=tk.TOP, pady=5)

    save_button = ttk.Button(button_frame, text="Save", command=save_changes)
    save_button.pack(side=tk.TOP, pady=5)

    main_frame.columnconfigure(0, weight=1)
    main_frame.columnconfigure(1, weight=1)
    main_frame.columnconfigure(2, weight=0)
    main_frame.rowconfigure(1, weight=1)

    top.mainloop()


def string_slicing(dataframe, column):
    pass

def binary_encoding(dataframe, column):
    pass

def numeric_encoding(dataframe, column):
    pass

# Funcțiile existente (asigură-te că toate sunt definite)
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
