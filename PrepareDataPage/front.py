import tkinter as tk
from tkinter import ttk
from AnalyzeData.front import open_analyze_data_page
from PrepareDataPage.functions import update_entry_and_methods, save_csv, apply_method

numeric_values_methods_list = ['Selectare Coloane','FillNa cu mediana', 'FillNa cu medie', 'FillNa cu valoare specifică', 
                               'MICE', 'Replace', 'Standardizare', 'Normalizare', 'Tratare outlieri', 'Grupare', 
                               'Redenumire coloană', 'Eliminare coloană']
alfanumeric_values_methods_list = ['Selectare Coloane', 'FillNa cu valoare specifică', 'Replace','String Slicing', 
                                   'Codare binara pe pozitii', 'Codificare numerica', 'Grupare', 'Redenumire coloană', 'Eliminare coloană']

def open_prepare_data_page(user_id, dataframe):
    def on_closing():
        prepare_window.destroy()

    prepare_window = tk.Tk()  # Create a new Tk instance instead of Toplevel
    prepare_window.title("Preparare Date")
    prepare_window.state("zoomed")

    main_frame = ttk.Frame(prepare_window, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)  # Ensure padding to see the frame's extent

    # TreeView setup
    main_tree = ttk.Treeview(tree_frame, columns=dataframe.columns.tolist(), show="headings")
    for col in dataframe.columns:
        main_tree.heading(col, text=col)
        main_tree.column(col, width=100)  # You may need to adjust widths based on actual content
    main_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Vertical Scrollbar
    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=main_tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    main_tree.configure(yscrollcommand=vsb.set)

    # Horizontal Scrollbar
    hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=main_tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    main_tree.configure(xscrollcommand=hsb.set)

    # Ensure data is loaded into the TreeView
    for index, row in dataframe.iterrows():
        main_tree.insert("", tk.END, values=list(row))

    # Listbox Frame for numeric and alphanumeric columns
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    # Numeric columns setup
    ttk.Label(list_frame, text="Coloane numerice").pack(side=tk.LEFT, padx=10)
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    num_methods = ttk.Combobox(list_frame, values=numeric_values_methods_list, width=25)
    num_methods.pack(side=tk.LEFT, padx=10)
    ttk.Button(list_frame, text="Folosește metoda pe\ncoloanele numericele", command=lambda: apply_method(dataframe, num_methods.get(), 'numeric', main_tree)).pack(side=tk.LEFT, padx=10)

    # Alphanumeric columns setup
    ttk.Label(list_frame, text="Coloane alfanumerice").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ttk.Combobox(list_frame, values=alfanumeric_values_methods_list, width=25)
    alpha_methods.pack(side=tk.LEFT, padx=10)
    ttk.Button(list_frame, text="Aplica metoda pe\ncoloanele alfanumerice", command=lambda: apply_method(dataframe, alpha_methods.get(), 'alpha', main_tree)).pack(side=tk.LEFT, padx=10)

    # Populate listboxes
    for col in dataframe.select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe.select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)

    # Entry and method selection based on column type
    entry = ttk.Entry(main_frame)
    entry.pack(padx=10, pady=10, fill=tk.X, expand=False)

    method_cb = ttk.Combobox(main_frame)
    method_cb.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    ttk.Button(main_frame, text="Folosește metoda pentru coloană", command=lambda: apply_method(entry.get(), method_cb.get(), dataframe)).pack(side=tk.LEFT, padx=10, pady=10)

    # Bind listbox selection changes
    num_listbox.bind('<<ListboxSelect>>', lambda event: update_entry_and_methods(num_listbox, entry, method_cb, ['Normalizează', 'Standardizează']))
    alpha_listbox.bind('<<ListboxSelect>>', lambda event: update_entry_and_methods(alpha_listbox, entry, method_cb, ['Codifică', 'Umple goluri']))

    # Analyze button
    execute_button = ttk.Button(main_frame, text="Analizeaza datele", command=lambda: open_analyze_data_page(user_id, dataframe, prepare_window))
    execute_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    # Save data button
    save_button = ttk.Button(main_frame, text="Salvează datele", command=lambda: save_csv(dataframe, user_id))
    save_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    prepare_window.protocol("WM_DELETE_WINDOW", on_closing)
    prepare_window.mainloop()
