import tkinter as tk
from tkinter import ttk
import pandas as pd
from PrepareDataPage.front import open_prepare_data_page
from AddDataPage.functions import load_file, save_csv

def open_add_data_page(user_id):

    add_data_main_window = tk.Tk()
    add_data_main_window.title("Adaugare date")
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
    
    add_csv_button = ttk.Button(add_data_main_window, text="Încarcare set de date din CSV", 
                            command=lambda: load_file(dataframe_container, tree, "csv"))
    add_csv_button.pack(pady=10, fill=tk.X)

    add_excel_button = ttk.Button(add_data_main_window, text="Încarcare set de date din Excel",
                                    command=lambda: load_file(dataframe_container, tree, "excel"))
    add_excel_button.pack(pady=10, fill=tk.X)

    add_json_button = ttk.Button(add_data_main_window, text="Încarcare set de date din JSON",
                                    command=lambda: load_file(dataframe_container, tree, "json"))
    add_json_button.pack(pady=10, fill=tk.X)

    save_button = ttk.Button(add_data_main_window, text="Salvează setul de date local", 
                             command=lambda: save_csv(dataframe_container["dataframe"], 
                                                      dataframe_container["file_name"], user_id))
    save_button.pack(pady=10, fill=tk.X)

    prep_button = ttk.Button(add_data_main_window, text="Preprocesare Date", 
                             command=lambda: [add_data_main_window.destroy(), 
                                              open_prepare_data_page(user_id, dataframe_container["dataframe"])])
    prep_button.pack(pady=10, fill=tk.X)

    analyze_button = ttk.Button(add_data_main_window, text="Analiza Date")
    analyze_button.pack(pady=10, fill=tk.X)

    front_page_button = ttk.Button(add_data_main_window, text="Pagina principala")
    front_page_button.pack(pady=10, fill=tk.X)

    add_data_main_window.mainloop()
