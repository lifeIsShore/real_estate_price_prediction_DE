import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

# Config dosyasını yükleme
def load_config(config_path="config.json"):
    if os.path.exists(config_path):
        with open(config_path, "r") as config_file:
            return json.load(config_file)
    else:
        return {}  # Config dosyası yoksa boş bir dictionary döndürüyoruz.

# Config dosyasına kaydetme
def save_config(config, config_path="config.json"):
    with open(config_path, "w") as config_file:
        json.dump(config, config_file, indent=4)

# Dosya yolu seçme için bir fonksiyon
def browse_file(entry_widget):
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_widget.delete(0, tk.END)  # Var olan metni sil
        entry_widget.insert(0, file_path)  # Yeni yolu ekle

def browse_folder(entry_widget):
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_widget.delete(0, tk.END)  # Var olan metni sil
        entry_widget.insert(0, folder_path)  # Yeni yolu ekle

# UI arayüzü
def create_ui():
    config = load_config()

    window = tk.Tk()
    window.title("Config Settings")

    # Dosya yolu inputları ve etiketleri
    tk.Label(window, text="Input CSV Path:").grid(row=0, column=0, sticky="e")
    input_path_entry = tk.Entry(window, width=50)
    input_path_entry.grid(row=0, column=1)
    input_path_entry.insert(0, config.get("input_csv_path", ""))

    browse_input_button = tk.Button(window, text="Browse", command=lambda: browse_file(input_path_entry))
    browse_input_button.grid(row=0, column=2)

    tk.Label(window, text="Output Folder Path:").grid(row=1, column=0, sticky="e")
    output_path_entry = tk.Entry(window, width=50)
    output_path_entry.grid(row=1, column=1)
    output_path_entry.insert(0, config.get("output_found_path", ""))

    browse_output_button = tk.Button(window, text="Browse", command=lambda: browse_folder(output_path_entry))
    browse_output_button.grid(row=1, column=2)

    tk.Label(window, text="Batch Size:").grid(row=2, column=0, sticky="e")
    batch_size_entry = tk.Entry(window, width=20)
    batch_size_entry.grid(row=2, column=1)
    batch_size_entry.insert(0, str(config.get("batch_size", 1000)))

    tk.Label(window, text="Max Workers:").grid(row=3, column=0, sticky="e")
    max_workers_entry = tk.Entry(window, width=20)
    max_workers_entry.grid(row=3, column=1)
    max_workers_entry.insert(0, str(config.get("max_workers", 10)))

    # Kaydetme fonksiyonu
    def save_settings():
        config["input_csv_path"] = input_path_entry.get()
        config["output_found_path"] = output_path_entry.get()
        config["batch_size"] = int(batch_size_entry.get())
        config["max_workers"] = int(max_workers_entry.get())
        
        save_config(config)
        
        # Başarı mesajı
        messagebox.showinfo("Başarılı", "Ayarlar başarıyla kaydedildi!")
        
        window.destroy()  # UI'yi kapat

    save_button = tk.Button(window, text="Save Settings", command=save_settings)
    save_button.grid(row=4, column=1)

    window.mainloop()

# Ana fonksiyon
if __name__ == "__main__":
    create_ui()
