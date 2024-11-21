import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from geo_score import score_address  # score_address fonksiyonunu import etme


def process_addresses(df):
    not_found_addresses = []
    df["score"] = None

    def process_row(row):
        address = row["full_address"]
        score = score_address(address)
        if score is not None:
            return score
        else:
            not_found_addresses.append(address)
            return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        scores = list(executor.map(process_row, [row for _, row in df.iterrows()]))

    df["score"] = scores
    return df, not_found_addresses

def save_results(df, not_found_addresses, output_found_path, output_not_found_path, batch_num):
    df_with_scores = df.dropna(subset=["score"])
    df_with_scores.to_csv(f"{output_found_path}_batch_{batch_num}.csv", index=False, encoding="windows-1252")

    not_found_df = pd.DataFrame(not_found_addresses, columns=["Not Found Addresses"])
    not_found_df.to_csv(f"{output_not_found_path}_batch_{batch_num}.csv", index=False, encoding="windows-1252")

# Paths
input_csv_path = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_input\input_dataset\cleansed_ready_for model.csv"
output_found_path = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_output"
output_not_found_path = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_output"

# Load data and create 'full_address' column
df = pd.read_csv(input_csv_path, delimiter=";", encoding="windows-1252")
df["full_address"] = df.iloc[:, 0] + ", " + df.iloc[:, 1]

# Process in batches of 1000
batch_size = 1000
num_batches = (len(df) + batch_size - 1) // batch_size  # Calculate total number of batches

for batch_num in range(num_batches):
    start_idx = batch_num * batch_size
    end_idx = min(start_idx + batch_size, len(df))
    df_batch = df.iloc[start_idx:end_idx]

    # Process addresses and save results for the batch
    df_with_scores, not_found_addresses = process_addresses(df_batch)
    save_results(df_with_scores, not_found_addresses, output_found_path, output_not_found_path, batch_num + 1)

print("Processing and saving completed.")
