import pandas as pd
from geo_score import score_address
import threading
from queue import Queue

# Global değişkenler
BATCH_SIZE = 1000
INPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_input\input_dataset\cleansed_ready_for model.csv"
OUTPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_output\updated_dataset.csv"

def process_batch(batch_df, result_queue):
    """
    Bir veri grubundaki adresler için puanlama işlemini gerçekleştirir.
    """
    def safe_score_address(address):
        try:
            return score_address(address)
        except Exception as e:
            print(f"Hata: {address}, {e}")
            return None

    batch_df["Address Score"] = batch_df["Address"].apply(safe_score_address)
    result_queue.put(batch_df)

def save_batches_to_file(queue, output_file):
    """
    Kuyruktan gelen işlem sonuçlarını belirtilen dosyaya yazdırır.
    """
    while True:
        batch = queue.get()
        if batch is None:  # Kuyruk boş ve işlem bitmişse çıkış yap
            break
        batch.to_csv(output_file, mode='a', index=False, header=False, encoding='utf-8')

def main():
    # Veri setini yükle
    df = pd.read_csv(INPUT_FILE, encoding='utf-8')  # Özel karakterler için uygun encoding
    
    # Adres sütununu oluştur
    df["Address"] = df["Street"] + ", " + df["City_Code"]
    
    # Çıkış dosyası için başlık yaz
    df.head(0).to_csv(OUTPUT_FILE, index=False, encoding='utf-8')  # Başlığı yazmak için ilk satırı kullan
    
    # İşlem sonuçlarını saklamak için bir kuyruk oluştur
    result_queue = Queue()
    
    # Sonuçları yazan thread
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
