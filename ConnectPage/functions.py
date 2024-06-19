from tkinter import messagebox
import sqlite3
import os
from FrontPage.front import open_main_page

def connect_db():
    return sqlite3.connect('DataAnalysisApp/database.db')


def create_account(name, password):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users_information (name, password) VALUES (?, ?)", (name, password))
        conn.commit()
        
        # Recuperarea ID-ului utilizatorului recent adăugat
        cursor.execute("SELECT id FROM users_information WHERE name=?", (name,))
        user_id = cursor.fetchone()[0]
        
        # Crearea folderului pentru noul utilizator
        user_folder_path = os.path.join("C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults", str(user_id))
        os.makedirs(user_folder_path, exist_ok=True)  # 'exist_ok=True' pentru a evita erorile dacă folderul există deja

        messagebox.showinfo("Succes", "Contul a fost creat cu succes și folderul a fost generat.")
        
    except sqlite3.IntegrityError:
        messagebox.showerror("Eroare", "Numele de utilizator există deja.")
    except Exception as e:
        messagebox.showerror("Eroare", f"Eroare neașteptată: {e}")
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