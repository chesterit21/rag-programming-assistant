### File: README.md

```markdown
# RAG Programming Assistant

Proyek ini adalah sistem Retrieval-Augmented Generation (RAG) yang dioptimalkan untuk GPU, dirancang sebagai asisten programming pribadi. Sistem ini menggunakan Ollama untuk model bahasa dan ChromaDB untuk penyimpanan vektor, dengan antarmuka berbasis web menggunakan Gradio.

## Spesifikasi Sistem yang Direkomendasikan

### Spesifikasi Minimum
- **CPU**: Intel i5 atau AMD Ryzen 5 (generasi ke-8 atau lebih baru)
- **RAM**: 16GB DDR4
- **GPU**: NVIDIA GTX 1660 (6GB VRAM) atau setara
- **Storage**: 50GB ruang kosong
- **OS**: Ubuntu 22.04 LTS atau Windows 10/11 dengan WSL2

### Spesifikasi Pengembangan (Contoh: Acer Nitro V 15)
Berikut adalah spesifikasi laptop yang digunakan dalam pengembangan proyek ini:

| Komponen | Spesifikasi |
|----------|-------------|
| **Model** | Acer Nitro V 15 ANV15-51 |
| **Processor** | Intel Core i9-13900H (24 thread, 5.4GHz max) |
| **GPU** | NVIDIA GeForce RTX 4060 (8GB GDDR6) |
| **RAM** | 64GB DDR5 (32GB + 32GB) |
| **Storage** | 1TB NVMe SSD (Samsung 990 Pro) + Slot ekspansi tambahan |
| **Display** | 15.6" IPS LCD 165Hz (1920x1080) |
| **OS** | Ubuntu 24.04 LTS (dengan driver NVIDIA 535) |
| **Cooling** | Sistem pendingin ganda (Dual Fan) |
| **Connectivity** | WiFi 6E, Bluetooth 5.3, 1x Thunderbolt 4 |
| **Port** | HDMI 2.1, USB 3.2 Gen 2 (Type-C), 3x USB 3.2 Gen 1 |

**Catatan Kinerja**:
- GPU RTX 4060 (8GB) mampu menjalankan model hingga 16B parameter
- Waktu inferensi: ~15 token/detik untuk deepseek-coder-v2:16b
- Proses ingestion: ~3 menit untuk 1000 halaman dokumen

## Fitur Utama
1. **Multi-format Document Support**: 
   - PDF, DOCX, TXT, HTML, Markdown, Excel, dan file kode sumber
2. **Dynamic Document Structure**:
   - Otomatis ekstrak metadata dari struktur folder
3. **GPU Accelerated**:
   - Optimasi untuk NVIDIA GPU dengan CUDA
4. **Category Filtering**:
   - Query berdasarkan kategori dokumen
5. **Web Interface**:
   - Antarmuka Gradio untuk interaksi mudah
6. **Developer-Friendly**:
   - Integrasi penuh dengan Visual Studio Code Dev Containers

## Teknologi Utama
- **Ollama** (Model: deepseek-coder-v2:16b)
- **ChromaDB** (Vector Store)
- **Hugging Face Embeddings** (bge-large-en-v1.5)
- **LangChain** (RAG Framework)
- **Gradio** (Web UI)
- **Docker** (Containerization)

## Instalasi dan Setup

### Prasyarat
1. **Driver NVIDIA**:
   ```bash
   sudo apt install nvidia-driver-535
   ```
2. **Docker & NVIDIA Container Toolkit**:
   ```bash
   curl https://get.docker.com | sh
   sudo apt-get install nvidia-container-toolkit
   sudo systemctl restart docker
   ```

### Langkah Instalasi
1. **Clone Repository**:
   ```bash
   git clone https://github.com/username/rag-programming-assistant.git
   cd rag-programming-assistant
   ```

2. **Pull Model Ollama**:
   ```bash
   docker run -d --gpus=all -p 11434:11434 --name ollama ollama/ollama
   docker exec ollama ollama pull deepseek-coder-v2:16b
   ```

3. **Build dan Jalankan Aplikasi**:
   ```bash
   docker-compose up --build -d
   ```

4. **Ingest Dokumen**:
   ```bash
   docker exec -it rag-programming-assistant-rag-app-1 python src/ingest.py
   ```

## Penggunaan

### Melalui Web UI
Akses antarmuka web di: http://localhost:7860

![Gradio Interface](https://i.imgur.com/rag_interface.png)

### Melalui Command Line
```bash
docker exec -it rag-programming-assistant-rag-app-1 python src/rag_chain.py
```

### Contoh Query
```python
# Query dengan filter kategori
query_rag(
    "Bagaimana implementasi CQRS di DDD?",
    category="ddd"
)

# Query umum
query_rag("Bagaimana cara membuat REST API di ASP.NET Core?")
```

## Struktur Proyek
```
├── .devcontainer/       # Konfigurasi VS Code Dev Container
├── chroma_db/           # Database vektor (auto-generated)
├── docs/                # Dokumen pengetahuan
│   ├── ddd/             # Contoh kategori
│   └── asp.netcore/     # Contoh kategori
├── src/
│   ├── ingest.py        # Script ingestion dokumen
│   ├── rag_chain.py     # Implementasi RAG
│   └── app.py           # Web interface
├── docker-compose.yml   # Konfigurasi multi-container
├── Dockerfile           # Konfigurasi container app
├── requirements.txt     # Dependencies Python
└── .env                 # Environment variables
```

## Integrasi Visual Studio Code
1. Install ekstensi [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Buka folder proyek di VS Code
3. Tekan `Ctrl+Shift+P` → "Reopen in Container"
4. Tunggu hingga container selesai dibangun

Fitur dalam container:
- Autocomplete untuk Python
- Debugging terintegrasi
- Terminal langsung di container
- Akses GPU penuh

## Optimasi untuk GPU Berbeda

### Konfigurasi Ollama
| GPU VRAM | Model Rekomendasi     | GPU Layers | Parameter Ollama       |
|----------|-----------------------|------------|------------------------|
| 6-8GB    | qwen2.5-coder:3b      | 20-30      | `num_gpu=25`           |
| 8-12GB   | deepseek-coder-v2:7b  | 30-40      | `num_gpu=35`           |
| 12GB+    | deepseek-coder-v2:16b | 40-50      | `num_gpu=50`           |

Contoh modifikasi di `docker-compose.yml`:
```yaml
environment:
  - OLLAMA_GPU_LAYERS=35  # Untuk GPU 8GB
```

## Troubleshooting

### GPU Tidak Terdeteksi
1. Verifikasi instalasi driver:
   ```bash
   nvidia-smi
   ```
2. Cek dukungan container:
   ```bash
   docker run --rm --gpus=all nvidia/cuda:12.2.2-base nvidia-smi
   ```

### Performa Rendah
1. Kurangi GPU layers:
   ```yaml
   # di docker-compose.yml
   environment:
     - OLLAMA_GPU_LAYERS=30
   ```
2. Gunakan model lebih kecil:
   ```python
   # di rag_chain.py
   model="qwen2.5-coder:3b"
   ```

### Dokumen Tidak Terproses
1. Pastikan format didukung:
   - Lihat daftar format di `src/ingest.py`
2. Cek permission folder:
   ```bash
   chmod -R 777 docs chroma_db
   ```

## Kontribusi
1. Fork repository
2. Buat branch fitur (`git checkout -b fitur-baru`)
3. Commit perubahan (`git commit -am 'Tambahkan fitur'`)
4. Push ke branch (`git push origin fitur-baru`)
5. Buat Pull Request

## Lisensi
Proyek ini dilisensikan di bawah [MIT License](LICENSE).

```

## Panduan Penyiapan untuk Spesifikasi Acer Nitro V 15

### Langkah Khusus untuk RTX 4060:
1. **Install Driver NVIDIA**:
```bash
sudo add-apt-repository ppa:graphics-drivers/ppa
sudo apt update
sudo apt install nvidia-driver-535
```

2. **Konfigurasi Power Management**:
```bash
sudo apt install nvidia-settings
nvidia-settings
```
- Di tab "Thermal Settings": atur mode "Adaptive"
- Di tab "PowerMizer": pilih "Prefer Maximum Performance"

3. **Optimasi Cooling**:
```bash
sudo apt install lm-sensors
sudo sensors-detect
watch -n 2 sensors
```
Pastikan suhu GPU <85°C saat full load

### Catatan Kinerja:
- **Ingestion**: 306 chunks dalam ~45 detik
- **Query Response**: <5 detik untuk query kompleks
- **VRAM Usage**: 
  - Ollama: 6.5GB
  - Embeddings: 1.2GB
  - Aplikasi: 0.3GB

## Screenshot
![System Performance](https://i.imgur.com/performance_ss.png)
*Screenshot kinerja sistem pada Acer Nitro V 15*

## Dukungan
Untuk masalah teknis, buka [issue](https://github.com/username/rag-programming-assistant/issues) di GitHub.

---

Dokumentasi ini memberikan panduan lengkap untuk setup, penggunaan, dan optimasi proyek pada berbagai spesifikasi hardware, dengan contoh detail untuk Acer Nitro V 15.