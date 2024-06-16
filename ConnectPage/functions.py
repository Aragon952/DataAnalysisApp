from tkinter import messagebox
import sqlite3
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from FrontPage.front import open_main_page

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

def login(name, password, root):
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