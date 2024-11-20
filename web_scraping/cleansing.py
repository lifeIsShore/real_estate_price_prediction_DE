import pandas as pd
import numpy as np
import json
import os

# Config dosyasını yükleyen fonksiyon
def load_config(config_path):
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    else:
        raise FileNotFoundError(f"Config file not found at: {config_path}")

# Dinamik olarak sütun isimlerini config'ten çekerek veri temizleme ve özellik mühendisliği
def clean_and_engineer_features(df, config):
    columns = config["columns"]  # Sütun adlarını config'ten al
    price_col = columns["price_column"]
    living_area_col = columns["living_area_column"]
    land_size_col = columns["land_size_column"]

    # Price sütununu temizle ve sayısal forma çevir
    df[price_col] = (
        df[price_col]
        .str.replace(r"[^\d,]", "", regex=True)  # Euro sembolü ve diğer karakterleri temizle
        .str.replace(",", ".")  # Ondalık işaretini standartlaştır
        .astype(float)
    )

    # Living Area sütununu temizle ve sayısal forma çevir
    df[living_area_col] = (
        df[living_area_col]
        .str.replace(r"[^\d,]", "", regex=True)
        .str.replace(",", ".")
        .astype(float)
    )

    # Metrekare başına fiyat hesapla
    df["Price per sqm"] = df[price_col] / df[living_area_col]

    # Land Size sütunundaki "Unknown" değerlerini NaN olarak işaretle ve sayısallaştır
    df[land_size_col] = (
        df[land_size_col]
        .replace("Unknown", np.nan)
        .str.replace(r"[^\d,]", "", regex=True)
        .str.replace(",", ".")
        .astype(float)
    )

    return df

# Full address kolonunu oluşturma
def create_full_address(df, config):
    address_columns = config["columns"]["address_columns"]
    df["full_address"] = df[address_columns].agg(", ".join, axis=1)  # Adres kolonlarını birleştir
    return df

# Config yolunu belirleyin
config_path = r"C:\Users\ahmty\Desktop\Python\real_estate_price_prediction_DE\real_estate_price_prediction_DE\config.json"

# Config dosyasını yükle
config = load_config(config_path)

# CSV dosyasını yükle
input_csv_path = config.get("input_csv_path", r"C:\default\input.csv")
df = pd.read_csv(input_csv_path, delimiter=";", encoding="windows-1252")

# Full address oluşturma
df = create_full_address(df, config)

# Veri temizleme ve özellik mühendisliği
df = clean_and_engineer_features(df, config)

# Temizlenmiş veriyi kaydet
output_path = config.get("output_found_path", r"C:\default\output.csv")
df.to_csv(output_path, index=False, encoding="windows-1252")

print("Veri temizleme ve özellik mühendisliği tamamlandı.")
