import tkinter as tk
from tkinter import ttk, Menu

from AddDataPage.front import open_add_data_page

def select_item(event):
    # Obține elementul selectat
    widget = event.widget
    index = int(widget.curselection()[0])
    value = widget.get(index)
    print("Ai selectat:", value)

# Crearea ferestrei principale


def open_main_page(user_id):
    root = tk.Tk()
    root.title("Pagina principala")
    root.geometry("787x545")  # Dimensiunea ferestrei

    welcome_label = ttk.Label(root, text=f"Bine ai venit, ID-ul tău este: {user_id}")
    welcome_label.pack(pady=20)

    menu_bar = Menu(root)
    root.config(menu=menu_bar)

    # Adaugare meniu
    file_menu = Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Pagina principala", menu=file_menu)
    menu_bar.add_command(label="Adaugare date")
    menu_bar.add_command(label="Preprocesare date")
    menu_bar.add_command(label="Analizarea datelor")
    menu_bar.add_command(label="Vizualizare rezultate")
    menu_bar.add_command(label="Detalii cont")
    menu_bar.add_command(label="Deconectare")

    # Crearea unui frame pentru a grupa widget-urile
    frame = ttk.Frame(root, padding="10")
    frame.pack(fill=tk.BOTH, expand=True)

    # Listbox pentru seturi de date
    label = ttk.Label(frame, text="Seturi de date anterioare")
    label.pack()

    listbox = tk.Listbox(frame, height=10, width=50, activestyle='dotbox')
    listbox.pack(padx=10, pady=10)

    # Adaugarea unor elemente in listbox
    data_sets = ["Analiza Consumului de Energie Regenerabilă în Europa (1990-2024)",
                "Performanta Scolara pe Districte Educationale",
                "Incidența Bolilor Cardiovasculare, 2005-2024",
                "Rata Criminalitatii in Principalele Metropole Globale",
                "Efectele Schimbarilor Climatice asupra Biodiversitatii in Arii Protejate"]
    for item in data_sets:
        listbox.insert(tk.END, item)

    listbox.bind('<<ListboxSelect>>', select_item)

    # Butoane
    buttons_frame = ttk.Frame(frame)
    buttons_frame.pack(fill=tk.X, pady=10)

    btn_select = ttk.Button(buttons_frame, text="Selectare date pentru preprocesare")
    btn_select.pack(fill=tk.X, padx=5, pady=2)

    btn_analyze = ttk.Button(buttons_frame, text="Selectare date pentru analiza")
    btn_analyze.pack(fill=tk.X, padx=5, pady=2)

    btn_add = ttk.Button(buttons_frame, text="Adaugare set de date nou", command= lambda : open_add_data_page(user_id))
    btn_add.pack(fill=tk.X, padx=5, pady=2)


    btn_add = ttk.Button(buttons_frame, text="Vizualizare Rezultate salvate")
    btn_add.pack(fill=tk.X, padx=5, pady=2)

    # Checkbox
    chk_state = tk.BooleanVar()
    chk_state.set(False) # set check state
    chk = ttk.Checkbutton(frame, text='Utilizarea serviciilor remote de analiza', var=chk_state)
    chk.pack()

# Rularea aplicatiei

    root.mainloop()




