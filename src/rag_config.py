# rag_config.py

import os
import torch
from dotenv import load_dotenv

# --- Manajemen Konfigurasi Terpusat ---
load_dotenv()

class RAGConfig:
    """
    Menyimpan semua konfigurasi untuk sistem RAG.
    Dioptimalkan untuk model DeepCoder dengan konteks 128K.
    """
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Konfigurasi Model Embedding Ganda
    DB_DIRS = {
        "bge_m3": os.path.join(ROOT_DIR, "chroma_db_bge_m3"),
        "bge_code": os.path.join(ROOT_DIR, "chroma_db_bge_code"),
        "gemma": os.path.join(ROOT_DIR, "chroma_db_gemma"),
    }
    EMBEDDING_MODELS = {
        "bge_m3": "BAAI/bge-m3",
        "bge_code": "BAAI/bge-code-v1",
        "gemma": "google/embeddinggemma-300m",
    }
    COLLECTION_NAMES = {
        "bge_m3": "bge_m3_collection",
        "bge_code": "bge_code_collection",
        "gemma": "gemma_collection",
    }
    
    # --- Konfigurasi Device Spesifik ---
    # Gunakan CUDA (jika tersedia) untuk proses ingest yang berat agar lebih cepat.
    INGEST_EMBEDDING_DEVICE = DEVICE
    # Gunakan CPU untuk embedding saat RAG chain berjalan, agar VRAM bisa fokus untuk LLM.
    RAG_EMBEDDING_DEVICE = "cpu"


    # --- Pengaturan Spesifik per Model untuk Ingest & Retrieval ---
    MODEL_SETTINGS = {
        "bge_m3": {
            "chunk_size": 4096, "overlap_lines": 10, "batch_size": 8, 
            "max_length": 8192, "pooling": "cls", "normalize": True, 
            "distance": "cosine"
        },
        "bge_code": {
            "chunk_size": 512, "overlap_lines": 10, "batch_size": 8, 
            "max_length": 512, "pooling": "cls", "normalize": True, 
            "distance": "cosine"
        },
        "gemma": {
            "chunk_size": 2048, "overlap_lines": 10, "batch_size": 16, 
            "max_length": 2048, "pooling": "mean", "normalize": True, 
            "distance": "cosine"
        },
    }

    # Konfigurasi Reranker
    CROSS_ENCODER_MODEL = 'BAAI/bge-reranker-v2-m3'
    CROSS_ENCODER_DEVICE =  'cpu' #DEVICE

    # Konfigurasi LLM (DeepCoder)
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "deepcoder:1.5b-preview-q4_K_M")
    DEEPCODER_CONTEXT_SIZE = 128000 # Konteks size 128K untuk DeepCoder

    # Konfigurasi Proses Retrieval (Dioptimalkan untuk Konteks Besar)
    RETRIEVER_SEARCH_TYPE = "similarity"
    INITIAL_K = 25  # Ambil lebih banyak dokumen awal dari setiap retriever
    TOP_N_RERANKED = 20 # Ambil lebih banyak dokumen teratas setelah reranking untuk mengisi konteks

    # Deskripsi tugas untuk query embedding (praktik terbaik untuk model BGE)
    TASK_DESCRIPTIONS = {
        "bge_m3": "Represent this sentence for searching relevant passages: ",
        "bge_code": "Represent this code for searching relevant code snippets: ",
        "gemma": "" # Gemma tidak memerlukan instruksi
    }

    # --- Template Prompt yang Dioptimalkan untuk DeepCoder ---
    PROMPT_QUESTION_REWRITE_ID = """
<start_of_turn>user
Anda adalah ahli dalam penulisan ulang query. Tugas Anda HANYA menulis ulang pertanyaan lanjutan menjadi pertanyaan mandiri yang sangat deskriptif, berdasarkan riwayat percakapan.
Tugas Anda BUKAN untuk menjawab pertanyaan.

Pertanyaan yang ditulis ulang harus berisi semua konteks yang diperlukan dari riwayat percakapan, sehingga optimal untuk sistem pencarian kode (code retrieval system).

**Contoh 1:**
RIWAYAT: User: "Apa itu decorator?" Assistant: "Decorator adalah fungsi yang mengubah fungsi lain."
PERTANYAAN LANJUTAN: "Beri saya contohnya"
PERTANYAAN MANDIRI: "Beri contoh code decorator di Python dan penjelasannya"

**Contoh 2:**
RIWAYAT: User: "Saya error 'IndexError: list index out of range' di function get_user_data"
PERTANYAAN LANJUTAN: "Bagaimana cara memperbaikinya?"
PERTANYAAN MANDIRI: "Bagaimana cara memperbaiki error 'IndexError: list index out of range' di function get_user_data?"

---
RIWAYAT PERCAKAPAN:
{chat_history}

PERTANYAAN LANJUTAN:
{question}
<end_of_turn>
<start_of_turn>model
PERTANYAAN MANDIRI YANG DIOPTIMALKAN:
"""

    PROMPT_WITH_CONTEXT_ID = """
<start_of_turn>user
Anda adalah SFCore-Assistant, seorang insinyur perangkat lunak senior. Tugas Anda adalah menjawab pertanyaan pengguna HANYA berdasarkan konteks yang disediakan di bawah ini.

**ATURAN MUTLAK (ZERO-TOLERANCE):**
1.  **Konteks adalah Segalanya:** Jawaban Anda HARUS secara ketat didasarkan pada informasi yang disediakan dalam konteks. Jika jawaban yang akurat tidak dapat ditemukan dalam konteks, Anda HARUS menolak untuk menjawab dan menyatakan bahwa informasi yang relevan tidak ditemukan.
2.  **Dilarang Halusinasi:** DILARANG KERAS menambahkan informasi, fakta, atau kode yang tidak secara eksplisit ada dalam konteks yang diberikan. Ini termasuk detail sintaksis kecil yang tidak sesuai dengan konteks.
3.  **Struktur Jawaban:** Ikuti struktur berikut secara persis. JANGAN menambahkan section lain.
    ```
    **Solusi Kode:**
    [Tulis seluruh blok kode yang lengkap dan dapat dijalankan di sini. Prioritaskan kode dari konteks yang diberikan.]

    **Penjelasan:**
    [Jelaskan kode tersebut dengan jelas dan ringkas dalam Bahasa Indonesia. Jelaskan mengapa kode itu ditulis seperti itu berdasarkan konteks.]

    **Sumber:**
    - `[source_path_1]` [Jelaskan secara singkat cuplikan apa yang diambil dari sumber ini]
    - `[source_path_2]` [Jelaskan secara singkat cuplikan apa yang diambil dari sumber ini]
    ```
4.  **Kutip Sumber:** Anda WAJIB mengutip semua sumber dari konteks yang digunakan untuk membangun jawaban. Referensikan `source_path` dari metadata.

---
KONTEKS YANG DISEDIAKAN (DARI DATABASE KODE):
{context}
---

RIWAYAT PERCAKAPAN SEBELUMNYA (Hanya untuk konteks percakapan, bukan untuk fakta):
{chat_history}
---

PERTANYAAN PENGGUNA SAAT INI:
{question}
<end_of_turn>
<start_of_turn>model
**Solusi Kode:**
"""  

# Perhatikan bagaimana kita langsung memulai dengan memaksa struktur output.

    PROMPT_NO_CONTEXT_ID = """
<start_of_turn>user
Anda adalah SFCore-Assistant. Anda tidak menemukan dokumen yang relevan dalam database kode untuk menjawab pertanyaan pengguna.

Jawab pertanyaan pengguna **HAYA JIKA** pertanyaannya bersifat umum tentang konsep pemrograman, algoritma, atau teknologi yang luas (contoh: "Apa itu MVC?", "Jelaskan garbage collection").

**ATURAN:**
- Jika pertanyaan spesifik terhadap codebase, proyek, atau kode tertentu (misalnya menanyakan function `x`, error di file `y`), Anda HARUS menolak menjawab dan menjelaskan bahwa informasinya tidak ditemukan dalam dokumentasi.
- Jika pertanyaan umum, jawab dengan ringkas dan teknis dalam Bahasa Indonesia.
- Selalu tekankan bahwa jawaban ini berdasarkan pengetahuan umum, bukan dari codebase spesifik.

---
RIWAYAT PERCAKAPAN SEBELUMNYA:
{chat_history}
---

PERTANYAAN PENGGUNA SAAT INI:
{question}
<end_of_turn>
<start_of_turn>model
"""
# Buat instance tunggal dari konfigurasi untuk diimpor di seluruh aplikasi
config = RAGConfig()

