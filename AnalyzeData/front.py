import tkinter as tk
from tkinter import ttk
from AnalyzeData.functions import save_csv, display_analysis_results, assisted_modeling, analyze_data, apply_method_to_all_columns

def open_analyze_data_page(user_id, dataframe):
    analyze_window = tk.Toplevel()
    analyze_window.title("Analiza Datelor")
    analyze_window.state("zoomed")

    main_frame = ttk.Frame(analyze_window, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for TreeView and Scrollbars
    tree_frame = ttk.Frame(main_frame, height=200)
    tree_frame.pack(fill=tk.BOTH, expand=False, pady=20, padx=20)

    tree = ttk.Treeview(tree_frame, columns=dataframe.columns.tolist(), show="headings")
    for col in dataframe.columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.configure(xscrollcommand=hsb.set)

    for index, row in dataframe.iterrows():
        tree.insert("", tk.END, values=list(row))

    # Setup listboxes and entry for column selection and method application
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    ttk.Label(list_frame, text="Coloane numerice").pack(side=tk.LEFT, padx=10)
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    num_methods = ['Normalizează', 'Standardizează']
    num_listbox.bind('<<ListboxSelect>>', lambda event: update_entry_and_methods(num_listbox, entry, method_cb, num_methods))

    ttk.Label(list_frame, text="Coloane alfanumerice").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ['Codifică', 'Umple goluri']
    alpha_listbox.bind('<<ListboxSelect>>', lambda event: update_entry_and_methods(alpha_listbox, entry, method_cb, alpha_methods))

    for col in dataframe.select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe.select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)

    # Numeric columns analysis setup
    numeric_methods_frame = ttk.Frame(main_frame)
    numeric_methods_frame.pack(fill=tk.X, pady=10)

    ttk.Label(numeric_methods_frame, text="Metodă pentru toate coloanele numerice:").pack(side=tk.LEFT, padx=10)
    numeric_method_cb = ttk.Combobox(numeric_methods_frame, values=['Normalizează', 'Standardizează'])
    numeric_method_cb.pack(side=tk.LEFT, padx=10)
    apply_numeric_method_button = ttk.Button(numeric_methods_frame, text="Aplică Metodă Numerică", command=lambda: apply_method_to_all_columns(dataframe, numeric_method_cb.get(), 'numeric'))
    apply_numeric_method_button.pack(side=tk.LEFT, padx=10)

    # Alphanumeric columns analysis setup
    alpha_methods_frame = ttk.Frame(main_frame)
    alpha_methods_frame.pack(fill=tk.X, pady=10)

    ttk.Label(alpha_methods_frame, text="Metodă pentru toate coloanele alfanumerice:").pack(side=tk.LEFT, padx=10)
    alpha_method_cb = ttk.Combobox(alpha_methods_frame, values=['Codifică', 'Umple goluri'])
    alpha_method_cb.pack(side=tk.LEFT, padx=10)
    apply_alpha_method_button = ttk.Button(alpha_methods_frame, text="Aplică Metodă Alfanumerică", command=lambda: apply_method_to_all_columns(dataframe, alpha_method_cb.get(), 'alpha'))
    apply_alpha_method_button.pack(side=tk.LEFT, padx=10)


    control_frame = ttk.Frame(main_frame)
    control_frame.pack(fill=tk.X, pady=10)

    entry = ttk.Entry(control_frame)
    entry.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.X)

    method_cb = ttk.Combobox(control_frame)
    method_cb.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    apply_button = ttk.Button(control_frame, text="Folosește metoda pentru coloană", command=lambda: apply_method(entry.get(), method_cb.get(), dataframe))
    apply_button.pack(side=tk.LEFT, padx=10)

        # Bottom control buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    analyze_button = ttk.Button(button_frame, text="Analizează datele", command=lambda: analyze_data(dataframe))
    analyze_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    save_button = ttk.Button(button_frame, text="Salvează datele", command=lambda: save_csv(dataframe, user_id))
    save_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    assisted_modeling_button = ttk.Button(button_frame, text="Modelare asistată", command=lambda: assisted_modeling(dataframe))
    assisted_modeling_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    display_results_button = ttk.Button(button_frame, text="Afișare rezultate", command=lambda: display_analysis_results(dataframe))
    display_results_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)


    analyze_window.mainloop()

def update_entry_and_methods(listbox, entry, method_cb, methods):
    selection = listbox.curselection()
    if selection:
        entry.delete(0, tk.END)
        entry.insert(0, listbox.get(selection[0]))
        method_cb['values'] = methods
        method_cb.current(0)

def apply_method(selected_column, method, dataframe):
    print(f"Applying {method} to {selected_column}. Placeholder for method application.")
