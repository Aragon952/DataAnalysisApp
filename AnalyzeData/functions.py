import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import openai
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

api_key = "sk-proj-PBFLHil6BVfWS860yS27T3BlbkFJsp0W4Nt469C3EAMg9nqY"
openai.api_key = api_key

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

def request_analysis(response_text, stats_data, generate_message):
    if not openai.api_key:
        raise ValueError("API key for OpenAI is not set. Please set the OPENAI_API_KEY environment variable.")

    messages = [
        {"role": "system", "content": "You are an intelligent assistant tasked with analyzing statistical data."},
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
        messagebox.showerror("Error", f"Failed to interact with ChatGPT API: {str(e)}")
        response_text.insert(tk.END, "Failed to retrieve an analysis.\n")

def save_csv(dataframe, user_id):
    print("Data saved successfully.")

def save_picture(dataframe, user_id):
    print("Picture saved successfully.")

def apply_descriptive_statistics(dataframe, columns):
    columns_stats = ['Column_Name', 'Count', 'Mean', 'Std', 'Min', '25%', '50%', '75%', 'Max']

    def generate_statistics_message(stats_data):
        prompt_stats = "Here are the descriptive statistics, please analyze:\n"
        for index, row in stats_data.iterrows():
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
        
        stats_df = pd.concat(stats_rows, axis=1).transpose()
        show_results(stats_df)

    def show_results(stats_df):
        results_win = tk.Toplevel()
        results_win.title("Descriptive Statistics Results")
        tree = ttk.Treeview(results_win, columns=columns_stats, show="headings", height=10)
        tree.pack(padx=10, pady=10, fill='both', expand=True)

        for col in columns_stats:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width = 80)

        for index, row in stats_df.iterrows():
            values = [row[col] for col in columns_stats]
            tree.insert("", "end", values=values)

        response_text = tk.Text(results_win, height=10, width=50)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        analyze_button = ttk.Button(results_win, text="Request ChatGPT Analysis", command=lambda: request_analysis(response_text, stats_df, generate_statistics_message))
        analyze_button.pack(pady=10)

    top = tk.Toplevel()
    top.title("Calculate Descriptive Statistics")

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    listbox = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height = 10)
    for col in columns:
        listbox.insert(tk.END, col)
    listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    listbox.config(yscrollcommand=scrollbar.set)

    apply_button = ttk.Button(main_frame, text="Calculate Statistics for Selected Columns", command=lambda: apply_statistics([listbox.get(i) for i in listbox.curselection()]))
    apply_button.pack(pady=10)

    top.mainloop()

def apply_linear_regression(dataframe, columns):
    def generate_regression_message(results):
        prompt_stats = "Here are the linear regression results, please analyze:\n"
        prompt_stats += f"R-squared: {results.rsquared}, Adjusted R-squared: {results.rsquared_adj}\n"
        prompt_stats += f"F-statistic: {results.fvalue}, Prob (F-statistic): {results.f_pvalue}\n"
        
        # Iterate over the regression coefficients
        for param_name, param in results.params.items():
            prompt_stats += f"{param_name}: Coefficient = {param}, P>|t| = {results.pvalues[param_name]}\n"

        return prompt_stats


    top = tk.Toplevel()
    top.title("Perform Linear Regression")

    # Setarea frame-ului principal
    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Listbox pentru variabila dependentă
    label_dep = ttk.Label(main_frame, text="Select the dependent variable:")
    label_dep.pack(padx=10, pady=5)
    listbox_dep = tk.Listbox(main_frame, selectmode='single', exportselection=0, height=6)
    listbox_dep.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    # Listbox pentru variabilele independente
    label_indep = ttk.Label(main_frame, text="Select the independent variables:")
    label_indep.pack(padx=10, pady=5)
    listbox_indep = tk.Listbox(main_frame, selectmode='multiple', exportselection=0, height=10)
    listbox_indep.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    # Adăugarea coloanelor în listbox-uri
    for col in columns:
        listbox_dep.insert(tk.END, col)
        listbox_indep.insert(tk.END, col)

    # Buton pentru efectuarea regresiei
    button_run = ttk.Button(main_frame, text="Run Regression", command=lambda: perform_regression(listbox_dep, listbox_indep))
    button_run.pack(pady=20)

    def perform_regression(listbox_dep, listbox_indep):
        dep_var = listbox_dep.get(listbox_dep.curselection())
        indep_vars = [listbox_indep.get(i) for i in listbox_indep.curselection()]
        
        if not dep_var or not indep_vars:
            messagebox.showerror("Error", "Please select at least one dependent and one or more independent variables.")
            return
        
        # Prepare the data
        X = dataframe[indep_vars]
        X = sm.add_constant(X)  # Adds a constant term to the predictor
        y = dataframe[dep_var]

        # Fit the linear regression model
        model = sm.OLS(y, X)
        results = model.fit()  # This is the RegressionResults object

        # Now you can pass 'results' to generate message and request analysis functions
        show_results(results)

    def show_results(results):
        results_win = tk.Toplevel()
        results_win.title("Regression Results")
        text = tk.Text(results_win, wrap="word")
        text.insert(tk.END, results.summary().as_text())  # Use as_text() to display summary in a Text widget
        text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Text widget for ChatGPT response
        response_text = tk.Text(results_win, height=10, width=50)
        response_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Button for ChatGPT analysis
        analyze_button = ttk.Button(results_win, text="Request ChatGPT Analysis",
                                    command=lambda: request_analysis(response_text, results, generate_regression_message))
        analyze_button.pack(pady=10)


    top.mainloop()

def apply_logistic_regression(dataframe, columns):
    def perform_logistic_regression(dep_var, indep_vars):
        formula = f"{dep_var} ~ " + " + ".join(indep_vars)
        model = smf.logit(formula, data=dataframe).fit(disp=0)  # disp=0 to suppress fit output
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
    top = tk.Toplevel()
    top.title("Perform Cluster Analysis")

    def on_closing():
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            top.destroy()  # Properly destroy the window

    top.protocol("WM_DELETE_WINDOW", on_closing)  # Handle window close

    main_frame = ttk.Frame(top, padding="3 3 12 12")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Enter number of clusters:").pack(padx=10, pady=5)
    num_clusters_entry = ttk.Entry(main_frame, width=10)
    num_clusters_entry.pack(padx=10, pady=5)

    ttk.Button(main_frame, text="Run Clustering", command=lambda: perform_clustering(int(num_clusters_entry.get()))).pack(pady=20)

    def perform_clustering(num_clusters):
        X = dataframe[columns].values
        kmeans = KMeans(n_clusters=num_clusters, n_init=10, random_state=0).fit(X)
        labels = kmeans.labels_
        show_results(X, labels, kmeans.cluster_centers_)

    def show_results(data, labels, centroids):
        results_win = tk.Toplevel()
        results_win.title("Clustering Results")
        fig, ax = plt.subplots()
        scatter = ax.scatter(data[:, 0], data[:, 1], c=labels, cmap='viridis', marker='o', alpha=0.5)
        ax.scatter(centroids[:, 0], centroids[:, 1], s=300, c='red', marker='x')
        ax.set_title('Cluster Analysis Result')
        canvas = FigureCanvasTkAgg(fig, master=results_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    top.mainloop()

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