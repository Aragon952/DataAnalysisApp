import tkinter as tk
from tkinter import ttk
from AnalyzeData.functions import *

numeric_methods = ['Statistici descriptive', 'Regresie Liniara', 'Regresie Logistica', 'Analiza Cluster', 'Testare de Ipoteze', 
                   'Analiza de Corelatie', 'Analiza Componente Principale', 'Analiza Discriminanta Lineara', 
                   'Metode Bayesian']
alfanumeric_methods = ['Frecventa si distributie', 'Tabel de Contingenta', 'Testul Chi-patrat', 'Analiza Asociatiei',
                       'Analiza de Sentiment', ]


def open_analyze_data_page(user_id, dataframe):
    analyze_window = tk.Tk()
    analyze_window.title("Analiza Datelor")
    analyze_window.state("zoomed")

    main_frame = ttk.Frame(analyze_window, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Frame for TreeView and Scrollbars
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

    # Setup listboxes and entry for column selection and method application
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.X, expand=False, side=tk.TOP, pady=10)

    ttk.Label(list_frame, text="Coloane numerice").pack(side=tk.LEFT, padx=10)
    num_listbox = tk.Listbox(list_frame, height=5)
    num_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    num_methods = ttk.Combobox(list_frame, values=numeric_methods, width=25)
    num_methods.pack(side=tk.LEFT, padx=10)

    def handle_numeric_methods(event):
        selected_method = num_methods.get()
        if selected_method == 'Statistici descriptive':
            apply_descriptive_statistics(dataframe, dataframe.select_dtypes(include='number').columns.tolist())
        elif selected_method == 'Regresie Liniara':
            apply_linear_regression(dataframe)
        elif selected_method == 'Regresie Logistica':
            apply_logistic_regression(dataframe)
        elif selected_method == 'Analiza Cluster':
            apply_cluster_analysis(dataframe)
        elif selected_method == 'Testare de Ipoteze':
            apply_hypothesis_testing(dataframe)
        elif selected_method == 'Analiza de Corelatie':
            apply_correlation_analysis(dataframe)
        elif selected_method == 'Analiza Componente Principale':
            apply_pca(dataframe)
        elif selected_method == 'Analiza Discriminanta Lineara':
            apply_lda(dataframe)
        elif selected_method == 'Metode Bayesian':
            apply_bayesian_methods(dataframe)
        else:
            print("Method not implemented yet")

    num_methods.bind('<<ComboboxSelected>>', handle_numeric_methods)
    
    ttk.Label(list_frame, text="Coloane alfanumerice").pack(side=tk.LEFT, padx=10)
    alpha_listbox = tk.Listbox(list_frame, height=5)
    alpha_listbox.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
    alpha_methods = ttk.Combobox(list_frame, values=alfanumeric_methods, width=25)
    alpha_methods.pack(side=tk.LEFT, padx=10)

    def handle_alpha_methods(event):
        selected_method = alpha_methods.get()
        if selected_method == 'Frecventa si distributie':
            apply_frequency_distribution(dataframe)
        elif selected_method == 'Tabel de Contingenta':
            apply_contingency_table(dataframe)
        elif selected_method == 'Testul Chi-patrat':
            apply_chi_square_test(dataframe)
        elif selected_method == 'Analiza Asociatiei':
            apply_association_analysis(dataframe)
        elif selected_method == 'Analiza de Sentiment':
            apply_sentiment_analysis(dataframe)
        else:
            print("Method not implemented yet")

    alpha_methods.bind('<<ComboboxSelected>>', handle_alpha_methods)

    for col in dataframe.select_dtypes(include='number').columns:
        num_listbox.insert(tk.END, col)
    for col in dataframe.select_dtypes(exclude='number').columns:
        alpha_listbox.insert(tk.END, col)

        # Bottom control buttons
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(fill=tk.X, pady=10)

    save_button = ttk.Button(button_frame, text="Salvează datele", command=lambda: save_csv(dataframe, user_id))
    save_button.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

    analyze_window.mainloop()
