import tkinter as tk
from tkinter import ttk, Menu
from FrontPage.functions import fetch_datasets, on_select
from AddDataPage.front import open_add_data_page
import pandas as pd
from PrepareDataPage.front import open_prepare_data_page

def open_main_page(user_id):
    root = tk.Tk()
    root.title("Pagina principala")
    root.state('zoomed')

    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    label = ttk.Label(frame, text="Seturi de date salvate local:")
    label.pack()

    listbox = tk.Listbox(frame, height=10, width=50, activestyle='dotbox')
    listbox.pack(padx=10, pady=10)
    data_sets = fetch_datasets(user_id)
    for item in data_sets:
        listbox.insert(tk.END, item)


    dataframe_container = {"dataframe": pd.DataFrame()}

    listbox.bind('<<ListboxSelect>>', lambda event: on_select(event, user_id, listbox, selected_file_entry, dataframe_container))

    selected_file_label = ttk.Label(root, text="Fișier selectat:")
    selected_file_label.pack()

    selected_file_entry = ttk.Entry(root, width=50)
    selected_file_entry.pack(pady=5)

    buttons_frame = ttk.Frame(frame)
    buttons_frame.pack(fill=tk.X, pady=10)

    btn_select = ttk.Button(buttons_frame, text="Selectare date pentru preprocesare", command=lambda: open_prepare_data_page(user_id, dataframe_container["dataframe"]))
    btn_select.pack(fill=tk.X, padx=5, pady=2)

    btn_analyze = ttk.Button(buttons_frame, text="Selectare date pentru analiza")
    btn_analyze.pack(fill=tk.X, padx=5, pady=2)

    btn_add = ttk.Button(buttons_frame, text="Adaugare set de date nou", command=lambda: open_add_data_page(user_id))
    btn_add.pack(fill=tk.X, padx=5, pady=2)

    btn_view = ttk.Button(buttons_frame, text="Vizualizare Rezultate salvate")
    btn_view.pack(fill=tk.X, padx=5, pady=2)

    root.mainloop()
