import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import sys
import os

# Acesta adaugă directorul părinte (DataAnalysisApp) la sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FrontPage.front import open_main_page

# Funcții pentru gestionarea bazei de date
def connect_db():
    return sqlite3.connect('DataAnalysisApp/database.db')


def create_account(name, password):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users_information (name, password) VALUES (?, ?)", (name, password))
        conn.commit()
        messagebox.showinfo("Succes", "Contul a fost creat cu succes!")
    except sqlite3.IntegrityError:
        messagebox.showerror("Eroare", "Numele de utilizator există deja.")
    finally:
        conn.close()

def login(name, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users_information WHERE name=? AND password=?", (name, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        user_id = user[0]
        messagebox.showinfo("Succes", "Te-ai conectat cu succes!")
        root.destroy()  # Închide fereastra de conectare
        open_main_page(user_id)  # Deschide pagina principală cu ID-ul utilizatorului
    else:
        messagebox.showerror("Eroare", "Numele de utilizator sau parola sunt incorecte.")

# Interfața grafică pentru conectare
def setup_gui():
    global root
    root = tk.Tk()
    root.title("Conectare")
    root.geometry("250x150")

    username_label = ttk.Label(root, text="Nume utilizator:")
    username_label.grid(row=0, column=0, padx=10, pady=10)
    username_entry = ttk.Entry(root)
    username_entry.grid(row=0, column=1, padx=10, pady=10)

    password_label = ttk.Label(root, text="Parola:")
    password_label.grid(row=1, column=0, padx=10, pady=10)
    password_entry = ttk.Entry(root, show="*")
    password_entry.grid(row=1, column=1, padx=10, pady=10)

    login_button = ttk.Button(root, text="Conectare", command=lambda: login(username_entry.get(), password_entry.get()))
    login_button.grid(row=2, column=0, padx=10, pady=10)
    
    create_button = ttk.Button(root, text="Creare cont", command=lambda: create_account(username_entry.get(), password_entry.get()))
    create_button.grid(row=2, column=1, padx=10, pady=10)

    root.mainloop()


setup_gui()
