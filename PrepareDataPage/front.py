import tkinter as tk
from tkinter import ttk
import pandas as pd
from AnalyzeData.front import open_analysis_page

def open_prepare_data_page(user_id, dataframe):
    prepare_window = tk.Toplevel()
    prepare_window.title("Preparare Date")
    prepare_window.geometry("900x700")

        # Main frame to hold everything
    main_frame = ttk.Frame(prepare_window, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for TreeView and Scrollbars
    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)  # Ensure padding to see the frame's extent

    # TreeView setup
    tree = ttk.Treeview(tree_frame, columns=dataframe.columns.tolist(), show="headings")
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)  # You may need to adjust widths based on actual content
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Vertical Scrollbar
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=vsb.set)

    # Horizontal Scrollbar
    hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.configure(xscrollcommand=hsb.set)

    # Ensure data is loaded into the TreeView
    for index, row in dataframe.iterrows():
        tree.insert("", tk.END, values=list(row))

    # Frame for listboxes and buttons
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    # Listboxes for column selection
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

    for col in dataframe.select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe.select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)

    # Buttons for preprocessing
    preprocess_frame = ttk.Frame(main_frame)
    preprocess_frame.pack(fill=tk.X, expand=False, side=tk.TOP)

    ttk.Button(preprocess_frame, text="Normalizează").pack(side=tk.LEFT, padx=5, pady=5)
    ttk.Button(preprocess_frame, text="Standardizează").pack(side=tk.LEFT, padx=5, pady=5)

    # Entry and Combobox for preprocessing
    entry = ttk.Entry(preprocess_frame)
    entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

    methods = ['Normalizează', 'Standardizează', 'Umple goluri']
    method_cb = ttk.Combobox(preprocess_frame, values=methods)
    method_cb.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)

    ttk.Button(preprocess_frame, text="Aplică Metoda", command=lambda: apply_method(entry.get(), method_cb.get(), dataframe)).pack(side=tk.LEFT, padx=10, pady=10)

    execute_button = ttk.Button(preprocess_frame, text="Analizeaza datele", command=lambda: open_analysis_page(user_id, dataframe))
    execute_button.pack(side=tk.LEFT, padx=10, pady=10)

    prepare_window.mainloop()

def apply_method(column, method, dataframe):
    print(f"Aplică metoda {method} pe coloana {column}")
    # Add specific preprocessing logic here

