import tkinter as tk
from tkinter import ttk
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ConnectPage.functions import create_account, login, center_window

def setup_gui():
    connect_page_front = tk.Tk()
    connect_page_front.title("Conectare")
    connect_page_front_height = 200
    connect_page_front_width = 275
    center_window(connect_page_front, connect_page_front_width, connect_page_front_height)
    connect_page_front.configure(bg="lightblue")
    connect_page_front.resizable(False, False)
    
    welcome_label = ttk.Label(connect_page_front, text="Bine ai venit!", font=("Helvetica", 16), background="lightblue")
    welcome_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    username_label = ttk.Label(connect_page_front, text="Nume utilizator:", background="lightblue", font=("Helvetica", 10))
    username_label.grid(row=1, column=0, padx=10, pady=10)  
    username_entry = ttk.Entry(connect_page_front)
    username_entry.grid(row=1, column=1, padx=10, pady=10)

    password_label = ttk.Label(connect_page_front, text="Parola:", background="lightblue", font=("Helvetica", 10))    
    password_label.grid(row=2, column=0, padx=10, pady=10)
    password_entry = ttk.Entry(connect_page_front, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    login_button = ttk.Button(connect_page_front, text="Conectare",
                              command=lambda: login(username_entry.get(), password_entry.get(), connect_page_front))
    login_button.grid(row=3, column=0, padx=10, pady=10)
    
    create_button = ttk.Button(connect_page_front, text="Creare cont", 
                               command=lambda: create_account(username_entry.get(), password_entry.get()))
    create_button.grid(row=3, column=1, padx=10, pady=10)

    connect_page_front.mainloop()

setup_gui()


