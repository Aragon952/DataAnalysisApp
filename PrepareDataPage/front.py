import tkinter as tk
from tkinter import ttk
import pandas as pd
from AnalyzeData.front import open_analysis_page

def open_prepare_data_page(user_id, dataframe):
    # Crearea unei noi ferestre
    prepare_window = tk.Toplevel()
    prepare_window.title("Preparare Date")
    prepare_window.geometry("900x700")

    # Crearea unui frame pentru TreeView și Scrollbars
    frame = ttk.Frame(prepare_window, padding="3 3 12 12")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Specificarea coloanelor cu identificatori clari și utilizarea acestora
    tree = ttk.Treeview(frame, columns=dataframe.columns.tolist(), show="headings")
    for col in dataframe.columns:
        tree.heading(col, text=col)  # Asigură-te că identificatorii sunt corect utilizați aici
        tree.column(col, width=100)

    # Încărcarea datelor în Treeview
    for index, row in dataframe.iterrows():
        tree.insert("", tk.END, values=row.tolist())

    tree.pack(expand=True, fill=tk.BOTH)

    # Adăugarea Scrollbar-ului vertical
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Listele pentru coloane numerice și alfanumerice
    numeric_cols = dataframe.select_dtypes(include='number').columns.tolist()
    alpha_cols = dataframe.select_dtypes(exclude='number').columns.tolist()

    list_frame = ttk.Frame(prepare_window, padding="3 3 12 12")
    list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)

    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.grid(row=0, column=0, padx=10, pady=10)
    for col in numeric_cols:
        num_listbox.insert(tk.END, col)

    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.grid(row=0, column=2, padx=10, pady=10)
    for col in alpha_cols:
        alpha_listbox.insert(tk.END, col)

    # Adăugarea butoanelor pentru preprocesare
    ttk.Button(list_frame, text="Normalizează").grid(row=1, column=0)
    ttk.Button(list_frame, text="Standardizează").grid(row=1, column=2)

    # Entry și Combobox pentru preprocesare specifică
    entry = ttk.Entry(prepare_window)
    entry.grid(row=2, column=0, padx=10, pady=10, sticky='ew')

    methods = ['Normalizează', 'Standardizează', 'Umple goluri']
    method_cb = ttk.Combobox(prepare_window, values=methods)
    method_cb.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

    ttk.Button(prepare_window, text="Aplică Metoda", command=lambda: apply_method(entry.get(), method_cb.get(), dataframe)).grid(row=2, column=2, padx=10, pady=10)
    
    execute_button = ttk.Button(prepare_window, text="Analizeaza datele", command=lambda: open_analysis_page(user_id, dataframe))
    execute_button.grid(row=3, column=0, padx=10, pady=10, sticky='ew')

    prepare_window.mainloop()

def apply_method(column, method, dataframe):
    print(f"Aplică metoda {method} pe coloana {column}")
    # Aici vei adăuga logica specifică pentru fiecare metodă de preprocesare


