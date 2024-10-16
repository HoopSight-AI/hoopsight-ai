import os
import pandas as pd

# Define the input directory where your CSV files are located
print("RUNNING")
input_dir = 'alexadams/Desktop/oct-15-no-process'

# Define the output directory where you want to store the reorganized data
output_dir = '/kaggle/working/MetricType'  # Change this to your desired output path

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Iterate over each metric type directory in the input directory
for metric_type in os.listdir(input_dir):
    metric_path = os.path.join(input_dir, metric_type)
    if os.path.isdir(metric_path):
        # Create a directory for the metric type in the output directory
        metric_output_dir = os.path.join(output_dir, metric_type)
        os.makedirs(metric_output_dir, exist_ok=True)

        # Process each CSV file in the metric type directory
        for filename in os.listdir(metric_path):
            if filename.endswith('.csv'):
                # Read the CSV file into a DataFrame
                csv_path = os.path.join(metric_path, filename)
                df = pd.read_csv(csv_path)

                # Process each row in the DataFrame
                for _, row in df.iterrows():
                    team = row['Team']
                    
                    # Define the file path for the team's consolidated CSV file
                    team_csv_path = os.path.join(metric_output_dir, f'{team}.csv')

                    # Convert the current row into a DataFrame to append it
                    team_data = pd.DataFrame([row])
                    
                    # Append the current row to the team's CSV file, avoiding loading the entire dataset into memory
                    team_data.to_csv(team_csv_path, mode='a', header=not os.path.exists(team_csv_path), index=False)

                    print(f"Appended data to {team_csv_path}")
                    
print("DONE")
