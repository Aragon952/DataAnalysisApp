import tkinter as tk
from tkinter import ttk
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ConnectPage.functions import create_account, login, center_window

def setup_gui():
    connect_page_main_window = tk.Tk()
    connect_page_main_window.title("Connect Page")
    connect_page_front_height = 200
    connect_page_front_width = 250
    center_window(connect_page_main_window, connect_page_front_width, connect_page_front_height)
    connect_page_main_window.configure(bg="lightblue")
    connect_page_main_window.resizable(False, False)
    
    welcome_label = ttk.Label(connect_page_main_window, text="Welcome", font=("Helvetica", 16), background="lightblue")
    welcome_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10,)

    username_label = ttk.Label(connect_page_main_window, text="Username:", background="lightblue", font=("Helvetica", 10))
    username_label.grid(row=1, column=0, padx=10, pady=10)  
    username_entry = ttk.Entry(connect_page_main_window)
    username_entry.grid(row=1, column=1, padx=10, pady=10)

    password_label = ttk.Label(connect_page_main_window, text="Password", background="lightblue", font=("Helvetica", 10))    
    password_label.grid(row=2, column=0, padx=10, pady=10)
    password_entry = ttk.Entry(connect_page_main_window, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=10)

    login_button = ttk.Button(connect_page_main_window, text="Connect",
                              command=lambda: login(username_entry.get(), password_entry.get(), connect_page_main_window))
    login_button.grid(row=3, column=0, padx=10, pady=10)
    
    create_button = ttk.Button(connect_page_main_window, text="Create Account", 
                               command=lambda: create_account(username_entry.get(), password_entry.get()))
    create_button.grid(row=3, column=1, padx=10, pady=10)

    connect_page_main_window.mainloop()

setup_gui()


