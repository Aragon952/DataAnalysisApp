import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import pandas as pd
import numpy as np
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
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

api_key = "Insert your API key"
openai.api_key = api_key

def get_value_from_user(prompt):
    root = tk.Tk()
    root.withdraw()

    user_value = simpledialog.askstring("Input", prompt, parent=root)

    root.destroy()

    return user_value

def save_file_info_to_database(user_id, filename, filepath):
    conn = sqlite3.connect('DataAnalysisApp/database.db')
    cur = conn.cursor()
    try:
        cur.execute('''
            INSERT INTO user_history (user_informationid, file_path, file_name)
            VALUES (?, ?, ?)
        ''', (user_id, filepath, filename))
        conn.commit()
        messagebox.showinfo("Success", "File info saved successfully to database.")
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    finally:
        conn.close()

def save_csv(dataframe, user_id):
    if dataframe.empty:
        messagebox.showwarning("Warning", "There is no data to save.")
        return

    file_name = get_value_from_user("Enter the name for the CSV file:")
    if file_name:
        if not file_name.endswith(".csv"):
            file_name += ".csv"

        directory = f"C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults\\{user_id}\\DataSets"

        if not os.path.exists(directory):
            os.makedirs(directory)

        file_path = os.path.join(directory, file_name)

        dataframe.to_csv(file_path, index=False)

        save_file_info_to_database(user_id, file_name, file_path)

        messagebox.showinfo("Success", f"The dataset was successfully saved to {file_path}")
    else:
        messagebox.showwarning("Warning", "Filename was not provided. Data was not saved.")

def request_analysis(response_text, stats_data, generate_message):
    if not openai.api_key:
        raise ValueError("The OpenAI API key is not set. Please set it and try again.")

    messages = [
        {"role": "system", "content": "You are an intelligent assistant responsible for analyzing statistical data."},
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
        messagebox.showerror("Error", f"Interaction with ChatGPT failed {str(e)}")
        response_text.insert(tk.END, "Could not retrieve an analysis.\n")

def display_results(window_title, data, columns, user_id, analysis_function=None, generate_message=None):
    def invoke_analysis():
        if analysis_function and generate_message:
            analysis_function(response_text, data, generate_message)

    def save_to_csv(user_id, data, results_win):
        base_dir = f"C:\\Users\\user\\Desktop\\Licenta\\GitApp\\DataAndResults\\{user_id}\\Results"
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
        try:
            cur.execute(
                "INSERT INTO user_result_history (result_name, result_path, user_informationid) VALUES (?, ?, ?)", 
                (file_name, file_path, user_id)
            )
            conn.commit()
            messagebox.showinfo("Database Update", "Result record has been saved successfully!")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {e}")
        finally:
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
        
    save_button = ttk.Button(results_win, text="Save to CSV", command=lambda: save_to_csv(user_id, data, results_win))
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

def apply_linear_regression(dataframe, columns, user_id):
    def generate_regression_message(results):
        prompt_stats = "Here are the linear regression results, please analyze:\n"
        for index, row in results.iterrows():
            prompt_stats += f"{row['Parameter']}: {row['Value']}\n"
        return prompt_stats

    def perform_regression(listbox_dep, listbox_indep):
        dep_var = listbox_dep.get(listbox_dep.curselection()[0])
        indep_vars = [listbox_indep.get(i) for i in listbox_indep.curselection()]

        if not dep_var or not indep_vars:
            messagebox.showerror("Error", "Please select at least one dependent and one or more independent variables.")
            return

        X = dataframe[indep_vars]
        X = sm.add_constant(X)
        y = dataframe[dep_var]

        model = sm.OLS(y, X)
        results = model.fit()

        model_stats = pd.DataFrame({
            'Parameter': ['R-squared', 'Adjusted R-squared', 'F-statistic', 'Prob (F-statistic)'],
            'Value': [f"{results.rsquared:.4f}", f"{results.rsquared_adj:.4f}", f"{results.fvalue:.4f}", f"{results.f_pvalue:.4g}"],
            'Coefficient': [None, None, None, None],
            'P-value': [None, None, None, None]
        })

        coef_stats = pd.DataFrame({
            'Parameter': results.params.index,
            'Value': [f"Coefficient = {coef:.4f}" for coef in results.params],
            'Coefficient': results.params.values,
            'P-value': results.pvalues.values
        })

        results_df = pd.concat([model_stats, coef_stats], ignore_index=True)

        display_results("Regression Results", results_df, ['Parameter', 'Value', 'Coefficient', 'P-value'], user_id, request_analysis, generate_message=generate_regression_message)

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

def apply_logistic_regression(dataframe, columns, user_id):
    def generate_logistic_regression_message(results_df):
        prompt_stats = "Here are the logistic regression results, please analyze all the values:\n"
        for index, row in results_df.iterrows():
            prompt_stats += f"{row['Parameter']}: Coefficient = {row['Coefficient']}, P-value = {row['P-value']}\n"
        return prompt_stats

    def perform_logistic_regression(dep_var, indep_vars):
        if dataframe[dep_var].dropna().isin([0, 1]).all():
            formula = f"{dep_var} ~ " + " + ".join(indep_vars)
            model = smf.logit(formula, data=dataframe).fit(disp=0)
            return model
        else:
            messagebox.showerror("Error", "Dependent variable must be binary (0 or 1).")
            return None

    def show_results(model):
        if model is not None:
            results_data = pd.DataFrame({
                'Parameter': ['Log-Likelihood', 'Pseudo R-squared'] + list(model.params.index),
                'Coefficient': [model.llf, model.prsquared] + list(model.params),
                'P-value': [None, None] + list(model.pvalues)
            })

            display_results("Logistic Regression Results", results_data, ['Parameter', 'Coefficient', 'P-value'], user_id, request_analysis, generate_message=generate_logistic_regression_message)

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

    button_run = ttk.Button(main_frame, text="Run Logistic Regression", command=lambda: show_results(perform_logistic_regression(listbox_dep.get(listbox_dep.curselection()[0]), [listbox_indep.get(i) for i in listbox_indep.curselection()])))
    button_run.pack(pady=20)

    top.mainloop()

def apply_cluster_analysis(dataframe, columns, user_id):
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

def apply_correlation_analysis(dataframe, columns, user_id):
    def generate_correlation_prompt(correlation_data):
        var1, var2, correlation = correlation_data
        return f"The correlation between {var1} and {var2} is {correlation:.2f}. Can you analyze the implications of this relationship?"

    root = tk.Tk()
    root.title("Correlation Analysis")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var1 = ttk.Label(main_frame, text="Select the first variable:")
    label_var1.pack(padx=10, pady=5)
    var1 = ttk.Combobox(main_frame, values=columns, state="readonly")
    var1.pack(padx=10, pady=5)

    label_var2 = ttk.Label(main_frame, text="Select the second variable:")
    label_var2.pack(padx=10, pady=5)
    var2 = ttk.Combobox(main_frame, values=columns, state="readonly")
    var2.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Calculate Correlation", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            if not var1.get() or not var2.get():
                raise ValueError("Please select both variables.")
            correlation = dataframe[[var1.get(), var2.get()]].corr().iloc[0, 1]
            show_results(var1.get(), var2.get(), correlation)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_results(var1, var2, correlation):
        results_data = pd.DataFrame({
            'Column1': [var1],
            'Column2': [var2],
            'Correlation': [f"{correlation:.2f}"]
        })
        display_results("Correlation Results", results_data, ['Column1', 'Column2', 'Correlation'], user_id, request_analysis, generate_message=lambda data: generate_correlation_prompt((data.iloc[0]['Column1'], data.iloc[0]['Column2'], float(data.iloc[0]['Correlation']))))

    root.mainloop()

def apply_pca(dataframe, columns, user_id):
    def generate_pca_prompt(pca_data):
        prompt = "The PCA analysis results are as follows:\n\n"
        
        if 'Explained Variance' in pca_data.columns:
            prompt += "Explained Variance:\n"
            for i, var in enumerate(pca_data['Explained Variance']):
                prompt += f"PC{i+1}: {var:.4f}\n"
        
        if 'Cumulative Explained Variance' in pca_data.columns:
            prompt += "\nCumulative Explained Variance:\n"
            for i, var in enumerate(pca_data['Cumulative Explained Variance']):
                prompt += f"PC{i+1}: {var:.4f}\n"
        
        loading_columns = [col for col in pca_data.columns if col.startswith('Loading PC')]
        if loading_columns:
            prompt += "\nComponent Loadings (top 5 features for each PC):\n"
            num_pcs = len(set([col.split(' - ')[0] for col in loading_columns]))
            for i in range(num_pcs):
                pc_loadings = [col for col in loading_columns if col.startswith(f'Loading PC{i+1}')]
                sorted_loadings = sorted(pc_loadings, key=lambda x: abs(pca_data[x].iloc[0]), reverse=True)[:5]
                prompt += f"PC{i+1}: " + ", ".join([f"{col.split(' - ')[1]}: {pca_data[col].iloc[0]:.4f}" for col in sorted_loadings]) + "\n"
        
        transformed_columns = [col for col in pca_data.columns if col.startswith('Transformed PC')]
        if transformed_columns:
            prompt += "\nTransformed Data (first 3 rows):\n"
            for i in range(min(3, len(pca_data))):
                prompt += f"Row {i+1}: " + ", ".join([f"{col}: {pca_data[col].iloc[i]:.4f}" for col in transformed_columns]) + "\n"
        
        prompt += "\nCan you analyze these results and provide insights?"
        return prompt

    root = tk.Toplevel()
    root.title("PCA Analysis")
    root.geometry("800x600")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var = ttk.Label(main_frame, text="Select the variables:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_num_components = ttk.Label(main_frame, text="Enter the number of principal components:")
    label_num_components.pack(padx=10, pady=5)
    num_components_entry = ttk.Entry(main_frame, width=10)
    num_components_entry.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Run PCA", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Please select at least one variable.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            num_components = int(num_components_entry.get())
            if num_components < 1 or num_components > len(selected_columns):
                raise ValueError("The number of components must be between 1 and the number of selected variables.")
            pca_results = perform_pca(selected_columns, num_components)
            show_results(selected_columns, pca_results)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def perform_pca(selected_columns, num_components):
        X = dataframe[selected_columns].dropna().values
        pca = PCA(n_components=num_components)
        components = pca.fit_transform(X)
        explained_variance = pca.explained_variance_ratio_
        return {'explained_variance': explained_variance, 'components': components, 'pca': pca}

    def show_results(selected_columns, pca_results):
        num_components = len(pca_results['explained_variance'])
        
        results_df = pd.DataFrame({
            'Explained Variance': pca_results['explained_variance'],
            'Cumulative Explained Variance': np.cumsum(pca_results['explained_variance'])
        })
        
        loadings = pca_results['pca'].components_.T
        for i in range(num_components):
            for j, col in enumerate(selected_columns):
                results_df[f'Loading PC{i+1} - {col}'] = loadings[j, i]
        
        transformed_data = pca_results['components'][:5]
        for i in range(num_components):
            results_df[f'Transformed PC{i+1}'] = pd.Series(transformed_data[:, i])
        
        display_results("PCA Results", results_df, results_df.columns.tolist(), 
                        user_id, request_analysis, generate_pca_prompt)

    root.mainloop()

def apply_lda(dataframe, columns, user_id):
    def generate_lda_prompt(lda_data):
        explained_variance = lda_data['explained_variance']
        components = lda_data['components']
        class_means = lda_data['class_means']
        prompt = "The LDA analysis results are as follows:\n"
        prompt += f"Explained Variance: {explained_variance}\n"
        for i, component in enumerate(components):
            prompt += f"Component {i+1}: {component}\n"
        prompt += "Class Means:\n"
        for i, mean in enumerate(class_means):
            prompt += f"Class {i+1}: {mean}\n"
        prompt += "Can you analyze these results?"
        return prompt

    root = tk.Toplevel()
    root.title("LDA Analysis")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var = ttk.Label(main_frame, text="Select the variables:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_class = ttk.Label(main_frame, text="Select the class column:")
    label_class.pack(padx=10, pady=5)
    class_var = ttk.Combobox(main_frame, values=columns, state="readonly")
    class_var.pack(padx=10, pady=5)

    label_num_components = ttk.Label(main_frame, text="Select the number of components:")
    label_num_components.pack(padx=10, pady=5)
    num_components_var = tk.StringVar(value='None')
    num_components_entry = ttk.Entry(main_frame, textvariable=num_components_var)
    num_components_entry.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Run LDA", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Please select at least one variable.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            class_column = class_var.get()
            if not class_column:
                raise ValueError("Please select the class column.")
            num_components = num_components_var.get()
            if num_components.lower() != 'none':
                num_components = int(num_components)
            else:
                num_components = None
            lda_results = perform_lda(selected_columns, class_column, num_components)
            show_results(selected_columns, class_column, lda_results)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def perform_lda(selected_columns, class_column, num_components):
        X = dataframe[selected_columns].values
        y = dataframe[class_column].values
        lda = LDA(n_components=num_components)
        components = lda.fit_transform(X, y)
        explained_variance = lda.explained_variance_ratio_
        class_means = lda.means_
        return {'explained_variance': explained_variance, 'components': components, 'selected_columns': selected_columns, 'class_means': class_means}

    def show_results(selected_columns, class_column, lda_results):
        
        results_win = tk.Toplevel(root)
        results_win.title("LDA Results")

        results_frame = ttk.Frame(results_win, padding="3 3 12 12")
        results_frame.pack(fill=tk.BOTH, expand=True)

        tree_columns = ["Component", "Explained Variance"] + selected_columns + ["Class Mean"]
        tree_scroll = ttk.Scrollbar(results_frame, orient="vertical")
        tree_scroll.pack(side="right", fill="y")
        tree = ttk.Treeview(results_frame, columns=tree_columns, show="headings", yscrollcommand=tree_scroll.set)
        tree_scroll.config(command=tree.yview)

        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)
        tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        for i, var_exp in enumerate(lda_results['explained_variance']):
            values = [f"Component {i+1}", f"{var_exp:.2f}"] + [f"{v:.2f}" for v in lda_results['components'][:, i]] + [""]
            tree.insert("", "end", values=values)

        for i, mean in enumerate(lda_results['class_means']):
            values = ["", "", ""] * len(selected_columns) + [f"Class {i+1}"] + [f"{m:.2f}" for m in mean]
            tree.insert("", "end", values=values)

        response_text = tk.Text(results_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        lda_data = {'explained_variance': lda_results['explained_variance'], 'components': lda_results['components'], 'class_means': lda_results['class_means']}
        analyze_button = ttk.Button(results_frame, text="Analyze with ChatGPT", command=lambda: request_analysis(response_text, lda_data, generate_lda_prompt))
        analyze_button.pack(pady=10)

    root.mainloop()

def apply_bayesian_methods(dataframe, columns, user_id):
    def generate_bayesian_prompt(bayesian_data):
        accuracy = bayesian_data['accuracy'].iloc[0] if isinstance(bayesian_data['accuracy'], pd.Series) else bayesian_data['accuracy']
        precision = bayesian_data['precision'].iloc[0] if isinstance(bayesian_data['precision'], pd.Series) else bayesian_data['precision']
        recall = bayesian_data['recall'].iloc[0] if isinstance(bayesian_data['recall'], pd.Series) else bayesian_data['recall']
        f1_score = bayesian_data['f1_score'].iloc[0] if isinstance(bayesian_data['f1_score'], pd.Series) else bayesian_data['f1_score']

        prompt = (
            "The Bayesian method results are as follows:\n"
            f"Classification Accuracy: {accuracy:.2f}\n"
            f"Precision: {precision:.2f}\n"
            f"Recall: {recall:.2f}\n"
            f"F1 Score: {f1_score:.2f}\n"
            "Can you analyze these results?"
        )
        return prompt

    root = tk.Toplevel()
    root.title("Bayesian Methods Analysis")
    root.geometry("800x600")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var = ttk.Label(main_frame, text="Select the variables:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_class = ttk.Label(main_frame, text="Select the class column:")
    label_class.pack(padx=10, pady=5)
    class_var = ttk.Combobox(main_frame, values=columns, state="readonly")
    class_var.pack(padx=10, pady=5)

    button_run = ttk.Button(main_frame, text="Run Bayesian Method", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            class_column = class_var.get()
            if not selected_indices or not class_column:
                raise ValueError("Please select at least one variable and a class column.")
            bayesian_results = perform_bayesian_methods(selected_columns, class_column)
            show_results(bayesian_results)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def perform_bayesian_methods(selected_columns, class_column):
        X = dataframe[selected_columns].values
        y = dataframe[class_column].values
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        model = GaussianNB()
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        results = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted', zero_division=1),
            'recall': recall_score(y_test, y_pred, average='weighted', zero_division=1),
            'f1_score': f1_score(y_test, y_pred, average='weighted', zero_division=1)
        }
        return results

    def show_results(bayesian_results):
        results_df = pd.DataFrame([bayesian_results])
        display_results("Bayesian Methods Results", results_df, results_df.columns.tolist(), user_id, request_analysis, generate_bayesian_prompt)

    root.mainloop()

def apply_frequency_distribution(dataframe, columns):
    root = tk.Toplevel()
    root.title("Frequency Distribution")
    root.geometry("250x350")

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

    label_var = ttk.Label(main_frame, text="Select columns for frequency distribution:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    display_option = tk.StringVar(value="table")
    radio_table = ttk.Radiobutton(main_frame, text="Tabular Display", variable=display_option, value="table")
    radio_table.pack(anchor=tk.W, padx=10, pady=2)
    radio_chart = ttk.Radiobutton(main_frame, text="Graphical Display", variable=display_option, value="chart")
    radio_chart.pack(anchor=tk.W, padx=10, pady=2)

    button_run = ttk.Button(main_frame, text="Calculate Frequency Distribution", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Please select at least one column.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            frequency_results = perform_frequency_distribution(selected_columns)
            show_results(selected_columns, frequency_results, display_option.get())
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def perform_frequency_distribution(selected_columns):
        frequency_results = {}
        for col in selected_columns:
            frequency_results[col] = dataframe[col].value_counts()
        return frequency_results

    def show_results(selected_columns, frequency_results, display_type):
        window = tk.Toplevel(root)
        window.geometry("800x600")
        window.title("Frequency Distribution Results")
        if display_type == "table":
            show_results_table(window, selected_columns, frequency_results)
        else:
            show_results_chart(window, selected_columns, frequency_results)

    def show_results_table(window, selected_columns, frequency_results):
        for col in selected_columns:
            frame = ttk.Frame(window)
            frame.pack(fill=tk.BOTH, expand=True)

            label = ttk.Label(frame, text=f"Frequency Distribution for {col}:")
            label.pack()

            tree = ttk.Treeview(frame, columns=("Value", "Frequency"), show="headings")
            tree.heading("Value", text="Value")
            tree.heading("Frequency", text="Frequency")
            tree.pack(padx=10, pady=10, expand=True)

            for value, count in frequency_results[col].items():
                tree.insert("", "end", values=(value, count))

    def show_results_chart(window, selected_columns, frequency_results):
        canvas_frame = ttk.Frame(window)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        chart_canvas = tk.Canvas(canvas_frame)
        chart_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=chart_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        scrollable_frame = ttk.Frame(chart_canvas)
        chart_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: chart_canvas.configure(
                scrollregion=chart_canvas.bbox("all")
            )
        )
        chart_canvas.configure(yscrollcommand=scrollbar.set)
        
        for col in selected_columns:
            fig, ax = plt.subplots(figsize=(10, 5))
            frequency_results[col].plot(kind='bar', ax=ax)
            ax.set_title(f"Frequency Distribution for {col}")
            ax.set_xlabel("Value")
            ax.set_ylabel("Frequency")
            plt.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
            canvas.draw()
            
            plt.close(fig)
            
    root.mainloop()

def apply_contingency_table(dataframe, columns, user_id):
    root = tk.Toplevel()
    root.title("Column Selection for Analysis")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var1 = ttk.Label(main_frame, text="Select the first column:")
    label_var1.pack(padx=10, pady=5)
    listbox_var1 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=5)
    for col in columns:
        listbox_var1.insert(tk.END, col)
    listbox_var1.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_var2 = ttk.Label(main_frame, text="Select the second column:")
    label_var2.pack(padx=10, pady=5)
    listbox_var2 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=5)
    for col in columns:
        listbox_var2.insert(tk.END, col)
    listbox_var2.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    button_show = ttk.Button(main_frame, text="Show Contingency Table", command=lambda: show_contingency())
    button_show.pack(pady=10)

    response_text = tk.Text(main_frame, height=10)
    response_text.pack(pady=10, fill=tk.BOTH, expand=True)

    button_analysis = ttk.Button(main_frame, text="Request GPT Analysis", command=lambda: request_gpt_analysis())
    button_analysis.pack(pady=10)

    def show_contingency():
        try:
            col1 = listbox_var1.get(listbox_var1.curselection())
            col2 = listbox_var2.get(listbox_var2.curselection())
            if col1 == col2:
                raise ValueError("Please select different columns.")
            contingency_table = pd.crosstab(dataframe[col1], dataframe[col2])
            create_new_window(contingency_table, f"Contingency Table: {col1} vs {col2}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def request_gpt_analysis():
        try:
            col1 = listbox_var1.get(listbox_var1.curselection())
            col2 = listbox_var2.get(listbox_var2.curselection())
            contingency_table = pd.crosstab(dataframe[col1], dataframe[col2])
            generate_message = lambda x: f"Please analyze this data:\n{x}"
            request_analysis(response_text, contingency_table, generate_message)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_new_window(data, title):
        new_window = tk.Toplevel(root)
        new_window.title(title)
        display_table(data, new_window)

    def display_table(data, window):
        frame = ttk.Frame(window)
        frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

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

def apply_chi_square_test(dataframe, columns):
    root = tk.Toplevel()
    root.title("Chi-Square Test")
    root.geometry("300x480")

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

    label_var1 = ttk.Label(main_frame, text="Select the first column for the Chi-square test:")
    label_var1.pack(padx=10, pady=5)
    listbox_var1 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=10)
    for col in columns:
        listbox_var1.insert(tk.END, col)
    listbox_var1.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    label_var2 = ttk.Label(main_frame, text="Select the second column for the Chi-square test:")
    label_var2.pack(padx=10, pady=5)
    listbox_var2 = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=10)
    for col in columns:
        listbox_var2.insert(tk.END, col)
    listbox_var2.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    button_run = ttk.Button(main_frame, text="Calculate Chi-Square Test", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_col1 = listbox_var1.get(listbox_var1.curselection())
            selected_col2 = listbox_var2.get(listbox_var2.curselection())
            if not selected_col1 or not selected_col2:
                raise ValueError("Please select one column from each list.")
            if selected_col1 == selected_col2:
                raise ValueError("Please select different columns.")
            chi_square_results = perform_chi_square_test([selected_col1, selected_col2])
            show_results([selected_col1, selected_col2], chi_square_results)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def perform_chi_square_test(selected_columns):
        col1, col2 = selected_columns
        contingency_table = pd.crosstab(dataframe[col1], dataframe[col2])
        chi2, p, dof, expected = chi2_contingency(contingency_table)
        return {'chi2': chi2, 'p_value': p, 'dof': dof, 'expected': expected, 'contingency_table': contingency_table}

    def generate_chi_square_prompt(results):
        prompt = (
            f"Results of the Chi-square test are as follows:\n"
            f"Chi-squared: {results['chi2']:.4f}\n"
            f"P-value: {results['p_value']:.4f}\n"
            f"Degrees of Freedom: {results['dof']}\n\n"
            f"Observed Contingency Table:\n{results['contingency_table']}\n\n"
            f"Expected Contingency Table:\n"
            f"{pd.DataFrame(results['expected'], index=results['contingency_table'].index, columns=results['contingency_table'].columns)}"
            "\nCan you analyze these results?"
        )
        return prompt

    def show_results(selected_columns, chi_square_results):
        result_window = tk.Toplevel(root)
        result_window.geometry("800x800")
        result_window.title(f"Chi-Square Test Results for {selected_columns[0]} and {selected_columns[1]}")

        result_canvas = tk.Canvas(result_window)
        result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        result_scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=result_canvas.yview)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        result_frame = ttk.Frame(result_canvas)
        result_frame.bind(
            "<Configure>",
            lambda e: result_canvas.configure(
                scrollregion=result_canvas.bbox("all")
            )
        )

        result_canvas.create_window((0, 0), window=result_frame, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)

        chi2_label = ttk.Label(result_frame, text=f"Chi-squared: {chi_square_results['chi2']:.4f}")
        chi2_label.pack(pady=5)
        p_value_label = ttk.Label(result_frame, text=f"P-value: {chi_square_results['p_value']:.4f}")
        p_value_label.pack(pady=5)
        dof_label = ttk.Label(result_frame, text=f"Degrees of Freedom: {chi_square_results['dof']}")
        dof_label.pack(pady=5)

        create_treeview(result_frame, chi_square_results['contingency_table'], "Observed Contingency Table")
        expected_df = pd.DataFrame(chi_square_results['expected'], index=chi_square_results['contingency_table'].index, columns=chi_square_results['contingency_table'].columns)
        create_treeview(result_frame, expected_df, "Expected Contingency Table")

        response_text = tk.Text(result_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        analyze_button = ttk.Button(result_frame, text="Analyze with ChatGPT", command=lambda: request_analysis(response_text, chi_square_results, generate_chi_square_prompt))
        analyze_button.pack(pady=10)


    def create_treeview(parent, data, title):
        frame_label = ttk.Label(parent, text=title)
        frame_label.pack()

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

def apply_association_analysis(dataframe, columns):
    def perform_association_analysis(selected_columns, min_support, min_confidence):
        df_selected = dataframe[selected_columns].applymap(lambda x: bool(x))
        frequent_itemsets = apriori(df_selected, min_support=min_support, use_colnames=True)
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=min_confidence)
        rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x))
        rules['consequents'] = rules['consequents'].apply(lambda x: list(x))
        return rules

    def generate_association_message(rules):
        prompt = "Here are the association rules, please analyze:\n\n"
        for _, row in rules.iterrows():
            prompt += f"Antecedents: {', '.join(list(row['antecedents']))}\n"
            prompt += f"Consequents: {', '.join(list(row['consequents']))}\n"
            prompt += f"Support: {row['support']}\n"
            prompt += f"Confidence: {row['confidence']}\n"
            prompt += f"Lift: {row['lift']}\n\n"
        return prompt

    root = tk.Toplevel()
    root.geometry("400x600")
    root.title("Association Analysis")

    main_frame = ttk.Frame(root, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_var = ttk.Label(main_frame, text="Select columns for association analysis:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    min_support_label = ttk.Label(main_frame, text="Enter minimum support value (e.g., 0.5):")
    min_support_label.pack(padx=10, pady=5)
    min_support_entry = ttk.Entry(main_frame)
    min_support_entry.pack(padx=10, pady=5, fill=tk.X)

    min_confidence_label = ttk.Label(main_frame, text="Enter minimum confidence value (e.g., 0.5):")
    min_confidence_label.pack(padx=10, pady=5)
    min_confidence_entry = ttk.Entry(main_frame)
    min_confidence_entry.pack(padx=10, pady=5, fill=tk.X)

    button_run = ttk.Button(main_frame, text="Calculate Association Rules", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Please select at least one column.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            min_support = float(min_support_entry.get())
            min_confidence = float(min_confidence_entry.get())
            association_results = perform_association_analysis(selected_columns, min_support, min_confidence)
            show_results(association_results)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_results(rules):
        result_window = tk.Toplevel(root)
        result_window.geometry("800x600")
        result_window.title("Association Rules Results")

        result_canvas = tk.Canvas(result_window)
        result_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        result_scrollbar = ttk.Scrollbar(result_window, orient="vertical", command=result_canvas.yview)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        result_frame = ttk.Frame(result_canvas)
        result_frame.bind(
            "<Configure>",
            lambda e: result_canvas.configure(
                scrollregion=result_canvas.bbox("all")
            )
        )

        result_canvas.create_window((0, 0), window=result_frame, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)

        label = ttk.Label(result_frame, text="Association Rules:")
        label.pack()

        tree_columns = ["antecedents", "consequents", "support", "confidence", "lift"]
        tree = ttk.Treeview(result_frame, columns=tree_columns, show="headings")
        for col in tree_columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)
        tree.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        for _, row in rules.iterrows():
            values = [', '.join(list(row['antecedents'])), ', '.join(list(row['consequents'])), row['support'], row['confidence'], row['lift']]
            tree.insert("", "end", values=values)

        response_text = tk.Text(result_frame, height=10)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        analyze_button = ttk.Button(result_frame, text="Analyze with ChatGPT", command=lambda: request_analysis(response_text, rules, generate_association_message))
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
    root.geometry("800x800")
    root.title("Sentiment Analysis")

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

    label_var = ttk.Label(scrollable_frame, text="Select columns for sentiment analysis:")
    label_var.pack(padx=10, pady=5)
    listbox_vars = tk.Listbox(scrollable_frame, selectmode='multiple', exportselection=0, height=10)
    for col in columns:
        listbox_vars.insert(tk.END, col)
    listbox_vars.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    button_run = ttk.Button(scrollable_frame, text="Analyze Sentiments", command=lambda: on_run())
    button_run.pack(pady=20)

    def on_run():
        try:
            selected_indices = listbox_vars.curselection()
            if not selected_indices:
                raise ValueError("Please select at least one column.")
            selected_columns = [listbox_vars.get(i) for i in selected_indices]
            sentiment_results = perform_sentiment_analysis(selected_columns)
            show_results(sentiment_results)
        except ValueError as e:
            messagebox.showerror("Error", str(e))

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

        label = ttk.Label(scrollable_frame, text="Sentiment Analysis Results:")
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

        analyze_button = ttk.Button(scrollable_frame, text="Analyze with ChatGPT", command=lambda: request_analysis(response_text, sentiment_results, generate_sentiment_message))
        analyze_button.pack(pady=10)

    root.mainloop()
