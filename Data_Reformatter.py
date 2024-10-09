import os
import pandas as pd

# Define the input directory where your CSV files are located
input_dir = '/kaggle/input/nba-championship-winning-metrics-2004-2024'

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
        
        team_data = {}  # Dictionary to hold data for each team
        
        # Process each CSV file in the metric type directory
        for filename in os.listdir(metric_path):
            if filename.endswith('.csv'):
                # Extract the year from the filename
                year = filename.split('_')[-1].split('.')[0]
                csv_path = os.path.join(metric_path, filename)
                
                # Read the CSV file into a DataFrame
                df = pd.read_csv(csv_path)
                df['Year'] = int(year)  # Add the year column
                
                # Process each row in the DataFrame
                for _, row in df.iterrows():
                    team = row['Team']
                    
                    # Initialize the team's DataFrame if not already done
                    if team not in team_data:
                        team_data[team] = pd.DataFrame()
                    
                    # Append the row to the team's DataFrame
                    team_data[team] = pd.concat([team_data[team], pd.DataFrame([row])], ignore_index=True)
        
        # After processing all files, save each team's data into a single CSV file
        for team, data in team_data.items():
            # Save the team's CSV file directly in the metric type directory
            # Sanitize team names to avoid issues with file naming
            sanitized_team = team.replace('/', '_').replace('\\', '_')
            team_csv_path = os.path.join(metric_output_dir, f'{sanitized_team}.csv')
            data.to_csv(team_csv_path, index=False)
