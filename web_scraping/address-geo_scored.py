import pandas as pd
from geo_score import score_address
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import time

# Giriş ve çıkış dosyaları
INPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_input\input_dataset\ad_id-address.csv"
OUTPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_output\modified_ad_id-address.csv"
 
# Ayarlanabilir parametreler
BATCH_SIZE = 1000  # Her batch'te kaç satır işleneceği
MAX_THREADS = 5  # Aynı anda çalışacak maksimum thread sayısı
START_BATCH = 0  # İşleme başlayacağınız batch numarası
MAX_RETRIES = 3  # Bir API çağrısında yapılacak maksimum yeniden deneme sayısı
RETRY_DELAY = 2  # Her yeniden deneme arasındaki bekleme süresi (saniye cinsinden)
        
def process_batch(batch_df):
    """
    Bir batch verisi üzerinde adreslere Geo_Score hesaplaması yapar.
    """
    def safe_score(address):
        """
        API çağrısı yapar ve hata oluşursa yeniden dener.
        """
        attempt = 0
        while attempt < MAX_RETRIES:
            try:
                return score_address(address)
            except Exception as e:
                attempt += 1
                print(f"Hata adres: {address}, Hata mesajı: {e}. Deneme {attempt}/{MAX_RETRIES}.")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)  # Yeniden denemeden önce bekle
                else:
                    print(f"Tüm denemeler başarısız oldu, adres {address} için None döndürülecek.")
                    return None  # Hata durumunda None döner
        return None  # Eğer denemeler biterse None döner

    # Full_Address sütunu oluştur
    batch_df['Full_Address'] = batch_df['Street'] + ", " + batch_df['City_Code']
    
    # Geo_Score hesaplama
    batch_df['Geo_Score'] = batch_df['Full_Address'].apply(safe_score)
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
        # MAX_THREADS kadar batch işlemini paralel olarak başlat
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
