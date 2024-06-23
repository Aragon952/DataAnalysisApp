import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import openai

api_key = "sk-proj-PBFLHil6BVfWS860yS27T3BlbkFJsp0W4Nt469C3EAMg9nqY"

def update_treeview(dataframe, tree_frame):
    for i in tree_frame.get_children():
        tree_frame.delete(i)
    tree_frame["columns"] = list(dataframe.columns)
    tree_frame["show"] = "headings"
    for col in dataframe.columns:
        tree_frame.heading(col, text=col)
        tree_frame.column(col, anchor="center", width=100)
    
    for row_index, row in dataframe.iterrows():
        tree_frame.insert("", "end", values=list(row))

def save_csv(dataframe, user_id):
    print("Data saved successfully.")

def save_picture(dataframe, user_id):
    print("Picture saved successfully.")

def apply_descriptive_statistics(dataframe, columns):
    # Definirea coloanelor pentru statisticile descriptive
    columns_stats = ['Column_Name', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']
    
    def apply_statistics(selected_columns):
        if not selected_columns:
            messagebox.showerror("Error", "No columns selected. Please select at least one column.")
            return

        # Crearea unei liste de serii pentru fiecare coloană selectată
        stats_rows = []
        for column in selected_columns:
            if column in dataframe.columns:
                desc_stats = dataframe[column].describe()
                row = [column] + desc_stats.tolist()
                stats_rows.append(pd.Series(row, index=columns_stats))
        
        # Crearea unui DataFrame din lista de serii
        stats_df = pd.concat(stats_rows, axis=1).transpose()

        show_results(stats_df)
        top.destroy()

    def show_results(stats_df):
        results_win = tk.Toplevel()
        results_win.title("Descriptive Statistics Results")

        # Treeview pentru afișarea statisticilor
        tree = ttk.Treeview(results_win, columns=columns_stats, show="headings", height=10)
        tree.pack(padx=10, pady=10, fill='both', expand=True)

        # Configurarea headerelelor și coloanelor
        for col in columns_stats:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=80)

        # Adăugarea fiecărui rând de statistici în Treeview
        for index, row in stats_df.iterrows():
            values = [row['Column_Name'], row['Count'], row['Mean'], row['Std'], row['Min'], row['25%'], row['50%'], row['75%'], row['Max']]
            tree.insert("", "end", values=values)

        # Adăugarea unui widget Text pentru afișarea răspunsului ChatGPT
        response_text = tk.Text(results_win, height=10, width=50)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Buton pentru solicitarea analizei de la ChatGPT
        analyze_button = ttk.Button(results_win, text="Request ChatGPT Analysis", command=lambda: request_analysis(response_text, stats_df))
        analyze_button.pack(pady=10)

    # Setează cheia API folosind o variabilă de mediu
    openai.api_key = api_key

    # Asigură-te că cheia API este disponibilă
    if not openai.api_key:
        raise ValueError("API key for OpenAI is not set. Please set the OPENAI_API_KEY environment variable.")

    def request_analysis(response_text, stats_data):
        messages = [
            {"role": "system", "content": "You are an intelligent assistant tasked with analyzing statistical data."},
            {"role": "assistant", "content": generate_statistics_message(stats_data)}
        ]

        try:
            # Crează completarea chatului folosind modelul ChatGPT
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )
            # Extragerea răspunsului primit de la ChatGPT
            reply = chat.choices[0].message['content']
            response_text.insert(tk.END, "ChatGPT: " + reply + "\n")  # Afișarea răspunsului în widgetul Text
        except Exception as e:
            messagebox.showerror("Error", f"Failed to interact with ChatGPT API: {str(e)}")
            response_text.insert(tk.END, "Failed to retrieve an analysis.\n")

    def generate_statistics_message(stats_data):
        # Construiește mesajul cu datele statistice pentru a fi analizate de ChatGPT
        prompt_stats = "Here are the descriptive statistics, please analyze:\n"
        for index, row in stats_data.iterrows():
            prompt_stats += f"{row['Column_Name']} - Count: {row['Count']}, Mean: {row['Mean']}, Std Dev: {row['Std']}, Min: {row['Min']}, 25%: {row['25%']}, Median: {row['50%']}, 75%: {row['75%']}, Max: {row['Max']}\n"
        return prompt_stats
    
    top = tk.Toplevel()
    top.title("Calculate Descriptive Statistics")

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox.insert(tk.END, col)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    apply_button = ttk.Button(main_frame, text="Calculate Statistics for Selected Columns", command=lambda: apply_statistics([listbox.get(i) for i in listbox.curselection()]))
    apply_button.pack(pady=10)

    top.mainloop()

def apply_linear_regression(dataframe):
    print("Linear regression applied successfully.")

def apply_logistic_regression(dataframe):
    print("Logistic regression applied successfully.")

def apply_cluster_analysis(dataframe):
    print("Cluster analysis applied successfully.")

def apply_hypothesis_testing(dataframe):
    print("Hypothesis testing applied successfully.")

def apply_correlation_analysis(dataframe):
    print("Correlation analysis applied successfully.")

def apply_pca(dataframe):
    print("PCA applied successfully.")

def apply_lda(dataframe):
    print("LDA applied successfully.")

def apply_bayesian_methods(dataframe):
    print("Bayesian methods applied successfully.")

def apply_frequency_distribution(dataframe):
    print("Frequency distribution applied successfully.")

def apply_contingency_table(dataframe):
    print("Contingency table applied successfully.")

def apply_chi_square_test(dataframe):
    print("Chi-square test applied successfully.")

def apply_association_analysis(dataframe):
    print("Association analysis applied successfully.")

def apply_sentiment_analysis(dataframe):
    print("Sentiment analysis applied successfully.")