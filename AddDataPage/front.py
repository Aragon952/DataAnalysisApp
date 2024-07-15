import tkinter as tk
from tkinter import ttk
import pandas as pd
from PrepareDataPage.front import open_prepare_data_page
from AddDataPage.functions import load_file, save_csv
from AnalyzeData.front import open_analyze_data_page

def open_add_data_page(user_id):

    add_data_main_window = tk.Tk()
    add_data_main_window.title("Add Data")
    add_data_main_window.state('zoomed')

    frame = ttk.Frame(add_data_main_window, padding="3 3 12 12")
    frame.pack(fill=tk.BOTH, expand=True)

    tree = ttk.Treeview(frame, show="headings")
    tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=vsb.set)

    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    tree.configure(xscrollcommand=hsb.set)

    dataframe_container = {"dataframe": pd.DataFrame(), "file_name": ""}
    
    add_csv_button = ttk.Button(add_data_main_window, text="Load dataset from CSV", 
                            command=lambda: load_file(dataframe_container, tree, "csv"))
    add_csv_button.pack(pady=10, fill=tk.X)

    add_excel_button = ttk.Button(add_data_main_window, text="Load dataset from Excel",
                                    command=lambda: load_file(dataframe_container, tree, "excel"))
    add_excel_button.pack(pady=10, fill=tk.X)

    add_json_button = ttk.Button(add_data_main_window, text="Load dataset from JSON",
                                    command=lambda: load_file(dataframe_container, tree, "json"))
    add_json_button.pack(pady=10, fill=tk.X)

    save_button = ttk.Button(add_data_main_window, text="Save dataset locally", 
                             command=lambda: save_csv(dataframe_container["dataframe"], user_id))
    save_button.pack(pady=10, fill=tk.X)

    prep_button = ttk.Button(add_data_main_window, text="Prepare Data", 
                             command=lambda: [add_data_main_window.destroy(), 
                                              open_prepare_data_page(user_id, dataframe_container["dataframe"])])
    prep_button.pack(pady=10, fill=tk.X)

    analyze_button = ttk.Button(add_data_main_window, text="Analyze Data", 
                                command=lambda: [add_data_main_window.destroy(), 
                                                 open_analyze_data_page(user_id, dataframe_container["dataframe"])])
    analyze_button.pack(pady=10, fill=tk.X)

    add_data_main_window.mainloop()