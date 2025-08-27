# call_model_embedding.py

import os
from ingest import ingest_documents

def main():
    """
    Fungsi utama untuk mengorkestrasi pemanggilan skrip-skrip ingest.
    """
    # --- Konfigurasi Jaringan untuk Hugging Face Hub ---
    # Menambah timeout untuk mengatasi koneksi lambat saat download model besar.
    # Defaultnya adalah 10 detik, kita naikkan menjadi 60 detik.
    os.environ["HF_HUB_DOWNLOAD_TIMEOUT"] = "60"
    # Menambah jumlah percobaan ulang jika terjadi error jaringan sementara.
    os.environ["HF_HUB_DOWNLOAD_RETRIES"] = "3"
    
    # Daftar skrip yang akan dijalankan secara berurutan
    # ingest.py already handles all models including bge-code, so ingest_bge_code.py is redundant.
    scripts_to_run = [
        "ingest.py"
    ]

    print("Memulai proses orkestrasi ingest embedding model...")
    try:
        # Panggil fungsi ingesti secara langsung
        ingest_documents()
        print("\n>>> Semua proses ingesti telah berhasil dieksekusi. <<<")
    except Exception as e:
        print(f"\nERROR: Proses orkestrasi gagal: {e}")

if __name__ == "__main__":
    main()
