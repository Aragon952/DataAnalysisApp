import tkinter as tk
from tkinter import ttk
from AnalyzeData.functions import *

numeric_methods = ['Descriptive Statistics', 'Linear Regression', 'Logistic Regression', 'Cluster Analysis', 
                   'Correlation Analysis', 'Principal Component Analysis', 'Linear Discriminant Analysis', 
                   'Bayesian Methods', 'Contingency Table']
alphanumeric_methods = ['Frequency and Distribution', 'Contingency Table', 'Chi-Square Test', 'Association Analysis',
                        'Sentiment Analysis']

def open_analyze_data_page(user_id, dataframe):
    analyze_data_main_window = tk.Tk()
    analyze_data_main_window.title("Data Analysis")
    analyze_data_main_window.state("zoomed")

    main_frame = ttk.Frame(analyze_data_main_window, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    tree_frame = ttk.Frame(main_frame, height=200)
    tree_frame.pack(fill=tk.BOTH, expand=True, pady=20, padx=20)

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

    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    ttk.Label(list_frame, text="Numeric Columns").pack(side=tk.LEFT, padx=10)
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    num_methods = ttk.Combobox(list_frame, values=numeric_methods, width=25)
    num_methods.pack(side=tk.LEFT, padx=10)

    def handle_numeric_methods(event):
        selected_method = num_methods.get()
        if selected_method == 'Descriptive Statistics':
            apply_descriptive_statistics(dataframe, dataframe.select_dtypes(include='number').columns.tolist(), user_id)
        elif selected_method == 'Linear Regression':
            apply_linear_regression(dataframe, dataframe.select_dtypes(include='number').columns.tolist(), user_id)
        elif selected_method == 'Logistic Regression':
            apply_logistic_regression(dataframe, dataframe.select_dtypes(include='number').columns.tolist(), user_id)
        elif selected_method == 'Cluster Analysis':
            apply_cluster_analysis(dataframe, dataframe.select_dtypes(include='number').columns.tolist(), user_id)
        elif selected_method == 'Correlation Analysis':
            apply_correlation_analysis(dataframe, dataframe.select_dtypes(include='number').columns.tolist(), user_id)
        elif selected_method == 'Principal Component Analysis':
            apply_pca(dataframe, dataframe.select_dtypes(include='number').columns.tolist(), user_id)
        elif selected_method == 'Linear Discriminant Analysis':
            apply_lda(dataframe, dataframe.columns.tolist(), user_id)
        elif selected_method == 'Bayesian Methods':
            apply_bayesian_methods(dataframe, dataframe.columns.tolist(), user_id)
        elif selected_method == 'Contingency Table':
            apply_contingency_table(dataframe, dataframe.columns.tolist(), user_id)
        else:
            print("Method not implemented yet")

    num_methods.bind('<<ComboboxSelected>>', handle_numeric_methods)
    
    ttk.Label(list_frame, text="Alphanumeric Columns").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ttk.Combobox(list_frame, values=alphanumeric_methods, width=25)
    alpha_methods.pack(side=tk.LEFT, padx=10)

    def handle_alpha_methods(event):
        selected_method = alpha_methods.get()
        if selected_method == 'Frequency and Distribution':
            apply_frequency_distribution(dataframe, dataframe.select_dtypes(exclude='number').columns.tolist())
        elif selected_method == 'Contingency Table':
            apply_contingency_table(dataframe, dataframe.columns.tolist(), user_id)
        elif selected_method == 'Chi-Square Test':
            apply_chi_square_test(dataframe, dataframe.select_dtypes(exclude='number').columns.tolist())
        elif selected_method == 'Association Analysis':
            apply_association_analysis(dataframe, dataframe.columns.tolist())
        elif selected_method == 'Sentiment Analysis':
            apply_sentiment_analysis(dataframe, dataframe.select_dtypes(exclude='number').columns.tolist())
        else:
            print("Method not implemented yet")

    alpha_methods.bind('<<ComboboxSelected>>', handle_alpha_methods)

    for col in dataframe.select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe.select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)

    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    save_button = ttk.Button(button_frame, text="Save Data", command=lambda: save_csv(dataframe, user_id))
    save_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    analyze_data_main_window.mainloop()