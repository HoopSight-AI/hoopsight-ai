import os
import pandas as pd
import numpy as np

input_dir = '/Users/adarsh/Desktop/vscode-workspace/nba-prediction-model/nba-java-predictions/October_15_Data'
output_dir = '/Users/adarsh/Desktop/vscode-workspace/nba-prediction-model/nba-java-predictions/Cleaned_Data'
os.makedirs(output_dir, exist_ok=True)
column = 'Statistic'

for metric_type in os.listdir(input_dir):
    metric_path = os.path.join(input_dir, metric_type)
    if os.path.isdir(metric_path):
        # Create a directory for the metric type in the output directory
        metric_output_dir = os.path.join(output_dir, metric_type)
        os.makedirs(metric_output_dir, exist_ok=True)

        # Process each CSV file in the metric type directory
        for filename in os.listdir(metric_path):
            if filename.endswith('.csv'):
                csv_path = os.path.join(metric_path, filename)
                # Read the CSV file into a DataFrame
                df = pd.read_csv(csv_path)
                if column in df.columns:
                    # calculate important values for determining outliers
                    mean = df[column].mean()
                    std_dev = df[column].std()
                    median = df[column].median()
                    threshold = 3
                    z_scores = (df[column] - mean) / std_dev

                    # for each entry in the column, check if it is an outlier (defined as having a z-score > 3)
                    outlier_mask = abs(z_scores) > 3

                    outliers = df.loc[outlier_mask, column]
                    if not outliers.empty:
                        print(f"Outliers in {filename}:")
                        print(outliers)
                    else:
                        print(f"No outliers found in {filename}.")
                    # df.loc[outlier_mask, column] = median
                    df[column] = df[column].round(3)

                    #output_file_path = os.path.join(metric_output_dir, filename)
                    #df.to_csv(output_file_path, index=False)
print("DONE")
                        
                    

                   