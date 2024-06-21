import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import os
import sqlite3

def update_methods_for_one_column(listbox, entry, method_cb, methods):
    selection = listbox.curselection()
    if selection:
        entry.delete(0, tk.END)
        entry.insert(0, listbox.get(selection[0]))
        method_cb['values'] = methods  # Update the methods in the combobox

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

def select_columns(dataframe, tree_frame, dataframe_container, num_listbox, alpha_listbox):
    top = tk.Toplevel()
    top.title("Select Columns")

    def on_closing():
        top.destroy()

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
        dataframe_container['dataframe'] = original_dataframe
        update_treeview(original_dataframe, tree_frame)
        update_listboxes(original_dataframe, num_listbox, alpha_listbox)
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

    top.protocol("WM_DELETE_WINDOW", on_closing)

    top.mainloop()


def string_slicing(dataframe, column):
    pass

def binary_encoding(dataframe, column):
    pass

def numeric_encoding(dataframe, column):
    pass

# Funcțiile existente (asigură-te că toate sunt definite)
def fill_na_with_median(dataframe_container, tree_frame):
    dataframe = dataframe_container["dataframe"]
    numeric_columns = dataframe.select_dtypes(include=['number']).columns
    for column in numeric_columns:
        # Use .loc to ensure you are modifying the DataFrame directly
        median_value = dataframe[column].median()
        dataframe.loc[:, column].fillna(median_value, inplace=True)
    update_treeview(dataframe, tree_frame)

def fill_na_with_mean(dataframe_container, tree_frame):
    dataframe = dataframe_container["dataframe"]
    numeric_columns = dataframe.select_dtypes(include=['number']).columns
    for column in numeric_columns:
        # Use .loc to ensure you are modifying the DataFrame directly
        mean_value = dataframe[column].mean()
        dataframe.loc[:, column].fillna(mean_value, inplace=True)
    update_treeview(dataframe, tree_frame)

def fill_na_with_specific_value(dataframe_container, tree_frame):
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
