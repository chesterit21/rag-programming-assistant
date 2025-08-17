# call_model_embedding.py

import subprocess
import sys
import os

def run_script(script_path: str):
    """
    Menjalankan sebuah skrip Python menggunakan interpreter yang sama dan
    menangani potensi error.

    Args:
        script_path: Path absolut menuju skrip yang akan dijalankan.

    Returns:
        True jika berhasil, False jika terjadi error.
    """
    if not os.path.exists(script_path):
        print(f"\nERROR: Skrip tidak ditemukan di: {script_path}")
        return False

    script_name = os.path.basename(script_path)
    print(f"--- Memulai eksekusi: {script_name} ---")
    
    try:
        # Menjalankan skrip. check=True akan melempar CalledProcessError jika
        # skrip mengembalikan exit code non-zero.
        # Output dari skrip akan langsung ditampilkan di konsol.
        subprocess.run(
            [sys.executable, script_path], 
            check=True,
            text=True
        )
        print(f"--- Selesai eksekusi: {script_name} berhasil ---")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Eksekusi {script_name} gagal dengan exit code {e.returncode}.")
        # Output (stdout/stderr) sudah otomatis ditampilkan, jadi tidak perlu print lagi.
        return False
    except Exception as e:
        print(f"\nERROR: Terjadi kesalahan tak terduga saat menjalankan {script_name}: {e}")
        return False

def main():
    """
    Fungsi utama untuk mengorkestrasi pemanggilan skrip-skrip ingest.
    """
    # Dapatkan direktori di mana skrip ini berada untuk membuat path yang robust
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Daftar skrip yang akan dijalankan secara berurutan
    scripts_to_run = [
        "ingest.py",
        "ingest_bge_code.py"
    ]

    print("Memulai proses orkestrasi ingest embedding model...")

    for script_name in scripts_to_run:
        script_path = os.path.join(script_dir, script_name)
        
        # Jalankan skrip dan jika gagal, hentikan proses
        if not run_script(script_path):
            print("\nProses orkestrasi dihentikan karena terjadi error.")
            break
    else:
        # Blok ini hanya berjalan jika loop selesai tanpa `break`
        print("\n>>> Semua skrip telah berhasil dieksekusi. <<<")

if __name__ == "__main__":
    main()

