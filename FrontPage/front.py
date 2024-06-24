import tkinter as tk
from tkinter import ttk
from FrontPage.functions import fetch_datasets, on_select
from AddDataPage.front import open_add_data_page
import pandas as pd
from PrepareDataPage.front import open_prepare_data_page
from AnalyzeData.front import open_analyze_data_page

def open_main_page(user_id):
    main_page_front = tk.Tk()
    main_page_front.title("Pagina principala")
    main_page_front.state('zoomed')
    main_page_front.configure(bg="lightblue")

    style = ttk.Style(main_page_front)
    style.configure("TButton", foreground="white", background="blue", padding=10, font=("Arial", 12))

    frame = ttk.Frame(main_page_front, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    label = ttk.Label(frame, text="Seturi de date salvate local:")
    label.pack()

    listbox = tk.Listbox(frame, height=10, width=100, activestyle='dotbox')
    listbox.pack(padx=10, pady=10)
    data_sets = fetch_datasets(user_id)
    for item in data_sets:
        listbox.insert(tk.END, item)

    dataframe_container = {"dataframe": pd.DataFrame()}

    listbox.bind('<<ListboxSelect>>', lambda event: on_select(event, user_id, listbox, selected_file_entry, dataframe_container))

    selected_file_label = ttk.Label(main_page_front, text="Fișier selectat:")
    selected_file_label.pack()

    selected_file_entry = ttk.Entry(main_page_front, width=50)
    selected_file_entry.pack(pady=5)

    buttons_frame = ttk.Frame(frame)
    buttons_frame.pack(fill=tk.X, pady=10)

    btn_add = ttk.Button(buttons_frame, text="Adaugare set de date nou", 
                         command=lambda: [main_page_front.destroy(), open_add_data_page(user_id)], style="TButton")
    btn_add.pack(fill=tk.X, padx=5, pady=2)

    btn_select = ttk.Button(buttons_frame, text="Selectare date pentru preprocesare", 
                            command=lambda: [main_page_front.destroy(), 
                                             open_prepare_data_page(user_id, dataframe_container["dataframe"])], style="TButton")
    btn_select.pack(fill=tk.X, padx=5, pady=2)

    btn_analyze = ttk.Button(buttons_frame, text="Selectare date pentru analiza", 
                             command=lambda: [main_page_front.destroy(), 
                                              open_analyze_data_page(user_id, dataframe_container["dataframe"])], style="TButton")
    btn_analyze.pack(fill=tk.X, padx=5, pady=2)

    main_page_front.mainloop()
