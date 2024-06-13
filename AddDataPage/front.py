import tkinter as tk
from tkinter import ttk

def open_add_data_page(user_id):
    # Crearea unei noi ferestre
    add_data_window = tk.Toplevel()  # Schimbat de la tk.Tk() la tk.Toplevel()
    add_data_window.title("Adaugare date")
    add_data_window.geometry("800x600")

    # Crearea meniului
    menu_bar = tk.Menu(add_data_window)
    add_data_window.config(menu=menu_bar)

    # Adăugare opțiuni meniu
    menu_bar.add_command(label="Pagina principala")
    menu_bar.add_command(label="Adaugare date")
    menu_bar.add_command(label="Preprocesare date")
    menu_bar.add_command(label="Analizarea datelor")
    menu_bar.add_command(label="Vizualizare rezultate")



    # Crearea unui frame pentru tabel
    table_frame = ttk.Frame(add_data_window, padding="3 3 12 12")
    table_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

 # Crearea unui frame pentru TreeView și Scrollbars
    frame = ttk.Frame(add_data_window, padding="3 3 12 12")
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    add_data_window.columnconfigure(0, weight=1)
    add_data_window.rowconfigure(0, weight=1)

    # Crearea Treeview cu un număr suficient de coloane
    num_columns = 20  # Numărul de coloane
    columns = [str(i) for i in range(num_columns)]
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=18)
    for i in range(num_columns):
        tree.heading(str(i), text=f"Coloana {i+1}")
        tree.column(str(i), width=100, stretch=tk.NO)

    tree.grid(row=0, column=0, sticky='nsew')
    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    v_scrollbar.grid(row=0, column=1, sticky='ns')
    tree.configure(yscrollcommand=v_scrollbar.set)

    h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    h_scrollbar.grid(row=1, column=0, sticky='ew')
    tree.configure(xscrollcommand=h_scrollbar.set)




    # Crearea butonului pentru adăugarea datelor
    add_button = ttk.Button(add_data_window, text="Adaugare set de date")
    add_button.grid(row=1, column=0, padx=10, pady=10, sticky='ew')

    welcome_label = ttk.Label(add_data_window, text=f"Bine ai venit, ID-ul tău este: {user_id}")
    welcome_label.grid(pady=20)

    add_button = ttk.Button(add_data_window, text="Preprocesare Date")
    add_button.grid(row=2, column=0, padx=10, pady=10, sticky='ew')
    # Rularea ferestrei
    add_data_window.mainloop()

    