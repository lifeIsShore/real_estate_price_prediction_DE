import pandas as pd
from geo_score import score_address
import threading
from queue import Queue

# Giriş ve çıkış dosyaları
INPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_input\input_dataset\ad_id-address.csv"
OUTPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_input\input_dataset\modified_ad_id-address.csv"

BATCH_SIZE = 1000  # Her bir batch işlemi için verileri bölelim

def process_batch(batch_df, result_queue):
    """
    Bir batch verisi üzerinde adreslere Geo_Score hesaplaması yapar.
    """
    def safe_score(address):
        try:
            return score_address(address)
        except Exception as e:
            print(f"Hata adres: {address}, Hata mesajı: {e}")
            return None  # Hata oluşursa None döner

    # Full_Address sütunu oluştur
    batch_df['Full_Address'] = batch_df['Street'] + ", " + batch_df['City_Code']
    
    # Geo_Score hesaplama
    batch_df['Geo_Score'] = batch_df['Full_Address'].apply(safe_score)
    
    # Sonuçları kuyruğa ekle
    result_queue.put(batch_df)

def save_batches_to_file(queue, output_file):
    """
    Kuyruktan gelen işlem sonuçlarını belirtilen dosyaya yazdırır.
    """
    while True:
        batch = queue.get()
        if batch is None:  # Kuyruk boş ve işlem bitmişse çıkış yap
            break
        batch.to_csv(output_file, sep=';', mode='a', index=False, encoding='utf-8-sig', header=False)

def main():
    # Veri setini yükle
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8-sig')  # Kodlama

    # Çıkış dosyasına başlık yaz
    df.head(0).to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8-sig')  # İlk satırı başlık olarak yaz

    # İşlem sonuçlarını saklamak için bir kuyruk oluştur
    result_queue = Queue()

    # Sonuçları yazacak thread
    writer_thread = threading.Thread(target=save_batches_to_file, args=(result_queue, OUTPUT_FILE))
    writer_thread.start()

    # Batch'leri işleyin
    threads = []
    for start in range(0, len(df), BATCH_SIZE):
        end = start + BATCH_SIZE
        batch_df = df.iloc[start:end].copy()
        thread = threading.Thread(target=process_batch, args=(batch_df, result_queue))
        threads.append(thread)
        thread.start()

    # Tüm işleme thread'lerinin bitmesini bekleyin
    for thread in threads:
        thread.join()

    # Kuyruğa işaret ekleyerek yazma thread'ini sonlandır
    result_queue.put(None)
    writer_thread.join()

if __name__ == "__main__":
    main()
