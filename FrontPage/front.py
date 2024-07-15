import tkinter as tk
from tkinter import ttk
from FrontPage.functions import fetch_datasets, fetch_results, display_selected_result, open_data_page
from AddDataPage.front import open_add_data_page
from PrepareDataPage.front import open_prepare_data_page
from AnalyzeData.front import open_analyze_data_page

def open_main_page(user_id):
    main_window = tk.Tk()
    main_window.title("Main Page")
    main_window.state('zoomed')
    main_window.configure(bg="lightblue")

    main_frame = ttk.Frame(main_window, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    datasets_label = ttk.Label(main_frame, text="Locally Saved Datasets:", font=("Arial", 12, "bold"))
    datasets_label.pack(side=tk.TOP, anchor='w', pady=(0, 10))

    listbox_frame = ttk.Frame(main_frame)
    listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    listbox = tk.Listbox(listbox_frame, height=10, width=50, activestyle='dotbox')
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.configure(yscrollcommand=scrollbar.set)

    for item in fetch_datasets(user_id):
        listbox.insert(tk.END, item)

    buttons_frame = ttk.Frame(main_frame)
    buttons_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 20))
    ttk.Button(buttons_frame, text="Add New Dataset", command=lambda: open_add_data_page(user_id)).pack(side=tk.LEFT, expand=True, padx=5)
    ttk.Button(buttons_frame, text="Select Data for Preprocessing", command=lambda: open_data_page(user_id, listbox, open_prepare_data_page)).pack(side=tk.LEFT, expand=True, padx=5)
    ttk.Button(buttons_frame, text="Select Data for Analysis", command=lambda: open_data_page(user_id, listbox, open_analyze_data_page)).pack(side=tk.LEFT, expand=True, padx=5)

    results_label = ttk.Label(main_frame, text="Saved Results and Interpretations:", font=("Arial", 12, "bold"))
    results_label.pack(side=tk.TOP, anchor='w', pady=(0, 10))

    results_listbox_frame = ttk.Frame(main_frame)
    results_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    results_listbox = tk.Listbox(results_listbox_frame, height=10, width=50, activestyle='dotbox')
    results_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    results_scrollbar = ttk.Scrollbar(results_listbox_frame, orient="vertical", command=results_listbox.yview)
    results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    results_listbox.configure(yscrollcommand=results_scrollbar.set)

    for name, _ in fetch_results(user_id):
        results_listbox.insert(tk.END, name)

    ttk.Button(main_frame, text="Select Result", command=lambda: display_selected_result(user_id, results_listbox)).pack(side=tk.TOP, fill=tk.X, pady=(20, 0))

    main_window.mainloop()

