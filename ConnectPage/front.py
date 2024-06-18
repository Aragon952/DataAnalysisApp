import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ConnectPage.functions import create_account, login

    
def setup_gui():
    global root
    root = tk.Tk()
    root.title("Conectare")

    username_label = ttk.Label(root, text="Nume utilizator:")
    username_label.grid(row=0, column=0, padx=10, pady=10)  
    username_entry = ttk.Entry(root)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    password_label = ttk.Label(root, text="Parola:")
    password_label.grid(row=1, column=0, padx=10, pady=10)
    password_entry = ttk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    login_button = ttk.Button(root, text="Conectare", command=lambda: login(username_entry.get(), password_entry.get(), root))
    login_button.grid(row=2, column=0, padx=10, pady=10)
    
    create_button = ttk.Button(root, text="Creare cont", command=lambda: create_account(username_entry.get(), password_entry.get()))
    create_button.grid(row=2, column=1, padx=10, pady=10)

    root.mainloop()


setup_gui()
