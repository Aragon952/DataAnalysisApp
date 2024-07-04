import tkinter as tk
from tkinter import ttk
from FrontPage.functions import fetch_datasets, on_select, fetch_results, display_selected_result
from AddDataPage.front import open_add_data_page
import pandas as pd
from PrepareDataPage.front import open_prepare_data_page
from AnalyzeData.front import open_analyze_data_page

def open_main_page(user_id):
    main_window = tk.Tk()
    main_window.title("Main Page")
    main_window.state('zoomed')
    main_window.configure(bg="lightblue")

    main_frame = ttk.Frame(main_window, padding="20")
    main_frame.grid(row=0, column=0, sticky='nsew')

    main_window.grid_columnconfigure(0, weight=1)
    main_window.grid_rowconfigure(0, weight=1)

    datasets_label = ttk.Label(main_frame, text="Locally Saved Datasets:", font=("Arial", 12, "bold"))
    datasets_label.grid(row=0, column=0, sticky='w', pady=(0, 10))

    listbox = tk.Listbox(main_frame, height=10, width=100, activestyle='dotbox')
    listbox.grid(row=1, column=0, sticky='ew')
    
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=listbox.yview)
    scrollbar.grid(row=1, column=1, sticky='ns')
    listbox.configure(yscrollcommand=scrollbar.set)

    data_sets = fetch_datasets(user_id)
    for item in data_sets:
        listbox.insert(tk.END, item)

    dataframe_container = {"dataframe": pd.DataFrame()}
    listbox.bind('<<ListboxSelect>>', lambda event: on_select(event, user_id, listbox, selected_file_entry, dataframe_container))

    selected_file_label = ttk.Label(main_frame, text="Selected File:")
    selected_file_label.grid(row=2, column=0, sticky='w', pady=(10, 0))

    selected_file_entry = ttk.Entry(main_frame, width=100)
    selected_file_entry.grid(row=3, column=0, sticky='ew', pady=(5, 20))

    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.grid(row=4, column=0, sticky='ew', pady=(0, 20))

    btn_add = ttk.Button(buttons_frame, text="Add New Dataset",
                         command=lambda: [main_window.destroy(), open_add_data_page(user_id)])
    btn_add.grid(row=0, column=0, padx=(0, 5))

    btn_select = ttk.Button(buttons_frame, text="Select Data for Preprocessing",
                            command=lambda: [main_window.destroy(),
                                             open_prepare_data_page(user_id, dataframe_container["dataframe"])])
    btn_select.grid(row=0, column=1, padx=5)

    btn_analyze = ttk.Button(buttons_frame, text="Select Data for Analysis",
                             command=lambda: [main_window.destroy(),
                                              open_analyze_data_page(user_id, dataframe_container["dataframe"])])
    btn_analyze.grid(row=0, column=2, padx=(5, 0))

    results_label = ttk.Label(main_frame, text="Saved Results and Interpretations:", font=("Arial", 12, "bold"))
    results_label.grid(row=5, column=0, sticky='w', pady=(0, 10))

    results_listbox = tk.Listbox(main_frame, height=10, width=100, activestyle='dotbox')
    results_listbox.grid(row=6, column=0, sticky='ew')

    results_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=results_listbox.yview)
    results_scrollbar.grid(row=6, column=1, sticky='ns')
    results_listbox.configure(yscrollcommand=results_scrollbar.set)

    # Fetch and display results
    result_data = fetch_results(user_id)
    for name, _ in result_data:
        results_listbox.insert(tk.END, name)

    results_listbox.bind('<<ListboxSelect>>', lambda event: display_selected_result(event, user_id, result_data))

    btn_select_result = ttk.Button(main_frame, text="Select Result")
    btn_select_result.grid(row=7, column=0, pady=(20, 0))

    main_frame.grid_columnconfigure(0, weight=1)
    buttons_frame.grid_columnconfigure((0, 1, 2), weight=1)

    main_window.mainloop()