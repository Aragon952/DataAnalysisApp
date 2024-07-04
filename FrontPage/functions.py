import sqlite3
from tkinter import messagebox, simpledialog, ttk
import os
import tkinter as tk
import pandas as pd

def connect_db():
    return sqlite3.connect('DataAnalysisApp/database.db')

def fetch_datasets(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_name FROM user_history WHERE user_id = ?", (user_id,))
    datasets = [row[0] for row in cursor.fetchall()]
    conn.close()
    return datasets

def fetch_results(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT result_name, result_path FROM user_result_history WHERE user_informationid = ?", (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def display_selected_result(event, user_id, result_data):
    selection_index = event.widget.curselection()
    if selection_index:
        index = selection_index[0]
        result_name, result_path = result_data[index]
        display_results("Result Details", pd.read_csv(result_path), ["Column_Name", "Value"], user_id, None, None)

def display_results(window_title, data, columns, user_id, analysis_function=None, generate_message=None):
    def invoke_analysis():
        if analysis_function and generate_message:
            analysis_function(response_text, data, generate_message)

    def save_to_csv():
        base_dir = f"C:/Users/user/Desktop/Licenta/GitApp/DataAndResults/{user_id}/Results"
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

        file_name = simpledialog.askstring("File Name", "Enter the name of the file:", parent=results_win)
        if file_name:
            file_path = os.path.join(base_dir, file_name + ".csv")
            data.to_csv(file_path, index=False)
            messagebox.showinfo("Save to CSV", "File has been saved successfully!")
            save_file_record(user_id, file_name, file_path)

    def save_file_record(user_id, file_name, file_path):
        conn = sqlite3.connect('DataAnalysisApp/database.db')
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO user_result_history (result_name, result_path, user_informationid) VALUES (?, ?, ?)", 
            (file_name, file_path, user_id)
        )
        conn.commit()
        conn.close()

    results_win = tk.Toplevel()
    results_win.title(window_title)
    
    tree = ttk.Treeview(results_win, columns=columns, show="headings", height=10)
    tree.pack(padx=10, pady=10, fill='both', expand=True)
    
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", width=80)
    
    for index, row in data.iterrows():
        values = [row[col] for col in columns]
        tree.insert("", "end", values=values)

    response_text = tk.Text(results_win, height=10, width=50)
    response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    if analysis_function:
        analyze_button = ttk.Button(results_win, text="Request Analysis", command=invoke_analysis)
        analyze_button.pack(pady=10)

    save_button = ttk.Button(results_win, text="Save to CSV", command=save_to_csv)
    save_button.pack(pady=10)

def load_data(user_id, filename):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT file_history FROM user_history WHERE user_id = ? AND file_name = ?", (user_id, filename))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def select_item(event, listbox, user_id):
    if listbox.curselection():
        index = int(listbox.curselection()[0])
        selected = listbox.get(index)
        file_path = load_data(user_id, selected)
        return selected, file_path
    return None, None

def on_select(event, user_id, listbox, selected_file_entry, dataframe_container):
    selected, file_path = select_item(event, listbox, user_id)
    if selected:
        selected_file_entry.delete(0, tk.END)
        selected_file_entry.insert(0, selected)
        
        dataframe_container["dataframe"] = send_data(file_path)

def send_data(file_path):
    if file_path:
        try:
            dataframe = pd.read_csv(file_path)
            return dataframe  
        except Exception as e:
            messagebox.showerror("Eroare la încărcarea fișierului", str(e))
            return pd.DataFrame()  
    else:
        messagebox.showinfo("Informație", "Calea fișierului nu a fost găsită în baza de date.")
        return pd.DataFrame()  
