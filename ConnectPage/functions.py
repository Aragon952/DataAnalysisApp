from tkinter import messagebox
import sqlite3
import os
from FrontPage.front import open_main_page
import re
import bcrypt

def connect_db():
    return sqlite3.connect('DataAnalysisApp/database.db')

def create_account(name, password):
    # Basic input validation
    if not re.match(r"^[a-zA-Z0-9_.-]+$", name):
        messagebox.showerror("Error", "Username contains forbidden characters.")
        return
    if len(password) < 8 or not re.search(r"[a-zA-Z]", password) or not re.search(r"[0-9]", password):
        messagebox.showerror("Error", "Password must be at least 8 characters long and contain letters and numbers.")
        return

    conn = connect_db()
    cursor = conn.cursor()

    # Check if the username already exists
    cursor.execute("SELECT id FROM users_information WHERE name=?", (name,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Username already exists.")
        conn.close()
        return

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        cursor.execute("INSERT INTO users_information (name, password) VALUES (?, ?)", (name, hashed_password))
        conn.commit()
        user_id = cursor.lastrowid

        base_path = "C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults"
        user_folder_path = os.path.join(base_path, str(user_id))
        datasets_folder_path = os.path.join(user_folder_path, "DataSets")
        results_folder_path = os.path.join(user_folder_path, "Results")
        
        os.makedirs(user_folder_path, exist_ok=True)
        os.makedirs(datasets_folder_path, exist_ok=True)
        os.makedirs(results_folder_path, exist_ok=True)

        messagebox.showinfo("Success", "Account was successfully created and the folder has been generated.")
        
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error: {e}")
    finally:
        conn.close()

def login(name, password, root):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users_information WHERE name=?", (name,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, stored_password = user
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            messagebox.showinfo("Success", "You have successfully logged in!")
            root.destroy()
            open_main_page(user_id)
        else:
            messagebox.showerror("Error", "Incorrect username or password.")
    else:
        messagebox.showerror("Error", "Incorrect username or password.")

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    
    root.geometry(f'{width}x{height}+{x}+{y}')