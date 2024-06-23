import tkinter as tk
from tkinter import ttk
from AnalyzeData.front import open_analyze_data_page
from PrepareDataPage.functions import *

numeric_methods = ['Selectare Coloane', 'Eliminare coloane', 'Replace', 'Redenumire coloana', 'Grupare', 
                   'FillNa cu mediana', 'FillNa cu medie', 'FillNa cu valoare specifică', 'MICE', 
                   'Normalizare', 'Standardizare', 'Tratare outlieri']
alfanumeric_methods = ['Selectare coloane', 'Eliminare coloane', 'Replace', 'Redenumire coloana', 
                       'Grupare', 'Codare binara pe pozitii', 'Codificare numerica', 
                        'FillNa cu valoare specifică', 'String Slicing']

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
    num_methods = ttk.Combobox(list_frame, values=numeric_methods, width=25)
    num_methods.pack(side=tk.LEFT, padx=10)

    def handle_numeric_all_method_selection(event):
        selected_method = num_methods.get()
        if selected_method == 'Selectare Coloane':
            select_columns(dataframe_container, main_tree, num_listbox, alpha_listbox)
        elif selected_method == 'Eliminare coloane':
            remove_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Replace':
            replace_value(dataframe_container, tree_frame)
        elif selected_method == 'Redenumire coloana':
            rename_column(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Grupare':
            group_numeric_data(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'FillNa cu mediana':
            fill_numeric_nan_with_median(dataframe_container, tree_frame,
                                          dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'FillNa cu medie':
            fill_numeric_nan_with_mean(dataframe_container, tree_frame,
                                        dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'FillNa cu valoare specifică':
            fill_numeric_nan_with_specific_numeric_value(dataframe_container, tree_frame,
                                                          dataframe_container["dataframe"].
                                                          select_dtypes(include='number').columns.tolist())
        elif selected_method == 'MICE':
            mice_imputation_numeric(dataframe_container, tree_frame, 
                                    dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'Normalizare':
            normalize_numeric(dataframe_container, tree_frame, 
                              dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'Standardizare':
            standardize_numeric(dataframe_container, tree_frame, 
                                dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'Tratare outlieri':
            handle_outliers_numeric(dataframe_container, tree_frame, 
                                    dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        else:
            print("Method not implemented yet")

    num_methods.bind('<<ComboboxSelected>>', handle_numeric_all_method_selection)

    # Alphanumeric columns setup
    ttk.Label(list_frame, text="Coloane alfanumerice").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ttk.Combobox(list_frame, values=alfanumeric_methods, width=25)
    alpha_methods.pack(side=tk.LEFT, padx=10)

    def handle_alphanumeric_all_method_selection(event):
        selected_method = alpha_methods.get()
        if selected_method == 'Selectare coloane':
            select_columns(dataframe_container, main_tree, num_listbox, alpha_listbox)
        elif selected_method == 'Eliminare coloane':
            remove_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Replace':
            replace_value(dataframe_container, tree_frame)
        elif selected_method == 'Redenumire coloana':
            rename_column(dataframe_container, tree_frame)
        elif selected_method == 'Grupare':
            group_alphanumeric_data(dataframe_container, tree_frame,
                                    dataframe_container['dataframe'].columns.tolist(), num_listbox, alpha_listbox)
        elif selected_method == 'Codare binara pe pozitii':
            binary_encoding_alfanumeric(dataframe_container, tree_frame, 
                                        dataframe_container["dataframe"].select_dtypes(exclude='number').columns.tolist(),
                                        num_listbox, alpha_listbox)
        elif selected_method == 'Codificare numerica':
            numeric_encoding_alfanumeric(dataframe_container, tree_frame, 
                                        dataframe_container["dataframe"].select_dtypes(exclude='number').columns.tolist(),
                                        num_listbox, alpha_listbox)
        elif selected_method == 'FillNa cu valoare specifică':
            fill_alphanumeric_nan_with_specific_value(dataframe_container, tree_frame, 
                                                      dataframe_container["dataframe"].
                                                      select_dtypes(exclude='number').columns.tolist())
        elif selected_method == 'String Slicing':
            string_slicing_alfanumeric(dataframe_container, tree_frame, 
                                       dataframe_container["dataframe"].select_dtypes(exclude='number').columns.tolist())
        else:
            print("Method not implemented yet")

    alpha_methods.bind('<<ComboboxSelected>>', handle_alphanumeric_all_method_selection)

    # Populate listboxes
    for col in dataframe_container["dataframe"].select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe_container["dataframe"].select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)


    # Analyze button
    execute_button = ttk.Button(main_frame, text="Analizeaza datele", command=lambda: open_analyze_data_page(user_id, dataframe_container["dataframe"], prepare_window))
    execute_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    # Save data button
    save_button = ttk.Button(main_frame, text="Salvează datele", command=lambda: save_csv(dataframe_container, user_id))
    save_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    prepare_window.protocol("WM_DELETE_WINDOW", on_closing)
    prepare_window.mainloop()
