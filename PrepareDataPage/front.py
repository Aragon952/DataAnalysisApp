import tkinter as tk
from tkinter import ttk
from AnalyzeData.front import open_analyze_data_page
from PrepareDataPage.functions import *

numeric_methods = ['Select Columns', 'Remove Columns', 'Replace', 'Rename Column', 'Group',
                   'FillNa with Median', 'FillNa with Mean', 'FillNa with Specific Value', 'MICE',
                   'Normalize', 'Standardize', 'Handle Outliers']
alphanumeric_methods = ['Select Columns', 'Remove Columns', 'Replace', 'Rename Column',
                        'Group', 'Binary Encoding by Position', 'Numeric Encoding',
                        'FillNa with Specific Value', 'String Slicing']

def open_prepare_data_page(user_id, dataframe):
    dataframe_container = {"dataframe": dataframe}

    prepare_data_main_window = tk.Tk()
    prepare_data_main_window.title("Prepare Data")
    prepare_data_main_window.state("zoomed")

    main_frame = ttk.Frame(prepare_data_main_window, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    tree_frame = ttk.Frame(main_frame)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

    main_tree = ttk.Treeview(tree_frame, columns=dataframe_container["dataframe"].columns.tolist(), show="headings")
    for col in dataframe_container["dataframe"].columns:
        main_tree.heading(col, text=col)
        main_tree.column(col, width=100)
    main_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=main_tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    main_tree.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=main_tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    main_tree.configure(xscrollcommand=hsb.set)

    for index, row in dataframe_container["dataframe"].iterrows():
        main_tree.insert("", tk.END, values=list(row))

    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    ttk.Label(list_frame, text="Numeric Columns").pack(side=tk.LEFT, padx=10)
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    num_methods = ttk.Combobox(list_frame, values=numeric_methods, width=25)
    num_methods.pack(side=tk.LEFT, padx=10)

    def handle_numeric_all_method_selection(event):
        selected_method = num_methods.get()
        if selected_method == 'Select Columns':
            select_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Remove Columns':
            remove_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Replace':
            replace_value(dataframe_container, tree_frame)
        elif selected_method == 'Rename Column':
            rename_column(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Group':
            group_numeric_data(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'FillNa with Median':
            fill_numeric_nan_with_median(dataframe_container, tree_frame,
                                          dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'FillNa with Mean':
            fill_numeric_nan_with_mean(dataframe_container, tree_frame,
                                        dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'FillNa with Specific Value':
            fill_numeric_nan_with_specific_numeric_value(dataframe_container, tree_frame,
                                                          dataframe_container["dataframe"].
                                                          select_dtypes(include='number').columns.tolist())
        elif selected_method == 'MICE':
            mice_imputation_numeric(dataframe_container, tree_frame, 
                                    dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'Normalize':
            normalize_numeric(dataframe_container, tree_frame, 
                              dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'Standardize':
            standardize_numeric(dataframe_container, tree_frame, 
                                dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        elif selected_method == 'Handle Outliers':
            handle_outliers_numeric(dataframe_container, tree_frame, 
                                    dataframe_container["dataframe"].select_dtypes(include='number').columns.tolist())
        else:
            print("Method not implemented yet")

    num_methods.bind('<<ComboboxSelected>>', handle_numeric_all_method_selection)

    ttk.Label(list_frame, text="Alphanumeric Columns").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ttk.Combobox(list_frame, values=alphanumeric_methods, width=25)
    alpha_methods.pack(side=tk.LEFT, padx=10)

    def handle_alphanumeric_all_method_selection(event):
        selected_method = alpha_methods.get()
        if selected_method == 'Select Columns':
            select_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Remove Columns':
            remove_columns(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Replace':
            replace_value(dataframe_container, tree_frame)
        elif selected_method == 'Rename Column':
            rename_column(dataframe_container, tree_frame, num_listbox, alpha_listbox)
        elif selected_method == 'Group':
            group_alphanumeric_data(dataframe_container, tree_frame,
                                    dataframe_container['dataframe'].columns.tolist(), num_listbox, alpha_listbox)
        elif selected_method == 'Binary Encoding by Position':
            binary_encoding_alphanumeric(dataframe_container, tree_frame, 
                                        dataframe_container["dataframe"].select_dtypes(exclude='number').columns.tolist(),
                                        num_listbox, alpha_listbox)
        elif selected_method == 'Numeric Encoding':
            numeric_encoding_alphanumeric(dataframe_container, tree_frame, 
                                        dataframe_container["dataframe"].select_dtypes(exclude='number').columns.tolist(),
                                        num_listbox, alpha_listbox)
        elif selected_method == 'FillNa with Specific Value':
            fill_alphanumeric_nan_with_specific_value(dataframe_container, tree_frame, 
                                                      dataframe_container["dataframe"].
                                                      select_dtypes(exclude='number').columns.tolist())
        elif selected_method == 'String Slicing':
            string_slicing_alphanumeric(dataframe_container, tree_frame, 
                                       dataframe_container["dataframe"].select_dtypes(exclude='number').columns.tolist())
        else:
            print("Method not implemented yet")

    alpha_methods.bind('<<ComboboxSelected>>', handle_alphanumeric_all_method_selection)

    for col in dataframe_container["dataframe"].select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe_container["dataframe"].select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)

    execute_button = ttk.Button(main_frame, text="Analyze Data", command=lambda:[prepare_data_main_window.destroy(), open_analyze_data_page(user_id, dataframe_container["dataframe"])])
    execute_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    save_button = ttk.Button(main_frame, text="Save Data", command=lambda: save_csv(dataframe_container['dataframe'], user_id))
    save_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    prepare_data_main_window.mainloop()
