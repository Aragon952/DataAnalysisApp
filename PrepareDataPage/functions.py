import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import os
import sqlite3
import pandas as pd
from fancyimpute import IterativeImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from scipy.stats import zscore

# Metode apelate in functions

def update_treeview(dataframe, tree_frame):
    # Îndepărtăm orice widgets existente din tree_frame
    for widget in tree_frame.winfo_children():
        widget.destroy()

    # Creăm un nou Treeview în tree_frame
    main_tree = ttk.Treeview(tree_frame, columns=dataframe.columns.tolist(), show="headings")

    # Setăm antetele și lățimea coloanelor
    for col in dataframe.columns:
        main_tree.heading(col, text=col)
        main_tree.column(col, width=100)

    # Adăugăm un scrollbar vertical
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=main_tree.yview)
    vsb.pack(side='right', fill='y')
    main_tree.configure(yscrollcommand=vsb.set)

    # Adăugăm un scrollbar orizontal
    hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=main_tree.xview)
    hsb.pack(side='bottom', fill='x')
    main_tree.configure(xscrollcommand=hsb.set)

    # Adăugăm datele
    for index, row in dataframe.iterrows():
        main_tree.insert("", tk.END, values=list(row))

    # Ambalăm main_tree în tree_frame
    main_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

def save_file_info_to_database(user_id, filename, filepath):
    conn = sqlite3.connect('DataAnalysisApp/database.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO user_history (user_id, file_history, file_name)
        VALUES (?, ?, ?)
    ''', (user_id, filepath, filename))
    conn.commit()
    conn.close()

def get_value_from_user(prompt):
    # Creează un dialog Toplevel
    dialog_root = tk.Toplevel()
    dialog_root.title("Input")

    # Adaugă un Entry widget pentru a permite utilizatorului să introducă o valoare
    entry = tk.Entry(dialog_root)
    entry.pack(padx=20, pady=20)

    # Funcția care va fi apelată la apăsarea butonului OK
    def on_ok():
        user_value = entry.get()  # Extrage valoarea introdusă de utilizator
        dialog_root.user_value = user_value  # Stochează valoarea într-un atribut al fereastrei
        dialog_root.destroy()  # Închide fereastra după ce valoarea a fost preluată

    # Adaugă butoane pentru confirmare
    ok_button = tk.Button(dialog_root, text="OK", command=on_ok)
    ok_button.pack(pady=10)

    # Rulează loop-ul principal al dialogului
    dialog_root.mainloop()

    # Returnează valoarea introdusă de utilizator după închiderea ferestrei
    return dialog_root.user_value if hasattr(dialog_root, 'user_value') else None

def update_listboxes(dataframe, num_listbox, alpha_listbox):
    # Curățăm întâi conținutul actual al listbox-urilor
    num_listbox.delete(0, tk.END)
    alpha_listbox.delete(0, tk.END)

    # Adăugăm coloanele noi în listbox-uri
    # Identificăm coloanele numerice și alfanumerice
    numeric_columns = dataframe.select_dtypes(include='number').columns
    alfanumeric_columns = dataframe.select_dtypes(exclude='number').columns

    # Actualizăm listbox-ul pentru coloanele numerice
    for col in numeric_columns:
        num_listbox.insert(tk.END, col)

    # Actualizăm listbox-ul pentru coloanele alfanumerice
    for col in alfanumeric_columns:
        alpha_listbox.insert(tk.END, col)

def detect_outliers_percentile(column_data, threshold):
    lower_limit = column_data.quantile(threshold / 100.0)
    upper_limit = column_data.quantile(1 - threshold / 100.0)
    return (column_data < lower_limit) | (column_data > upper_limit)

def detect_outliers_zscore(column_data, z_threshold):
    zs = zscore(column_data)
    return (abs(zs) > z_threshold)

# Metode pentru toate coloanele

def select_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    top = tk.Toplevel()
    top.title("Select Columns")
    top.grab_set()  # Asigură că inputul este capturat de această fereastră

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    available_label = ttk.Label(main_frame, text="Available Columns")
    available_label.grid(row=0, column=0, padx=10)
    listbox_available = tk.Listbox(main_frame, selectmode=tk.MULTIPLE)
    listbox_available.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

    # Încărcăm coloanele disponibile în listbox
    for col in dataframe_container['dataframe'].columns:
        listbox_available.insert(tk.END, col)

    # Funcție pentru butonul de selectare
    def keep_selected_columns():
        selected_indices = listbox_available.curselection()
        selected_columns = [listbox_available.get(i) for i in selected_indices]
        dataframe = dataframe_container['dataframe']
        
        if selected_columns:
            new_dataframe = dataframe[selected_columns]
            dataframe_container['dataframe'] = new_dataframe
            update_treeview(dataframe_container['dataframe'], tree_frame)
            update_listboxes(dataframe_container['dataframe'], num_listbox, alpha_listbox)
            messagebox.showinfo("Success", "Columns selected successfully.", parent=top)
            top.destroy()
        else:
            messagebox.showwarning("No selection", "No columns selected to keep.", parent=top)

    # Buton pentru păstrarea coloanelor selectate
    select_button = ttk.Button(main_frame, text="Keep Selected Columns", command=keep_selected_columns)
    select_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.mainloop()

def remove_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    top = tk.Toplevel()
    top.title("Remove Columns")
    top.grab_set()  # Asigură că inputul este capturat de această fereastră

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    available_label = ttk.Label(main_frame, text="Available Columns")
    available_label.grid(row=0, column=0, padx=10)
    listbox_available = tk.Listbox(main_frame, selectmode=tk.MULTIPLE)
    listbox_available.grid(row=1, column=0, padx=10, pady=10, sticky="ns")

    # Încărcăm coloanele disponibile în listbox
    for col in dataframe_container['dataframe'].columns:
        listbox_available.insert(tk.END, col)

    # Funcție pentru butonul de eliminare
    def remove_selected_columns():
        selected_indices = listbox_available.curselection()
        selected_columns = [listbox_available.get(i) for i in selected_indices]
        dataframe = dataframe_container['dataframe']
        
        if selected_columns:
            dataframe.drop(columns=selected_columns, inplace=True)
            dataframe_container['dataframe'] = dataframe
            update_treeview(dataframe_container['dataframe'], tree_frame)
            update_listboxes(dataframe_container['dataframe'], num_listbox, alpha_listbox)
            messagebox.showinfo("Success", "Columns removed successfully.", parent=top)
            top.destroy()
        else:
            messagebox.showwarning("No selection", "No columns selected for removal.", parent=top)

    # Buton pentru eliminarea coloanelor selectate
    remove_button = ttk.Button(main_frame, text="Remove Selected Columns", command=remove_selected_columns)
    remove_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

    top.protocol("WM_DELETE_WINDOW", top.destroy)
    top.mainloop()

# Metode pentru o coloana

def select_column(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    pass

def remove_column(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    pass

# Metode pentru toate coloanele numerice

def group_all_numeric_data(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    top = tk.Toplevel()
    top.title("Group Data")
    top.grab_set()

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))
    top.columnconfigure(0, weight=1)
    top.rowconfigure(0, weight=1)

    # Opțiuni pentru selectarea coloanelor
    tk.Label(main_frame, text="Select first column:").grid(row=0, column=0, padx=10, pady=5)
    column1_combobox = ttk.Combobox(main_frame, values=list(dataframe_container['dataframe'].columns))
    column1_combobox.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(main_frame, text="Select second column:").grid(row=1, column=0, padx=10, pady=5)
    column2_combobox = ttk.Combobox(main_frame, values=list(dataframe_container['dataframe'].columns))
    column2_combobox.grid(row=1, column=1, padx=10, pady=5)

    # Opțiuni pentru operații
    operations = {"Add": "+", "Subtract": "-", "Multiply": "*", "Divide": "/"}
    tk.Label(main_frame, text="Select operation:").grid(row=2, column=0, padx=10, pady=5)
    operation_combobox = ttk.Combobox(main_frame, values=list(operations.keys()))
    operation_combobox.grid(row=2, column=1, padx=10, pady=5)

    # Opțiune pentru denumirea noii coloane
    tk.Label(main_frame, text="Enter new column name (optional):").grid(row=3, column=0, padx=10, pady=5)
    new_column_name_entry = ttk.Entry(main_frame)
    new_column_name_entry.grid(row=3, column=1, padx=10, pady=5)

    # Funcție pentru aplicarea grupării
    def apply_grouping():
        col1 = column1_combobox.get()
        col2 = column2_combobox.get()
        operation = operations[operation_combobox.get()]
        new_column_name = new_column_name_entry.get()

        if not new_column_name:
            new_column_name = f"{col1} {operation} {col2}"

        if operation == "+":
            dataframe_container['dataframe'][new_column_name] = dataframe_container['dataframe'][col1] + dataframe_container['dataframe'][col2]
        elif operation == "-":
            dataframe_container['dataframe'][new_column_name] = dataframe_container['dataframe'][col1] - dataframe_container['dataframe'][col2]
        elif operation == "*":
            dataframe_container['dataframe'][new_column_name] = dataframe_container['dataframe'][col1] * dataframe_container['dataframe'][col2]
        elif operation == "/":
            dataframe_container['dataframe'][new_column_name] = dataframe_container['dataframe'][col1] / dataframe_container['dataframe'][col2]

        update_treeview(dataframe_container['dataframe'], tree_frame)
        update_listboxes(dataframe_container['dataframe'], num_listbox, alpha_listbox)
        top.destroy()

    # Buton pentru aplicarea grupării
    apply_button = ttk.Button(main_frame, text="Apply", command=apply_grouping)
    apply_button.grid(row=4, column=0, columnspan=2, pady=10)

    top.mainloop()


# Functii pentru toate coloanele alfanumerice
def group_all_alfanumeric_data(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    top = tk.Toplevel()
    top.title("Group Alphanumeric Columns")
    top.grab_set()

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Selectarea coloanelor
    tk.Label(main_frame, text="Select first column:").pack(padx=10, pady=5)
    column1_combobox = ttk.Combobox(main_frame, values=list(dataframe_container['dataframe'].select_dtypes(include=[object]).columns))
    column1_combobox.pack(padx=10, pady=5, fill='x')

    tk.Label(main_frame, text="Select second column:").pack(padx=10, pady=5)
    column2_combobox = ttk.Combobox(main_frame, values=list(dataframe_container['dataframe'].select_dtypes(include=[object]).columns))
    column2_combobox.pack(padx=10, pady=5, fill='x')

    # Separator input
    tk.Label(main_frame, text="Enter separator (optional):").pack(padx=10, pady=5)
    separator_entry = ttk.Entry(main_frame)
    separator_entry.pack(padx=10, pady=5, fill='x')

    # New column name input
    tk.Label(main_frame, text="Enter new column name (optional):").pack(padx=10, pady=5)
    new_column_name_entry = ttk.Entry(main_frame)
    new_column_name_entry.pack(padx=10, pady=5, fill='x')

    # Funcția care aplică gruparea
    def apply_grouping():
        col1 = column1_combobox.get()
        col2 = column2_combobox.get()
        separator = separator_entry.get()
        new_column_name = new_column_name_entry.get()

        if not new_column_name:
            new_column_name = f"{col1}{separator}{col2}"

        if col1 and col2:
            dataframe = dataframe_container['dataframe']
            dataframe[new_column_name] = dataframe[col1].astype(str) + separator + dataframe[col2].astype(str)
            
            dataframe_container['dataframe'] = dataframe
            update_treeview(dataframe_container['dataframe'], tree_frame)
            update_listboxes(dataframe_container['dataframe'], num_listbox, alpha_listbox)
            messagebox.showinfo("Success", "Columns have been successfully grouped.", parent=top)
            top.destroy()
        else:
            messagebox.showerror("Error", "Please select both columns.", parent=top)

    apply_button = ttk.Button(main_frame, text="Apply Grouping", command=apply_grouping)
    apply_button.pack(pady=10)

    top.mainloop()


# Metode pentru o coloana numerica


# Metode pentru o coloana alfanumerica


# Metode pentru o coloana sau toate coloanele numerice

def fill_numeric_nan_with_median(dataframe_container, tree_frame, columns=None):
    def apply_fill(selected_columns):
        if not selected_columns:
            messagebox.showerror("Error", "No columns selected. Please select at least one column.")
            return
        
        dataframe = dataframe_container['dataframe']
        for column in selected_columns:
            if column in dataframe.columns:
                median_value = dataframe[column].median()
                dataframe.loc[:, column].fillna(median_value, inplace=True)

        dataframe_container['dataframe'] = dataframe
        update_treeview(dataframe_container['dataframe'], tree_frame)
        messagebox.showinfo("Success", "NaN values filled with median for selected columns.")

    if columns is not None:
        # If columns are provided directly, apply the fill operation immediately
        apply_fill(columns)
        return

    top = tk.Toplevel()
    top.title("Fill NaN with Median for Numeric Columns")

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    numeric_columns = dataframe_container['dataframe'].select_dtypes(include=['number']).columns
    for col in numeric_columns:
        listbox.insert(tk.END, col)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    apply_button = ttk.Button(main_frame, text="Apply Fill to Selected Columns", command=lambda: apply_fill([listbox.get(i) for i in listbox.curselection()]))
    apply_button.pack(pady=10)

    top.mainloop()


def fill_all_numeric_nan_with_mean(dataframe_container, tree_frame):
    dataframe = dataframe_container["dataframe"]
    numeric_columns = dataframe.select_dtypes(include=['number']).columns
    for column in numeric_columns:
        # Use .loc to ensure you are modifying the DataFrame directly
        mean_value = dataframe[column].mean()
        dataframe.loc[:, column].fillna(mean_value, inplace=True)
    update_treeview(dataframe, tree_frame)

def fill_all_numeric_nan_with_specific_numeric_value(dataframe_container, tree_frame):
    # Creează o fereastră de top-level pentru dialog
    top = tk.Toplevel()
    top.title("Fill Missing Values")

    # Setează fereastra să nu permită interacțiunea cu fereastra principală
    top.grab_set()

    # Textul de informare pentru utilizator
    label = ttk.Label(top, text="Please enter a specific value to fill missing values in numeric columns:")
    label.pack(padx=20, pady=10)

    # Câmp pentru valoarea specificată de utilizator
    value_entry = ttk.Entry(top)
    value_entry.pack(padx=20, pady=10)

    # Funcția care va fi apelată la apăsarea butonului 'OK'
    def on_ok():
        specific_value = value_entry.get()
        try:
            # Convertim valoarea primită într-un float
            specific_value = float(specific_value)
            # Aplicăm valoarea specifică pentru a umple valorile NaN în coloanele numerice
            numeric_columns = dataframe_container["dataframe"].select_dtypes(include='number').columns
            for column in numeric_columns:
                dataframe_container["dataframe"][column].fillna(specific_value, inplace=True)
            # Actualizăm interfața
            update_treeview(dataframe_container["dataframe"], tree_frame)
            top.destroy()
        except ValueError:
            ttk.Label(top, text="Invalid input, please enter a numeric value.").pack(padx=20, pady=20)

    # Buton pentru confirmarea valorii
    ok_button = ttk.Button(top, text="OK", command=on_ok)
    ok_button.pack(pady=20)

    # Rulează loop-ul principal al dialogului
    top.mainloop()

def mice_imputation_all_numeric(dataframe_container, tree_frame):
    # Extrage DataFrame-ul din container
    dataframe = dataframe_container["dataframe"]

    # Filtrăm doar coloanele numerice
    numeric_data = dataframe.select_dtypes(include=['number'])

    # Aplicăm imputarea MICE
    try:
        imputer = IterativeImputer()
        imputed_data = imputer.fit_transform(numeric_data)
        imputed_df = pd.DataFrame(imputed_data, columns=numeric_data.columns)

        # Înlocuim coloanele numerice în DataFrame-ul original cu versiunea imputată
        for col in numeric_data.columns:
            dataframe[col] = imputed_df[col]

        # Actualizează DataFrame-ul în container
        dataframe_container['dataframe'] = dataframe

        # Actualizează interfața grafică
        update_treeview(dataframe_container["dataframe"], tree_frame)
    except Exception as e:
        messagebox.showerror("Error during MICE Imputation", str(e))
        return

    messagebox.showinfo("Imputation Complete", "Missing values have been imputed successfully.")

def standardize_all_numeric(dataframe_container, tree_frame):
    dataframe = dataframe_container['dataframe']
    numeric_columns = dataframe.select_dtypes(include=['number']).columns
    
    try:
        # Aplicăm StandardScaler pentru a standardiza coloanele numerice
        scaler = StandardScaler()
        dataframe[numeric_columns] = scaler.fit_transform(dataframe[numeric_columns])
        
        # Actualizăm DataFrame-ul în container
        dataframe_container['dataframe'] = dataframe
        
        # Actualizează interfața grafică
        update_treeview(dataframe_container['dataframe'], tree_frame)
        
    except Exception as e:
        messagebox.showerror("Error during Standardization", str(e))
        return
    
    messagebox.showinfo("Standardization Complete", "Numeric columns have been standardized successfully.")

def normalize_all_numeric(dataframe_container, tree_frame):
    dataframe = dataframe_container['dataframe']
    numeric_columns = dataframe.select_dtypes(include=['number']).columns
    
    try:
        # Aplicăm MinMaxScaler pentru a normaliza coloanele numerice
        scaler = MinMaxScaler()
        dataframe[numeric_columns] = scaler.fit_transform(dataframe[numeric_columns])
        
        # Actualizăm DataFrame-ul în container
        dataframe_container['dataframe'] = dataframe
        
        # Actualizează interfața grafică
        update_treeview(dataframe_container['dataframe'], tree_frame)
        
    except Exception as e:
        messagebox.showerror("Error during Normalization", str(e))
        return
    
    messagebox.showinfo("Normalization Complete", "Numeric columns have been normalized successfully.")

def handle_outliers_all_numeric(dataframe_container, tree_frame):
    top = tk.Toplevel()
    top.title("Handle Outliers")
    top.grab_set()  # Asigură că inputul este capturat de această fereastră

    # Definiția funcției de aplicare a tratării outlierilor
    def apply_outlier_handling(dataframe_container, method, action, threshold, tree_frame):
        dataframe = dataframe_container['dataframe']
        numeric_columns = dataframe.select_dtypes(include=['number']).columns  # Selectăm doar coloanele numerice

        try:
            threshold = float(threshold)  # Conversie threshold la float
            for column in numeric_columns:
                if method == 'percentile':
                    outlier_mask = detect_outliers_percentile(dataframe[column], threshold)
                elif method == 'zscore':
                    outlier_mask = detect_outliers_zscore(dataframe[column], threshold)

                if action == 'remove':
                    dataframe = dataframe[~outlier_mask]
                elif action == 'nan':
                    dataframe.loc[outlier_mask, column] = float('nan')

            dataframe_container['dataframe'] = dataframe
            update_treeview(dataframe_container['dataframe'], tree_frame)
            top.destroy()
            messagebox.showinfo("Success", "Outliers handled successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Buton pentru aplicarea tratării outlierilor
    def on_apply_button_click():
        method = method_var.get()
        action = action_var.get()
        threshold = threshold_entry.get()
        apply_outlier_handling(dataframe_container, method, action, threshold, tree_frame)

    # Definițiile interfeței utilizator
    method_var = tk.StringVar(value="percentile")
    action_var = tk.StringVar(value="nan")
    tk.Label(top, text="Select method to detect outliers:").pack(anchor='w', padx=10, pady=5)
    ttk.Radiobutton(top, text="Percentile", variable=method_var, value="percentile").pack(anchor='w', padx=20)
    ttk.Radiobutton(top, text="Z-Score", variable=method_var, value="zscore").pack(anchor='w', padx=20)
    tk.Label(top, text="Action on detection:").pack(anchor='w', padx=10, pady=5)
    ttk.Radiobutton(top, text="Remove Row", variable=action_var, value="remove").pack(anchor='w', padx=20)
    ttk.Radiobutton(top, text="Replace with NaN", variable=action_var, value="nan").pack(anchor='w', padx=20)
    tk.Label(top, text="Enter threshold value (Percentile [0-100] or Z-Score):").pack(anchor='w', padx=10, pady=5)
    threshold_entry = ttk.Entry(top)
    threshold_entry.pack(padx=20, pady=5, fill='x')
    apply_button = ttk.Button(top, text="Apply", command=on_apply_button_click)
    apply_button.pack(pady=10)

    top.mainloop()

# Metode pentru o coloana sau toate coloanele alfanumerice

def fill_all_alfanumeric_nan_with_specific_alpha_value(dataframe_container, tree_frame):
    top = tk.Toplevel()
    top.title("Fill All Alphanumeric NaNs with a Specific Value")
    top.grab_set()

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Label și entry pentru valoarea specifică
    tk.Label(main_frame, text="Enter the value to fill all NaNs:").pack(padx=10, pady=5)
    value_entry = ttk.Entry(main_frame)
    value_entry.pack(padx=10, pady=5, fill='x')

    # Funcția care aplică umplerea NaN-urilor
    def apply_fill():
        value = value_entry.get()
        if value:
            dataframe = dataframe_container['dataframe']
            alfanumeric_columns = dataframe.select_dtypes(include=[object]).columns
            for column in alfanumeric_columns:
                dataframe[column] = dataframe[column].fillna(value)
            dataframe_container['dataframe'] = dataframe
            update_treeview(dataframe_container['dataframe'], tree_frame)
            messagebox.showinfo("Success", "All NaN values in alphanumeric columns have been filled.", parent=top)
            top.destroy()
        else:
            messagebox.showerror("Error", "Please enter a value to fill NaNs.", parent=top)

    apply_button = ttk.Button(main_frame, text="Apply Fill", command=apply_fill)
    apply_button.pack(pady=10)

    top.mainloop()

def string_slicing_all_alfanumeric(dataframe_container, tree_frame):
    top = tk.Toplevel()
    top.title("String Slicing on Alphanumeric Columns")
    top.grab_set()

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Opțiuni pentru selectarea metodei de slicing
    method_var = tk.StringVar(value="range")  # Default slicing method
    ttk.Radiobutton(main_frame, text="Slice by Range", variable=method_var, value="range").pack(anchor='w', padx=20)
    ttk.Radiobutton(main_frame, text="Slice from End", variable=method_var, value="from_end").pack(anchor='w', padx=20)
    ttk.Radiobutton(main_frame, text="Remove Substring", variable=method_var, value="remove_substring").pack(anchor='w', padx=20)

    # Input pentru indicele de start și sfârșit
    tk.Label(main_frame, text="Start index:").pack(padx=10, pady=5)
    start_entry = ttk.Entry(main_frame)
    start_entry.pack(padx=10, pady=5, fill='x')

    tk.Label(main_frame, text="End index (for range slicing):").pack(padx=10, pady=5)
    end_entry = ttk.Entry(main_frame)
    end_entry.pack(padx=10, pady=5, fill='x')

    # Entry pentru substring (pentru Remove Substring)
    tk.Label(main_frame, text="Substring to remove (for remove substring):").pack(padx=10, pady=5)
    substring_entry = ttk.Entry(main_frame)
    substring_entry.pack(padx=10, pady=5, fill='x')

    # Funcția care aplică slicing-ul
    def apply_slicing():
        method = method_var.get()
        start = start_entry.get()
        end = end_entry.get()
        substring = substring_entry.get()

        try:
            for column in dataframe_container['dataframe'].select_dtypes(include=[object]).columns:
                if method == 'range':
                    dataframe_container['dataframe'][column] = dataframe_container['dataframe'][column].str[int(start):int(end)]
                elif method == 'from_end':
                    dataframe_container['dataframe'][column] = dataframe_container['dataframe'][column].str[-int(start):]
                elif method == 'remove_substring':
                    dataframe_container['dataframe'][column] = dataframe_container['dataframe'][column].str.replace(substring, '', regex=False)
            
            update_treeview(dataframe_container['dataframe'], tree_frame)
            messagebox.showinfo("Success", "String slicing applied successfully.", parent=top)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}", parent=top)

        top.destroy()

    apply_button = ttk.Button(main_frame, text="Apply Slicing", command=apply_slicing)
    apply_button.pack(pady=10)

    top.mainloop()

def binary_encoding_all_alfanumeric(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    dataframe = dataframe_container['dataframe']
    alfanumeric_columns = dataframe.select_dtypes(include=[object]).columns

    for column in alfanumeric_columns:
        dummies = pd.get_dummies(dataframe[column], prefix=column)
        dataframe = pd.concat([dataframe, dummies], axis=1)
        dataframe.drop(column, axis=1, inplace=True)  # Eliminăm coloana originală

    dataframe_container['dataframe'] = dataframe
    update_treeview(dataframe_container['dataframe'], tree_frame)
    update_listboxes(dataframe_container['dataframe'], num_listbox, alpha_listbox)

def numeric_encoding_all_alfanumeric(dataframe_container, tree_frame, num_listbox, alpha_listbox):
    dataframe = dataframe_container['dataframe']
    alfanumeric_columns = dataframe.select_dtypes(include=[object]).columns

    for column in alfanumeric_columns:
        # Codificăm fiecare valoare unică într-o valoare numerică
        dataframe[column] = pd.factorize(dataframe[column])[0]

    dataframe_container['dataframe'] = dataframe
    update_treeview(dataframe_container['dataframe'], tree_frame)
    update_listboxes(dataframe_container['dataframe'], num_listbox, alpha_listbox)


# Alte metode apelate in front

def save_csv(dataframe_container, user_id):
    dataframe = dataframe_container["dataframe"]
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
