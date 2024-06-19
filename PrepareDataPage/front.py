import tkinter as tk
from tkinter import ttk
from AnalyzeData.front import open_analysis_page
from PrepareDataPage.functions import update_entry_and_methods, save_csv

def open_prepare_data_page(user_id, dataframe):
    prepare_window = tk.Toplevel()
    prepare_window.title("Preparare Date")
    prepare_window.state("zoomed")

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

    # Listbox Frame for numeric and alphanumeric columns
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    # Numeric columns setup
    ttk.Label(list_frame, text="Coloane numerice").pack(side=tk.LEFT, padx=10)
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    num_methods = ttk.Combobox(list_frame, values=['Normalizează', 'Standardizează'])
    num_methods.pack(side=tk.LEFT, padx=10)
    ttk.Button(list_frame, text="Folosește metoda pe toate numericele", command=lambda: apply_method(dataframe, num_methods.get(), 'numeric')).pack(side=tk.LEFT, padx=10)

    # Alphanumeric columns setup
    ttk.Label(list_frame, text="Coloane alfanumerice").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ttk.Combobox(list_frame, values=['Codifică', 'Umple goluri'])
    alpha_methods.pack(side=tk.LEFT, padx=10)
    ttk.Button(list_frame, text="Folosește metoda pe toate alfanumericele", command=lambda: apply_method(dataframe, alpha_methods.get(), 'alpha')).pack(side=tk.LEFT, padx=10)

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
    execute_button = ttk.Button(main_frame, text="Analizeaza datele", command=lambda: open_analysis_page(user_id, dataframe))
    execute_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    # Save data button
    save_button = ttk.Button(main_frame, text="Salvează datele", command=lambda: save_csv(dataframe, user_id))
    save_button.pack(padx=10, pady=10, fill=tk.X, expand=False)

    prepare_window.mainloop()


def apply_method(dataframe, method, col_type):
    if col_type == 'numeric':
        columns = dataframe.select_dtypes(include='number').columns
    else:
        columns = dataframe.select_dtypes(exclude='number').columns
    
    print(f"Applying {method} to all {col_type} columns: {', '.join(columns)}")
    # Here, implement the actual preprocessing logic for each column
