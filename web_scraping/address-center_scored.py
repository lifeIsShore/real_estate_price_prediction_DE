import pandas as pd
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from far_from_center_score import calculate_distance_address_to_city_center  # Modülden fonksiyonu dahil ediyoruz

# Giriş ve çıkış dosyaları
INPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\csv_input\input_dataset\ad_id-address1.csv"
OUTPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_output\modified_ad_id-address.csv"

# Ayarlanabilir parametreler
BATCH_SIZE = 1000
MAX_THREADS = 5
START_BATCH = 0
MAX_RETRIES = 3
RETRY_DELAY = 2

def calculate_distance_with_retry(address, retries=MAX_RETRIES, delay=RETRY_DELAY):
    """
    Adresin şehir merkezine olan mesafesini hesaplar. Hata durumunda yeniden dener.
    """
    attempt = 0
    while attempt < retries:
        try:
            return calculate_distance_address_to_city_center(address)
        except Exception as e:
            attempt += 1
            print(f"Hata adres: {address}, Hata mesajı: {e}. Deneme {attempt}/{retries}.")
            if attempt < retries:
                time.sleep(delay)
            else:
                print(f"Tüm denemeler başarısız oldu, adres {address} için None döndürülecek.")
                return None
    return None

def process_batch(batch_df):
    """
    Bir batch verisi üzerinde adreslere mesafe hesaplaması yapar.
    """
    batch_df['Distance_To_City_Center'] = batch_df['Full_Address'].apply(calculate_distance_with_retry)
    return batch_df

def main():
    # Veri setini yükle
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8-sig')

    # Çıkış dosyasına başlık yaz (eğer yoksa)
    if START_BATCH == 0:
        df.head(0).to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8-sig')

    # Toplam batch sayısını hesapla
    total_batches = math.ceil(len(df) / BATCH_SIZE)

    # İşlem yapılacak batch'leri belirle
    for batch_start in range(START_BATCH, total_batches, MAX_THREADS):
        batch_end = min(batch_start + MAX_THREADS, total_batches)
        futures = []
        
        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            for batch_num in range(batch_start, batch_end):
                start_idx = batch_num * BATCH_SIZE
                end_idx = min((batch_num + 1) * BATCH_SIZE, len(df))
                batch_df = df.iloc[start_idx:end_idx].copy()
                futures.append(executor.submit(process_batch, batch_df))

            # İşlemleri tamamlanınca sırayla işleyip dosyaya yaz
            for future in as_completed(futures):
                result_df = future.result()
                result_df.to_csv(OUTPUT_FILE, sep=';', mode='a', index=False, encoding='utf-8-sig', header=False)
        
        print(f"{batch_start} - {batch_end - 1} batch'leri tamamlandı!")

    print("Tüm batch'ler başarıyla işlendi!")

if __name__ == "__main__":
    main()
