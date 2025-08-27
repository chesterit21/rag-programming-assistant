# RAG Programming Assistant - Experimental

## BRANCH INI HANYA UNTUK EXPERIMTALS. 
### JANGAN PERNAH PULL REPOSITORY DARI BRANCH INI.

## Teknologi Utama
- **Ollama** (Model AI Utama: codegemma:7b-instruct-q4_K_M)
- **ChromaDB** (Vector Store)
- **Hugging Face Embeddings** (BAAI/bge-code-v1 & Salesforce/SFR-Embedding-Code-2B_R)
- **LangChain** (RAG Framework)
- **Gradio** (Web UI)
- **Docker** (Containerization)

👍 
Di Fedora, sebelum `pyenv install`, biasanya kita perlu install development dependency.
Coba jalankan ini:

```bash
sudo dnf groupinstall "Development Tools" -y
sudo dnf install -y \
  gcc \
  gcc-c++ \
  make \
  zlib-devel \
  bzip2 bzip2-devel \
  xz xz-devel \
  wget curl \
  libffi-devel \
  sqlite sqlite-devel \
  readline readline-devel \
  tk tk-devel \
  ncurses ncurses-devel \
  gdbm gdbm-devel \
  openssl-devel \
  xz-devel \
  libuuid-devel
```

Setelah itu, ulangi build Python:

```bash
pyenv uninstall 3.11.9
pyenv install 3.11.9

pip install --upgrade pip setuptools wheel
pip install Cython

```

Kalau semua dependency lengkap, warning `Missing the SQLite3 lib?`, `Missing the ncurses lib?` dll akan hilang ✅
Mantap 🚀 — artinya Python 3.11.9 sudah berhasil di-compile dan bisa dipakai.
Warning yang muncul hanya soal **`_tkinter`**, artinya **modul Tkinter (GUI toolkit)** tidak ikut terinstall karena library `tk` tidak ada saat build.

➡️ Kalau kamu tidak butuh **GUI app** berbasis Tkinter (misalnya `IDLE`, `tkinter` window, dll), error ini aman diabaikan ✅.
Untuk kebutuhan **RAG + embedding pipeline**, `tkinter` tidak diperlukan.

Kalau tetap ingin lengkap (biar tidak ada warning sama sekali), tinggal install dependensi Tk di Fedora, lalu compile ulang Python:

```bash
sudo dnf install -y tk tk-devel
```

Lalu ulangi:

```bash
pyenv uninstall 3.11.9
pyenv install 3.11.9
```

Nanti warning `_tkinter` akan hilang juga.

---

👉 Jadi sekarang sudah ada Python 3.11.9 siap dipakai.
Langkah berikutnya, kamu mau langsung setup **virtualenv + pip install dependency (torch, transformers, dll)**, atau kita bereskan dulu **deployment model embedding di Docker** (supaya tiap model seperti `bge-m3` atau `microsoft/codebert-base` jalan di container terpisah)?
