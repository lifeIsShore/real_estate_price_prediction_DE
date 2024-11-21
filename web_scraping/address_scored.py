import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from geo_score import score_address  # Import the score_address function
from far_from_center_score import calculate_distance_address_to_city_center  # Import the distance from city center function
from airport_dist_score import calculate_airport_distance_log  # Import the airport proximity scoring function
import json
import os

# Load configuration from config.json
def load_config(config_path=r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\config.json"):
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    else:
        return {}  # Return an empty dictionary if the config file does not exist

# Function to process addresses and calculate scores
def process_addresses(df):
    # Initialize columns for all scores
    df["score"] = None
    df["distance_from_center"] = None
    df["airport_proximity_score"] = None

    # Function to process a single row
    def process_row(row):
        address = row["full_address"]
        try:
            # Calculate scores
            score = score_address(address)
            distance_from_center = calculate_distance_address_to_city_center(address)
            airport_score = calculate_airport_distance_log(address)
        except Exception as e:
            print(f"Error processing address '{address}': {e}")
            score, distance_from_center, airport_score = None, None, None
        return score, distance_from_center, airport_score

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_row, [row for _, row in df.iterrows()]))

    # Add results to DataFrame columns
    df["score"] = [result[0] for result in results]
    df["distance_from_center"] = [result[1] for result in results]
    df["airport_proximity_score"] = [result[2] for result in results]
    return df

# Save the results to a CSV file
def save_results(df, output_found_path, batch_num):
    # Save rows with valid scores only
    df_with_scores = df.dropna(subset=["score", "distance_from_center", "airport_proximity_score"])
    output_file = f"{output_found_path}_batch_{batch_num}.csv"
    df_with_scores.to_csv(output_file, index=False, encoding="windows-1252")

# Load configuration values (paths)
config = load_config()

# Assign paths from the config file
input_csv_path = r"C:/Users/ahmty/Desktop/Python/real_estate_price_prediction_DE/real_estate_price_prediction_DE/csv_input/input_dataset/cleansed_ready_for model.csv"  # Use default if not found
output_found_path = r"C:/Users/ahmty/Desktop/Python/real_estate_price_prediction_DE/real_estate_price_prediction_DE/csv_input/input_dataset/cleansed_ready_for model2.csv"  # Use default if not found

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
