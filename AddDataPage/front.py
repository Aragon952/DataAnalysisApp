import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
from PrepareDataPage.front import open_prepare_data_page

def open_add_data_page(user_id):
    add_data_window = tk.Toplevel()
    add_data_window.title("Adaugare date")
    add_data_window.geometry("800x600")

    # Crearea DataFrame-ului
    dataframe = pd.DataFrame(np.random.randint(1, 100, size=(5, 5)), columns=['Col1', 'Col2', 'Col3', 'Col4', 'Col5'])

    # Crearea unui frame pentru TreeView și Scrollbars
    frame = ttk.Frame(add_data_window, padding="3 3 12 12")
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

    # Butonul de adăugare date și preprocesare
    add_button = ttk.Button(add_data_window, text="Adaugare set de date")
    add_button.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

    # Buton pentru a deschide fereastra de preprocesare
    prep_button = ttk.Button(add_data_window, text="Preprocesare Date", command=lambda: open_prepare_data_page(user_id, dataframe))
    prep_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
    

    add_data_window.mainloop()
