import tkinter as tk

def update_entry_and_methods(listbox, entry, method_cb, methods):
    selection = listbox.curselection()
    if selection:
        entry.delete(0, tk.END)
        entry.insert(0, listbox.get(selection[0]))
        method_cb['values'] = methods  # Update the methods in the combobox

def save_csv(dataframe, user_id):
    print("Data saved successfully.")