import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from geo_score import score_address  # score_address fonksiyonunu import etme

def process_addresses(df):
    df["score"] = None

    def process_row(row):
        address = row["full_address"]
        score = score_address(address)
        return score  # Bulunamayan adresler artık bir yere kaydedilmeyecek

    with ThreadPoolExecutor(max_workers=10) as executor:
        scores = list(executor.map(process_row, [row for _, row in df.iterrows()]))

    df["score"] = scores
    return df

def save_results(df, output_found_path, batch_num):
    df_with_scores = df.dropna(subset=["score"])  # Sadece bulunan adresleri kaydet
    df_with_scores.to_csv(f"{output_found_path}_batch_{batch_num}.csv", index=False, encoding="windows-1252")

# Paths
input_csv_path = r"C:\Users\ahmty\Desktop\Python\geo_DSproject_github_clone\git_py\csv_output\combined\will be used\cleansed_ready_for model_v2(no null).csv"
output_found_path = r"C:\Users\ahmty\Desktop\Python\geo_DSproject_github_clone\git_py\csv_output\combined\found_addresses_with_scores"

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
    df_with_scores = process_addresses(df_batch)
    save_results(df_with_scores, output_found_path, batch_num + 1)

print("Processing and saving completed.")
