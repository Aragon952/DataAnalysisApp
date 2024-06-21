import tkinter as tk
from tkinter import ttk
from AnalyzeData.front import open_analyze_data_page
from PrepareDataPage.functions import *

numeric_methods_all_columns = ['Selectare Coloane','FillNa cu mediana', 'FillNa cu medie', 'FillNa cu valoare specifică', 
                               'MICE', 'Standardizare', 'Normalizare', 'Tratare outlieri', 'Grupare', 'Eliminare coloane']
numeric_methods_one_column = ['Replace', 'Redenumire coloana', 'Eliminare coloana', 'FillNa cu mediana', 'FillNa cu medie', 
                              'FillNa cu valoare specifică', 'MICE', 'Standardizare', 'Normalizare', 'Tratare outlieri']
alfanumeric_methods_all_columns = ['FillNa cu valoare specifică', 'String Slicing', 'Codare binara pe pozitii', 
                                   'Codificare numerica', 'Grupare', 'Eliminare coloane']
alfanumeric_methods_one_column = ['FillNa cu valoare specifică', 'Replace', 'String Slicing', 'Codare binara pe pozitii', 
                                  'Codificare numerica', 'Redenumire coloană', 'Eliminare coloană']

def open_prepare_data_page(user_id, dataframe):
    def on_closing():
        prepare_window.destroy()
    
    dataframe_container = {"dataframe": dataframe}

    prepare_window = tk.Tk()  # Create a new Tk instance instead of Toplevel
    prepare_window.title("Preparare Date")
    prepare_window.state("zoomed")

    main_frame = ttk.Frame(prepare_window, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)  # Ensure padding to see the frame's extent

    # TreeView setup
    main_tree = ttk.Treeview(tree_frame, columns=dataframe_container["dataframe"].columns.tolist(), show="headings")
    for col in dataframe_container["dataframe"].columns:
        main_tree.heading(col, text=col)
        main_tree.column(col, width=100)
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
    for index, row in dataframe_container["dataframe"].iterrows():
        main_tree.insert("", tk.END, values=list(row))

    # Listbox Frame for numeric and alphanumeric columns
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    # Numeric columns setup
    ttk.Label(list_frame, text="Coloane numerice").pack(side=tk.LEFT, padx=10)
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    num_methods = ttk.Combobox(list_frame, values=numeric_methods_all_columns, width=25)
    num_methods.pack(side=tk.LEFT, padx=10)

    def handle_numeric_all_method_selection(event):
        selected_method = num_methods.get()
        if selected_method == 'Selectare Coloane':
            select_columns(dataframe_container["dataframe"], tree_frame, dataframe_container, num_listbox, alpha_listbox)
        elif selected_method == 'FillNa cu mediana':
            fill_na_with_median(dataframe_container, tree_frame)
        elif selected_method == 'FillNa cu medie':
            fill_na_with_mean(dataframe_container, tree_frame)
        elif selected_method == 'FillNa cu valoare specifică':
            fill_na_with_specific_value(dataframe_container, tree_frame)
        elif selected_method == 'MICE':
            perform_mice_imputation(dataframe_container, tree_frame)
        elif selected_method == 'Standardizare':
            perform_standardization(dataframe_container, tree_frame)
        elif selected_method == 'Normalizare':
            perform_normalization(dataframe_container, tree_frame)
        elif selected_method == 'Tratare outlieri':
            handle_outliers(dataframe_container, tree_frame)
        elif selected_method == 'Grupare':
            perform_grouping(dataframe_container, tree_frame)
        elif selected_method == 'Eliminare coloane':
            remove_columns(dataframe_container, tree_frame)
        else:
            print("Method not implemented yet")

    num_methods.bind('<<ComboboxSelected>>', handle_numeric_all_method_selection)

    # Alphanumeric columns setup
    ttk.Label(list_frame, text="Coloane alfanumerice").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ttk.Combobox(list_frame, values=alfanumeric_methods_all_columns, width=25)
    alpha_methods.pack(side=tk.LEFT, padx=10)
    ttk.Button(list_frame, text="Aplica metoda pe\ncoloanele alfanumerice").pack(side=tk.LEFT, padx=10)

    # Populate listboxes
    for col in dataframe_container["dataframe"].select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe_container["dataframe"].select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)

    # Entry and method selection based on column type
    entry = ttk.Entry(main_frame)
    entry.pack(padx=10, pady=10, fill=tk.X, expand=False)

    method_cb = ttk.Combobox(main_frame)
    method_cb.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    ttk.Button(main_frame, text="Folosește metoda pentru coloană").pack(side=tk.LEFT, padx=10, pady=10)

    # Bind listbox selection changes
    num_listbox.bind('<<ListboxSelect>>', lambda event: update_methods_for_one_column(num_listbox, entry, method_cb, numeric_methods_one_column))
    alpha_listbox.bind('<<ListboxSelect>>', lambda event: update_methods_for_one_column(alpha_listbox, entry, method_cb, alfanumeric_methods_one_column))

    # Analyze button
    execute_button = ttk.Button(main_frame, text="Analizeaza datele", command=lambda: open_analyze_data_page(user_id, dataframe_container["dataframe"], prepare_window))
    execute_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    # Save data button
    save_button = ttk.Button(main_frame, text="Salvează datele", command=lambda: save_csv(dataframe_container, user_id))
    save_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    ttk.Button(list_frame, text="Select Columns", command=lambda: select_columns(dataframe_container["dataframe"], main_tree, dataframe_container)).pack(side=tk.LEFT, padx=10)


    prepare_window.protocol("WM_DELETE_WINDOW", on_closing)
    prepare_window.mainloop()
