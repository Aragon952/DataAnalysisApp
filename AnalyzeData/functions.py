import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import openai
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from scipy.stats import chi2_contingency
from mlxtend.frequent_patterns import apriori, association_rules
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import sqlite3
import os


try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')


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


api_key = "sk-proj-PBFLHil6BVfWS860yS27T3BlbkFJsp0W4Nt469C3EAMg9nqY"
openai.api_key = api_key

def request_analysis(response_text, stats_data, generate_message):
    if not openai.api_key:
        raise ValueError("Cheia API OpenAI nu este setată. Vă rugăm să o setați și să încercați din nou.")

    messages = [
        {"role": "system", "content": "Esti un asistent inteligent insarcinat cu analiza datelor statistice."},
        {"role": "assistant", "content": generate_message(stats_data)}
    ]

    try:
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        reply = chat.choices[0].message['content']
        response_text.insert(tk.END, "ChatGPT: " + reply + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"Interactiune cu ChatGPT nereusita {str(e)}")
        response_text.insert(tk.END, "Nu s-a putut prelua o analiză.\n")

def save_csv(dataframe, user_id):
    print("Data saved successfully.")

def save_picture(dataframe, user_id):
    print("Picture saved successfully.")

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


def apply_descriptive_statistics(dataframe, columns, user_id):
    columns_stats = ['Column_Name', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']

    def generate_statistics_message(stats_df):
        prompt_stats = "Here are the descriptive statistics, please analyze:\n"
        for _, row in stats_df.iterrows():
            prompt_stats += f"{row['Column_Name']} - Count: {row['Count']}, Mean: {row['Mean']}, Std Dev: {row['Std']}, Min: {row['Min']}, 25%: {row['25%']}, Median: {row['50%']}, 75%: {row['75%']}, Max: {row['Max']}\n"
        return prompt_stats

    def apply_statistics(selected_columns):
        if not selected_columns:
            messagebox.showerror("Error", "No columns selected. Please select at least one column.")
            return

        stats_rows = []
        for column in selected_columns:
            if column in dataframe.columns:
                desc_stats = dataframe[column].describe()
                row = [column] + desc_stats.tolist()
                stats_rows.append(pd.Series(row, index=columns_stats))

        stats_df = pd.DataFrame(stats_rows, columns=columns_stats)
        stats_df['Column_Name'] = selected_columns
        display_results("Descriptive Statistics Results", stats_df, columns_stats, user_id, request_analysis, generate_statistics_message)

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

    apply_button = ttk.Button(main_frame, text="Calculate Statistics for Selected Columns", 
                              command=lambda: apply_statistics([listbox.get(i) for i in listbox.curselection()]))
    apply_button.pack(pady=10)

    top.mainloop()

def apply_linear_regression(dataframe, columns):
    def generate_regression_message(results):
        prompt_stats = "Here are the linear regression results, please analyze:\n"
        prompt_stats += f"R-squared: {results.rsquared}, Adjusted R-squared: {results.rsquared_adj}\n"
        prompt_stats += f"F-statistic: {results.fvalue}, Prob (F-statistic): {results.f_pvalue}\n"
        for param_name, param in results.params.items():
            prompt_stats += f"{param_name}: Coefficient = {param}, P>|t| = {results.pvalues[param_name]}\n"
        return prompt_stats

    def perform_regression(listbox_dep, listbox_indep):
        dep_var = listbox_dep.get(listbox_dep.curselection())
        indep_vars = [listbox_indep.get(i) for i in listbox_indep.curselection()]
        
        if not dep_var or not indep_vars:
            messagebox.showerror("Error", "Please select at least one dependent and one or more independent variables.")
            return

        X = dataframe[indep_vars]
        X = sm.add_constant(X) 
        y = dataframe[dep_var]

        model = sm.OLS(y, X)
        results = model.fit()
        display_results("Regression Results", results, generate_regression_message)

    top = tk.Toplevel()
    top.title("Perform Linear Regression")

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_dep = ttk.Label(main_frame, text="Select the dependent variable:")
    label_dep.pack(padx=10, pady=5)
    listbox_dep = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=6)
    listbox_dep.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_indep = ttk.Label(main_frame, text="Select the independent variables:")
    label_indep.pack(padx=10, pady=5)
    listbox_indep = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    listbox_indep.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    for col in columns:
        listbox_dep.insert(tk.END, col)
        listbox_indep.insert(tk.END, col)

    button_run = ttk.Button(main_frame, text="Run Regression", command=lambda: perform_regression(listbox_dep, listbox_indep))
    button_run.pack(pady=20)

    top.mainloop()

def apply_logistic_regression(dataframe, columns):
    def perform_logistic_regression(dep_var, indep_vars):
        formula = f"{dep_var} ~ " + " + ".join(indep_vars)
        model = smf.logit(formula, data=dataframe).fit(disp=0)
        return model

    def show_results(model):
        results_win = tk.Toplevel()
        results_win.title("Logistic Regression Results")
        text = tk.Text(results_win, wrap="word")
        text.insert(tk.END, model.summary().as_text())
        text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        response_text = tk.Text(results_win, height=10, width=50)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        analyze_button = ttk.Button(results_win, text="Request ChatGPT Analysis",
                                    command=lambda: request_analysis(response_text, model, generate_logistic_regression_message))
        analyze_button.pack(pady=10)

    def generate_logistic_regression_message(model):
        prompt_stats = "Here are the logistic regression results, please analyze all the values:\n"
        prompt_stats += f"Log-Likelihood: {model.llf}\n"
        prompt_stats += f"Pseudo R-squ.: {model.prsquared}\n"
        for param in model.params.index:
            prompt_stats += f"{param}: Coefficient = {model.params[param]}, P-value = {model.pvalues[param]}\n"
        return prompt_stats

    top = tk.Toplevel()
    top.title("Perform Logistic Regression")

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_dep = ttk.Label(main_frame, text="Select the dependent variable (binary):")
    label_dep.pack(padx=10, pady=5)
    listbox_dep = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=6)
    listbox_dep.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_indep = ttk.Label(main_frame, text="Select the independent variables:")
    label_indep.pack(padx=10, pady=5)
    listbox_indep = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    listbox_indep.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    for col in columns:
        listbox_dep.insert(tk.END, col)
        listbox_indep.insert(tk.END, col)

    button_run = ttk.Button(main_frame, text="Run Logistic Regression", command=lambda: show_results(perform_logistic_regression(listbox_dep.get(listbox_dep.curselection()), [listbox_indep.get(i) for i in listbox_indep.curselection()])))
    button_run.pack(pady=20)

    top.mainloop()

def apply_cluster_analysis(dataframe, columns):
    root = tk.Tk()
    root.title("Perform Cluster Analysis")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Select the first variable for clustering:").pack(padx=10, pady=5)
    var1 = ttk.Combobox(main_frame, values=columns, state="readonly")
    var1.pack(padx=10, pady=5)

    ttk.Label(main_frame, text="Select the second variable for clustering:").pack(padx=10, pady=5)
    var2 = ttk.Combobox(main_frame, values=columns, state="readonly")
    var2.pack(padx=10, pady=5)

    ttk.Label(main_frame, text="Enter number of clusters:").pack(padx=10, pady=5)
    num_clusters_entry = ttk.Entry(main_frame, width=10)
    num_clusters_entry.pack(padx=10, pady=5)

    def on_run():
        try:
            selected_columns = [var1.get(), var2.get()]
            num_clusters = int(num_clusters_entry.get())
            perform_clustering(num_clusters, selected_columns)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    ttk.Button(main_frame, text="Run Clustering", command=on_run).pack(pady=20)

    def perform_clustering(num_clusters, selected_columns):
        X = dataframe[selected_columns].values
        kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=0).fit(X)
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_

        fig, ax = plt.subplots()
        scatter = ax.scatter(X[:, 0], X[:, 1], c=labels, cmap='viridis', marker='o', alpha=0.5)
        ax.scatter(centroids[:, 0], centroids[:, 1], s=300, c='red', marker='x')
        ax.set_xlabel(selected_columns[0])
        ax.set_ylabel(selected_columns[1])
        ax.set_title('Cluster Analysis Result')
        plt.colorbar(scatter, ax=ax, label='Cluster Label')
        plt.show()

    root.mainloop()

def apply_correlation_analysis(dataframe, columns):
    def generate_correlation_prompt(correlation_data):
        var1, var2, correlation = correlation_data
        return f"Corelația dintre {var1} și {var2} este {correlation:.2f}. Poți să analizezi implicațiile acestei relații?"

    root = tk.Tk()
    root.title("Analiza de Corelație")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var1 = ttk.Label(main_frame, text="Selectează prima variabilă:")
    label_var1.pack(padx=10, pady=5)
    var1 = ttk.Combobox(main_frame, values=columns, state="readonly")
    var1.pack(padx=10, pady=5)

    label_var2 = ttk.Label(main_frame, text="Selectează a doua variabilă:")
    label_var2.pack(padx=10, pady=5)
    var2 = ttk.Combobox(main_frame, values=columns, state="readonly")
    var2.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Calculează Corelația", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            if not var1.get() or not var2.get():
                raise ValueError("Selectează ambele variabile.")
            correlation = dataframe[[var1.get(), var2.get()]].corr().iloc[0, 1]
            show_results(var1.get(), var2.get(), correlation)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def show_results(var1, var2, correlation):
        results_win = tk.Toplevel()
        results_win.title("Rezultate Corelație")

        results_frame = ttk.Frame(results_win, padding="3 3 12 12")
        results_frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(results_frame, columns=("Coloana1", "Coloana2", "Corelatie"), show="headings")
        tree.heading("Coloana1", text="Nume Coloana 1")
        tree.heading("Coloana2", text="Nume Coloana 2")
        tree.heading("Corelatie", text="Corelație")
        tree.pack(padx=10, pady=10, expand=True)
        tree.insert("", "end", values=(var1, var2, f"{correlation:.2f}"))

        response_text = tk.Text(results_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        correlation_data = (var1, var2, correlation)
        analyze_button = ttk.Button(results_frame, text="Analizează cu ChatGPT", command=lambda: request_analysis(response_text, correlation_data, generate_correlation_prompt))
        analyze_button.pack(pady=10)

    root.mainloop()

def apply_pca(dataframe, columns):
    def generate_pca_prompt(pca_data):
        explained_variance = pca_data['explained_variance']
        components = pca_data['components']
        prompt = "Rezultatele analizei PCA sunt următoarele:\n"
        prompt += f"Varianța explicată: {explained_variance}\n"
        for i, component in enumerate(components):
            prompt += f"Componenta {i+1}: {component}\n"
        prompt += "Poți analiza aceste rezultate?"
        return prompt
    
    root = tk.Toplevel()
    root.title("Analiza PCA")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    
    label_var = ttk.Label(main_frame, text="Selectează variabilele:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    
    label_num_components = ttk.Label(main_frame, text="Introduceți numărul de componente principale:")
    label_num_components.pack(padx=10, pady=5)
    num_components_entry = ttk.Entry(main_frame, width=10)
    num_components_entry.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Rulează PCA", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Selectează cel puțin o variabilă.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            num_components = int(num_components_entry.get())
            if num_components < 1 or num_components > len(selected_columns):
                raise ValueError("Numărul de componente trebuie să fie între 1 și numărul de variabile selectate.")
            pca_results = perform_pca(selected_columns, num_components)
            show_results(selected_columns, pca_results)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_pca(selected_columns, num_components):
        X = dataframe[selected_columns].values
        pca = PCA(n_components=num_components)
        components = pca.fit_transform(X)
        explained_variance = pca.explained_variance_ratio_
        return {'explained_variance': explained_variance, 'components': components, 'selected_columns': selected_columns}

    def show_results(selected_columns, pca_results):
        
        results_win = tk.Toplevel()
        results_win.title("Rezultate PCA")

        results_frame = ttk.Frame(results_win, padding="3 3 12 12")
        results_frame.pack(fill=tk.BOTH, expand=True)

        
        tree_columns = ["Componenta", "Varianța Explicată"] + [f"Variabilă {i+1}" for i in range(len(selected_columns))]
        tree = ttk.Treeview(results_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.pack(padx=10, pady=10, expand=True)

        
        for i, var_exp in enumerate(pca_results['explained_variance']):
            values = [f"Componenta {i+1}", f"{var_exp:.2f}"] + [f"{v:.2f}" for v in pca_results['components'][:, i]]
            tree.insert("", "end", values=values)

        response_text = tk.Text(results_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        pca_data = {'explained_variance': pca_results['explained_variance'], 'components': pca_results['components']}
        analyze_button = ttk.Button(results_frame, text="Analizează cu ChatGPT", command=lambda: request_analysis(response_text, pca_data, generate_pca_prompt))
        analyze_button.pack(pady=10)

    root.mainloop()

def apply_lda(dataframe, columns):
    def generate_lda_prompt(lda_data):
        explained_variance = lda_data['explained_variance']
        components = lda_data['components']
        prompt = "Rezultatele analizei LDA sunt următoarele:\n"
        prompt += f"Varianța explicată: {explained_variance}\n"
        for i, component in enumerate(components):
            prompt += f"Componenta {i+1}: {component}\n"
        prompt += "Poți analiza aceste rezultate?"
        return prompt

    root = tk.Toplevel()
    root.title("Analiza LDA")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    
    label_var = ttk.Label(main_frame, text="Selectează variabilele:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    
    label_class = ttk.Label(main_frame, text="Selectează coloana de clasă:")
    label_class.pack(padx=10, pady=5)
    class_var = ttk.Combobox(main_frame, values=columns, state="readonly")
    class_var.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Rulează LDA", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Selectează cel puțin o variabilă.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            class_column = class_var.get()
            if not class_column:
                raise ValueError("Selectează coloana de clasă.")
            lda_results = perform_lda(selected_columns, class_column)
            show_results(selected_columns, class_column, lda_results)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_lda(selected_columns, class_column):
        X = dataframe[selected_columns].values
        y = dataframe[class_column].values
        lda = LDA()
        components = lda.fit_transform(X, y)
        explained_variance = lda.explained_variance_ratio_
        return {'explained_variance': explained_variance, 'components': components, 'selected_columns': selected_columns}

    def show_results(selected_columns, class_column, lda_results):
        
        results_win = tk.Toplevel(root)
        results_win.title("Rezultate LDA")

        results_frame = ttk.Frame(results_win, padding="3 3 12 12")
        results_frame.pack(fill=tk.BOTH, expand=True)

        
        tree_columns = ["Componenta", "Varianța Explicată"] + [f"Variabilă {i+1}" for i in range(len(selected_columns))]
        tree = ttk.Treeview(results_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.pack(padx=10, pady=10, expand=True)

        
        for i, var_exp in enumerate(lda_results['explained_variance']):
            values = [f"Componenta {i+1}", f"{var_exp:.2f}"] + [f"{v:.2f}" for v in lda_results['components'][:, i]]
            tree.insert("", "end", values=values)

        response_text = tk.Text(results_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        lda_data = {'explained_variance': lda_results['explained_variance'], 'components': lda_results['components']}
        analyze_button = ttk.Button(results_frame, text="Analizează cu ChatGPT", command=lambda: request_analysis(response_text, lda_data, generate_lda_prompt))
        analyze_button.pack(pady=10)

    root.mainloop()

def generate_bayesian_prompt(bayesian_data):
    accuracy = bayesian_data['accuracy']
    precision = bayesian_data['precision']
    recall = bayesian_data['recall']
    f1_score = bayesian_data['f1_score']
    prompt = (
        f"Rezultatele metodei bayesiene sunt următoarele:\n"
        f"Acuratețea clasificării: {accuracy:.2f}\n"
        f"Precizia: {precision:.2f}\n"
        f"Rata de reamintire: {recall:.2f}\n"
        f"Scorul F1: {f1_score:.2f}\n"
        "Poți analiza aceste rezultate?"
    )
    return prompt

def apply_bayesian_methods(dataframe, columns):
    root = tk.Toplevel()
    root.title("Metode Bayesiene")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    
    label_var = ttk.Label(main_frame, text="Selectează variabilele:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    
    label_class = ttk.Label(main_frame, text="Selectează coloana de clasă:")
    label_class.pack(padx=10, pady=5)
    class_var = ttk.Combobox(main_frame, values=columns, state="readonly")
    class_var.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Rulează Metoda Bayesiana", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Selectează cel puțin o variabilă.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            class_column = class_var.get()
            if not class_column:
                raise ValueError("Selectează coloana de clasă.")
            bayesian_results = perform_bayesian_methods(selected_columns, class_column)
            show_results(selected_columns, class_column, bayesian_results)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_bayesian_methods(selected_columns, class_column):
        X = dataframe[selected_columns].values
        y = dataframe[class_column].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = GaussianNB()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=1)
        recall = recall_score(y_test, y_pred, average='weighted', zero_division=1)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=1)
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'selected_columns': selected_columns
        }

    def show_results(selected_columns, class_column, bayesian_results):
        results_win = tk.Toplevel(root)
        results_win.title("Rezultate Metode Bayesiene")

        results_frame = ttk.Frame(results_win, padding="3 3 12 12")
        results_frame.pack(fill=tk.BOTH, expand=True)

        
        tree_columns = ["Metrică", "Valoare"]
        tree = ttk.Treeview(results_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=150)
        tree.pack(padx=10, pady=10, expand=True)

        
        tree.insert("", "end", values=("Acuratețea clasificării", f"{bayesian_results['accuracy']:.2f}"))
        tree.insert("", "end", values=("Precizia", f"{bayesian_results['precision']:.2f}"))
        tree.insert("", "end", values=("Rata de reamintire", f"{bayesian_results['recall']:.2f}"))
        tree.insert("", "end", values=("Scorul F1", f"{bayesian_results['f1_score']:.2f}"))

        response_text = tk.Text(results_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        bayesian_data = {
            'accuracy': bayesian_results['accuracy'],
            'precision': bayesian_results['precision'],
            'recall': bayesian_results['recall'],
            'f1_score': bayesian_results['f1_score']
        }
        analyze_button = ttk.Button(results_frame, text="Analizează cu ChatGPT", command=lambda: request_analysis(response_text, bayesian_data, generate_bayesian_prompt))
        analyze_button.pack(pady=10)

    root.mainloop()

def apply_frequency_distribution(dataframe, columns):
    root = tk.Toplevel()
    root.title("Distribuția Frecvenței")

    main_canvas = tk.Canvas(root)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    main_scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
    main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    main_frame = ttk.Frame(main_canvas)
    main_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(
            scrollregion=main_canvas.bbox("all")
        )
    )

    main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=main_scrollbar.set)

    label_var = ttk.Label(main_frame, text="Selectează coloanele pentru distribuția frecvenței:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    display_option = tk.StringVar(value="table")
    radio_table = ttk.Radiobutton(main_frame, text="Afișare Tabelară", variable=display_option, value="table")
    radio_table.pack(anchor=tk.W, padx=10, pady=2)
    radio_chart = ttk.Radiobutton(main_frame, text="Afișare Grafică", variable=display_option, value="chart")
    radio_chart.pack(anchor=tk.W, padx=10, pady=2)

    button_run = ttk.Button(main_frame, text="Calculează Distribuția Frecvenței", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Selectează cel puțin o coloană.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            frequency_results = perform_frequency_distribution(selected_columns)
            if display_option.get() == "table":
                show_results_table(selected_columns, frequency_results)
            else:
                show_results_chart(selected_columns, frequency_results)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_frequency_distribution(selected_columns):
        frequency_results = {}
        for col in selected_columns:
            frequency_results[col] = dataframe[col].value_counts()
        return frequency_results

    def show_results_table(selected_columns, frequency_results):
        for widget in main_frame.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Treeview) or isinstance(widget, tk.Canvas):
                widget.destroy()

        for col in selected_columns:
            label = ttk.Label(main_frame, text=f"Distribuția frecvenței pentru {col}:")
            label.pack()

            frame = ttk.Frame(main_frame)
            frame.pack(fill=tk.BOTH, expand=True)

            canvas = tk.Canvas(frame)
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            scrollable_frame = ttk.Frame(canvas)
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")
                )
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            tree_columns = ["Valoare", "Frecvență"]
            tree = ttk.Treeview(scrollable_frame, columns=tree_columns, show="headings")
            tree.heading("Valoare", text="Valoare")
            tree.heading("Frecvență", text="Frecvență")
            tree.pack(padx=10, pady=10, expand=True)

            for value, count in frequency_results[col].items():
                tree.insert("", "end", values=(value, count))

    def show_results_chart(selected_columns, frequency_results):
        fig, ax = plt.subplots(len(selected_columns), 1, figsize=(10, 5 * len(selected_columns)))
        if len(selected_columns) == 1:
            ax = [ax]
        for i, col in enumerate(selected_columns):
            frequency_results[col].plot(kind='bar', ax=ax[i])
            ax[i].set_title(f"Distribuția frecvenței pentru {col}")
            ax[i].set_xlabel("Valoare")
            ax[i].set_ylabel("Frecvență")
        plt.tight_layout()
        plt.show()

    root.mainloop()

def apply_contingency_table(dataframe, columns):
    root = tk.Toplevel()
    root.title("Tabel de Contingență")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var1 = ttk.Label(main_frame, text="Selectează prima coloană pentru tabelul de contingență:")
    label_var1.pack(padx=10, pady=5)
    listbox_var1 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=10)
    for col in columns:
        listbox_var1.insert(tk.END, col)
    listbox_var1.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_var2 = ttk.Label(main_frame, text="Selectează a doua coloană pentru tabelul de contingență:")
    label_var2.pack(padx=10, pady=5)
    listbox_var2 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=10)
    for col in columns:
        listbox_var2.insert(tk.END, col)
    listbox_var2.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    button_run = ttk.Button(main_frame, text="Calculează Tabelul de Contingență", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_col1 = listbox_var1.get(listbox_var1.curselection())
            selected_col2 = listbox_var2.get(listbox_var2.curselection())
            if not selected_col1 or not selected_col2:
                raise ValueError("Selectează câte o coloană din fiecare listă.")
            if selected_col1 == selected_col2:
                raise ValueError("Selectează coloane diferite.")
            contingency_table = perform_contingency_table([selected_col1, selected_col2])
            show_results([selected_col1, selected_col2], contingency_table)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_contingency_table(selected_columns):
        col1, col2 = selected_columns
        contingency_table = pd.crosstab(dataframe[col1], dataframe[col2])
        return contingency_table

    def show_results(selected_columns, contingency_table):
        for widget in main_frame.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Treeview) or isinstance(widget, tk.Canvas):
                widget.destroy()

        label = ttk.Label(main_frame, text=f"Tabel de contingență pentru {selected_columns[0]} și {selected_columns[1]}:")
        label.pack()

        
        frame = ttk.Frame(main_frame)
        frame.pack(fill=tk.BOTH, expand=True)

        
        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        
        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        tree_columns = [""] + list(contingency_table.columns)
        tree = ttk.Treeview(scrollable_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        tree.pack(padx=10, pady=10, expand=True)

        for index, row in contingency_table.iterrows():
            values = [index] + row.tolist()
            tree.insert("", "end", values=values)

    root.mainloop()

def apply_chi_square_test(dataframe, columns):
    root = tk.Toplevel()
    root.title("Testul Chi-pătrat")

    
    main_canvas = tk.Canvas(root)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    
    main_scrollbar = ttk.Scrollbar(root, orient="vertical", command=main_canvas.yview)
    main_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    
    main_frame = ttk.Frame(main_canvas)
    main_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(
            scrollregion=main_canvas.bbox("all")
        )
    )

    main_canvas.create_window((0, 0), window=main_frame, anchor="nw")
    main_canvas.configure(yscrollcommand=main_scrollbar.set)

    label_var1 = ttk.Label(main_frame, text="Selectează prima coloană pentru testul Chi-pătrat:")
    label_var1.pack(padx=10, pady=5)
    listbox_var1 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=10)
    for col in columns:
        listbox_var1.insert(tk.END, col)
    listbox_var1.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_var2 = ttk.Label(main_frame, text="Selectează a doua coloană pentru testul Chi-pătrat:")
    label_var2.pack(padx=10, pady=5)
    listbox_var2 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=10)
    for col in columns:
        listbox_var2.insert(tk.END, col)
    listbox_var2.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    button_run = ttk.Button(main_frame, text="Calculează Testul Chi-pătrat", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_col1 = listbox_var1.get(listbox_var1.curselection())
            selected_col2 = listbox_var2.get(listbox_var2.curselection())
            if not selected_col1 or not selected_col2:
                raise ValueError("Selectează câte o coloană din fiecare listă.")
            if selected_col1 == selected_col2:
                raise ValueError("Selectează coloane diferite.")
            chi_square_results = perform_chi_square_test([selected_col1, selected_col2])
            show_results([selected_col1, selected_col2], chi_square_results)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_chi_square_test(selected_columns):
        col1, col2 = selected_columns
        contingency_table = pd.crosstab(dataframe[col1], dataframe[col2])
        chi2, p, dof, expected = chi2_contingency(contingency_table)
        return {'chi2': chi2, 'p_value': p, 'dof': dof, 'expected': expected, 'contingency_table': contingency_table}

    def generate_chi_square_prompt(results):
        prompt = (
            f"Rezultatele testului Chi-pătrat sunt următoarele:\n"
            f"Chi-squared: {results['chi2']:.4f}\n"
            f"P-value: {results['p_value']:.4f}\n"
            f"Degrees of Freedom: {results['dof']}\n\n"
            f"Tabel de contingență observat:\n{results['contingency_table']}\n\n"
            f"Tabel de contingență așteptat:\n"
            f"{pd.DataFrame(results['expected'], index=results['contingency_table'].index, columns=results['contingency_table'].columns)}"
            "\nPoți analiza aceste rezultate?"
        )
        return prompt

    def show_results(selected_columns, chi_square_results):
        for widget in main_frame.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Treeview) or isinstance(widget, tk.Canvas) or isinstance(widget, tk.Text):
                widget.destroy()

        label = ttk.Label(main_frame, text=f"Testul Chi-pătrat pentru {selected_columns[0]} și {selected_columns[1]}:")
        label.pack()

        
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)

        chi2_label = ttk.Label(results_frame, text=f"Chi-squared: {chi_square_results['chi2']:.4f}")
        chi2_label.pack(pady=5)
        p_value_label = ttk.Label(results_frame, text=f"P-value: {chi_square_results['p_value']:.4f}")
        p_value_label.pack(pady=5)
        dof_label = ttk.Label(results_frame, text=f"Degrees of Freedom: {chi_square_results['dof']}")
        dof_label.pack(pady=5)

        
        obs_label = ttk.Label(results_frame, text="Tabelul de contingență observat:")
        obs_label.pack()
        create_treeview(results_frame, chi_square_results['contingency_table'], "Observat")

        exp_label = ttk.Label(results_frame, text="Tabelul de contingență așteptat:")
        exp_label.pack()
        expected_df = pd.DataFrame(chi_square_results['expected'], index=chi_square_results['contingency_table'].index, columns=chi_square_results['contingency_table'].columns)
        create_treeview(results_frame, expected_df, "Așteptat")

        
        response_text = tk.Text(main_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        
        analyze_button = ttk.Button(main_frame, text="Analizează cu ChatGPT", command=lambda: request_analysis(response_text, chi_square_results, generate_chi_square_prompt))
        analyze_button.pack(pady=10)

    def create_treeview(parent, data, label):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        tree_columns = [""] + list(data.columns)
        tree = ttk.Treeview(scrollable_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        tree.pack(padx=10, pady=10, expand=True)

        for index, row in data.iterrows():
            values = [index] + row.tolist()
            tree.insert("", "end", values=values)

    root.mainloop()

def generate_association_message(rules):
    prompt = "Here are the association rules, please analyze:\n\n"
    for _, row in rules.iterrows():
        prompt += f"Antecedents: {', '.join(list(row['antecedents']))}\n"
        prompt += f"Consequents: {', '.join(list(row['consequents']))}\n"
        prompt += f"Support: {row['support']}\n"
        prompt += f"Confidence: {row['confidence']}\n"
        prompt += f"Lift: {row['lift']}\n\n"
    return prompt

def apply_association_analysis(dataframe, columns):
    root = tk.Toplevel()
    root.title("Analiza Asocierilor")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    
    main_canvas = tk.Canvas(main_frame)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    
    vsb = ttk.Scrollbar(main_frame, orient="vertical", command=main_canvas.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=main_canvas.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    main_canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    
    scrollable_frame = ttk.Frame(main_canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(
            scrollregion=main_canvas.bbox("all")
        )
    )

    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    label_var = ttk.Label(scrollable_frame, text="Selectează coloanele pentru analiza asocierilor:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(scrollable_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    min_support_label = ttk.Label(scrollable_frame, text="Introdu valoarea minimă pentru suport (ex: 0.5):")
    min_support_label.pack(padx=10, pady=5)
    min_support_entry = ttk.Entry(scrollable_frame)
    min_support_entry.pack(padx=10, pady=5, fill=tk.X)

    min_confidence_label = ttk.Label(scrollable_frame, text="Introdu valoarea minimă pentru încredere (ex: 0.5):")
    min_confidence_label.pack(padx=10, pady=5)
    min_confidence_entry = ttk.Entry(scrollable_frame)
    min_confidence_entry.pack(padx=10, pady=5, fill=tk.X)

    button_run = ttk.Button(scrollable_frame, text="Calculează Reguli de Asociere", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Selectează cel puțin o coloană.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            min_support = float(min_support_entry.get())
            min_confidence = float(min_confidence_entry.get())
            association_results = perform_association_analysis(selected_columns, min_support, min_confidence)
            show_results(association_results)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_association_analysis(selected_columns, min_support, min_confidence):
        df_selected = dataframe[selected_columns].astype(bool)  
        frequent_itemsets = apriori(df_selected, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        return rules

    def show_results(rules):
        for widget in scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Treeview) or isinstance(widget, tk.Text):
                widget.destroy()

        label = ttk.Label(scrollable_frame, text="Reguli de asociere:")
        label.pack()

        tree_columns = ["antecedents", "consequents", "support", "confidence", "lift"]
        tree = ttk.Treeview(scrollable_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        tree.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        for _, row in rules.iterrows():
            values = [', '.join(list(row['antecedents'])), ', '.join(list(row['consequents'])), row['support'], row['confidence'], row['lift']]
            tree.insert("", "end", values=values)

        
        response_text = tk.Text(scrollable_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        
        analyze_button = ttk.Button(scrollable_frame, text="Analizează cu ChatGPT", command=lambda: request_analysis(response_text, rules, generate_association_message))
        analyze_button.pack(pady=10)

    root.mainloop()

def apply_sentiment_analysis(dataframe, columns):
    def generate_sentiment_message(sentiment_results):
        prompt = "Here are the sentiment analysis results, please analyze:\n\n"
        for _, row in sentiment_results.iterrows():
            prompt += f"Text: {row['Text']}\n"
            prompt += f"Negative: {row['Negative']}, Neutral: {row['Neutral']}, Positive: {row['Positive']}, Compound: {row['Compound']}\n\n"
        return prompt
    
    root = tk.Toplevel()
    root.title("Analiza Sentimentelor")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    main_canvas = tk.Canvas(main_frame)
    main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    vsb = ttk.Scrollbar(main_frame, orient="vertical", command=main_canvas.yview)
    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    hsb = ttk.Scrollbar(main_frame, orient="horizontal", command=main_canvas.xview)
    hsb.pack(side=tk.BOTTOM, fill=tk.X)
    main_canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    scrollable_frame = ttk.Frame(main_canvas)
    scrollable_frame.bind(
        "<Configure>",
        lambda e: main_canvas.configure(
            scrollregion=main_canvas.bbox("all")
        )
    )

    main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    label_var = ttk.Label(scrollable_frame, text="Selectează coloanele pentru analiza sentimentelor:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(scrollable_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    button_run = ttk.Button(scrollable_frame, text="Analizează Sentimentele", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Selectează cel puțin o coloană.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            sentiment_results = perform_sentiment_analysis(selected_columns)
            show_results(sentiment_results)
        except ValueError as e:
            messagebox.showerror("Eroare", str(e))

    def perform_sentiment_analysis(selected_columns):
        sia = SentimentIntensityAnalyzer()
        results = []
        for index, row in dataframe.iterrows():
            for column in selected_columns:
                sentiment_score = sia.polarity_scores(str(row[column]))
                results.append({
                    'Index': index,
                    'Column': column,
                    'Text': row[column],
                    'Negative': sentiment_score['neg'],
                    'Neutral': sentiment_score['neu'],
                    'Positive': sentiment_score['pos'],
                    'Compound': sentiment_score['compound']
                })
        return pd.DataFrame(results)

    def show_results(sentiment_results):
        for widget in scrollable_frame.winfo_children():
            if isinstance(widget, ttk.Label) or isinstance(widget, ttk.Treeview) or isinstance(widget, tk.Text):
                widget.destroy()

        label = ttk.Label(scrollable_frame, text="Rezultatele Analizei Sentimentelor:")
        label.pack()

        tree_columns = ["Index", "Column", "Text", "Negative", "Neutral", "Positive", "Compound"]
        tree = ttk.Treeview(scrollable_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        tree.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        for _, row in sentiment_results.iterrows():
            values = [row[col] for col in tree_columns]
            tree.insert("", "end", values=values)

        
        response_text = tk.Text(scrollable_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        
        analyze_button = ttk.Button(scrollable_frame, text="Analizează cu ChatGPT", command=lambda: request_analysis(response_text, sentiment_results, generate_sentiment_message))
        analyze_button.pack(pady=10)

    root.mainloop()

