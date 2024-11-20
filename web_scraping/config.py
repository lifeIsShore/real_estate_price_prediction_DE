import tkinter as tk
from tkinter import filedialog
import json

# Konfigürasyon dosyasının kaydedileceği dosya yolu
config_file = "config.json"

def save_config():
    # Kullanıcıdan dosya yollarını al
    input_csv_path = input_csv_entry.get()
    output_found_path = output_found_entry.get()

    # Konfigürasyon verisini oluştur
    config_data = {
        "input_csv_path": input_csv_path,
        "output_found_path": output_found_path
    }

    # Konfigürasyon verisini JSON dosyasına kaydet
    with open(config_file, 'w') as json_file:
        json.dump(config_data, json_file, indent=4)
    
    # Kullanıcıya bilgilendirme mesajı
    status_label.config(text="Configuration saved successfully!", fg="green")

def browse_input_csv():
    # Dosya seçici penceresi aç
    file_path = filedialog.askopenfilename(title="Select Input CSV File", filetypes=[("CSV files", "*.csv")])
    input_csv_entry.delete(0, tk.END)  # Mevcut değeri sil
    input_csv_entry.insert(0, file_path)  # Yeni dosya yolunu ekle

def browse_output_found():
    # Dosya seçici penceresi aç
    folder_path = filedialog.askdirectory(title="Select Output Folder")
    output_found_entry.delete(0, tk.END)  # Mevcut değeri sil
    output_found_entry.insert(0, folder_path)  # Yeni klasör yolunu ekle

# Ana pencereyi oluştur
root = tk.Tk()
root.title("Configuration UI")

# Dosya yolu girişleri ve etiketleri
tk.Label(root, text="Input CSV Path:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
input_csv_entry = tk.Entry(root, width=50)
input_csv_entry.grid(row=0, column=1, padx=10, pady=10)
input_csv_button = tk.Button(root, text="Browse", command=browse_input_csv)
input_csv_button.grid(row=0, column=2, padx=10, pady=10)

tk.Label(root, text="Output Folder Path:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
output_found_entry = tk.Entry(root, width=50)
output_found_entry.grid(row=1, column=1, padx=10, pady=10)
output_found_button = tk.Button(root, text="Browse", command=browse_output_found)
output_found_button.grid(row=1, column=2, padx=10, pady=10)

# Kaydet butonu
save_button = tk.Button(root, text="Save Configuration", command=save_config)
save_button.grid(row=2, column=1, padx=10, pady=20)

# Durum etiketi
status_label = tk.Label(root, text="", fg="red")
status_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Ana pencereyi başlat
root.mainloop()
