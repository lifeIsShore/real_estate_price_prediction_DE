import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from geo_score import score_address  # Import the score_address function
from far_from_center_score import calculate_distance_address_to_city_center  # Import the calculate_distance_address_to_city_center function
import json
import os

# Load configuration from config.json
def load_config(config_path="config.json"):
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    else:
        return {}  # Return an empty dictionary if the config file does not exist

# Function to process addresses and calculate scores and distance
def process_addresses(df):
    df["score"] = None
    df["distance_from_center"] = None  # Adding a new column for distance from the center

    def process_row(row):
        address = row["full_address"]
        score = score_address(address)
        distance = calculate_distance_address_to_city_center(address)  # Calculate the distance from the city center
        return score, distance  # Return both the score and distance

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_row, [row for _, row in df.iterrows()]))

    # Add the results to separate columns
    df["score"] = [result[0] for result in results]
    df["distance_from_center"] = [result[1] for result in results]
    return df

# Save the results to a CSV file
def save_results(df, output_found_path, batch_num):
    df_with_scores = df.dropna(subset=["score"])  # Save only rows with valid scores
    df_with_scores.to_csv(f"{output_found_path}_batch_{batch_num}.csv", index=False, encoding="windows-1252")

# Load configuration values (paths)
config = load_config()

# Assign paths from the config file
input_csv_path = config.get("input_csv_path", r"C:\default\input.csv")  # Use default if not found
output_found_path = config.get("output_found_path", r"C:\default\output")  # Use default if not found

# Load data and create 'full_address' column
df = pd.read_csv(input_csv_path, delimiter=";", encoding="windows-1252")
df["full_address"] = df.iloc[:, 0] + ", " + df.iloc[:, 1]

# Process in batches of 1000
batch_size = 1000
num_batches = (len(df) + batch_size - 1) // batch_size  # Calculate the total number of batches

for batch_num in range(num_batches):
    start_idx = batch_num * batch_size
    end_idx = min(start_idx + batch_size, len(df))
    df_batch = df.iloc[start_idx:end_idx]

    # Process addresses and save results for the batch
    df_with_scores = process_addresses(df_batch)
    save_results(df_with_scores, output_found_path, batch_num + 1)

print("Processing and saving completed.")
