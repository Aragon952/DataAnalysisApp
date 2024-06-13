import tkinter as tk
from tkinter import ttk

def open_analysis_page(user_id, dataframe):
    analysis_window = tk.Toplevel()
    analysis_window.title("Analize")
    analysis_window.geometry("974x503")

    # Dropdown pentru analize recomandate și toate analizele
    analyses = ['Select', 'Sortare', 'Valori unice', 'Găsește și înlocuiește', 'Rezumat',
                'Transpunere', 'Transformare XML', 'Coloane în text', 'Text în data calendaristică', 'Tabel încrucișat']
    recommended_analyses = ['Select', 'Sortare', 'Valori unice']

    analysis_var = tk.StringVar()
    all_analyses_cb = ttk.Combobox(analysis_window, values=analyses, textvariable=analysis_var)
    all_analyses_cb.grid(row=0, column=0, padx=10, pady=10)

    recommended_var = tk.StringVar()
    recommended_cb = ttk.Combobox(analysis_window, values=recommended_analyses, textvariable=recommended_var)
    recommended_cb.grid(row=0, column=1, padx=10, pady=10)

    # Lista pentru afișarea analizei selectate
    selected_analysis_list = tk.Listbox(analysis_window, height=4)
    selected_analysis_list.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

    # Adăugarea analizei selectate la listă
    def add_selected_analysis():
        selected_analysis = all_analyses_cb.get()
        selected_analysis_list.insert(tk.END, selected_analysis)

    select_button = ttk.Button(analysis_window, text="Adaugă Analiza Selectată", command=add_selected_analysis)
    select_button.grid(row=0, column=2, padx=10, pady=10)

    # Partea de Machine Learning
    ttk.Button(analysis_window, text="Modelare asistată").grid(row=2, column=0, padx=10, pady=10)
    ttk.Button(analysis_window, text="Modele de predicție").grid(row=2, column=1, padx=10, pady=10)
    ttk.Button(analysis_window, text="Modele de regresie").grid(row=2, column=2, padx=10, pady=10)

    # Dropdown pentru crearea tabelelor
    table_options = ['Fără diagrame', 'Cu diagrame', 'Tabele detaliate']
    table_var = tk.StringVar()
    table_cb = ttk.Combobox(analysis_window, values=table_options, textvariable=table_var)
    table_cb.grid(row=3, column=0, padx=10, pady=10)

    analysis_window.mainloop()

# Exemplu de utilizare
# df = pd.DataFrame(...)  # Your DataFrame
# open_analysis_page(1, df)  # Call the function with a user_id and a DataFrame
