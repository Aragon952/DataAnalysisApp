import sqlite3


def select_item(event):
    widget = event.widget
    index = int(widget.curselection()[0])
    value = widget.get(index)
    print("Ai selectat:", value)

def connect_db():
    return sqlite3.connect('DataAnalysisApp/database.db')

def fetch_datasets(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    query = "SELECT file_name FROM user_history WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    datasets = [row[0] for row in cursor.fetchall()]
    conn.close()
    return datasets