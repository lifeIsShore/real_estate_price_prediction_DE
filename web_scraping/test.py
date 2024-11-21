import pandas as pd
from geo_score import score_address

# Giriş ve çıkış dosyaları
INPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_input\input_dataset\ad_id-address.csv"
OUTPUT_FILE = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\csv_input\input_dataset\modified_ad_id-address.csv"

def main():
    # Veri setini yükle
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8-sig')  # Kodlamayı utf-8-sig olarak değiştirdik
    
    # Adres sütununu oluştur
    df['Full_Address'] = df['Street'] + ", " + df['City_Code']
    
    # Geo score hesaplama
    def safe_score(address):
        try:
            return score_address(address)
        except Exception as e:
            print(f"Hata adres: {address}, Hata mesajı: {e}")
            return None  # Hata oluşursa None döner
    
    # Geo_Score sütununu ekle
    df['Geo_Score'] = df['Full_Address'].apply(safe_score)
    
    # Çıkış dosyasına yazma
    df.to_csv(OUTPUT_FILE, sep=';', index=False, encoding='utf-8-sig')  # Çıkışı utf-8-sig ile kaydediyoruz
    print(f"Sonuç dosyası başarıyla kaydedildi: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
