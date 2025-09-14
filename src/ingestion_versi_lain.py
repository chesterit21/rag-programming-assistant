# ingest.py (Revised for Speed and Memory Efficiency)
import os
import glob
import torch
import git
import functools
import shutil
import re
import time
import logging
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional, Tuple

# Menggunakan konfigurasi terpusat
from rag_config import config

# Tree-sitter (opsional)
TS_AVAILABLE = True
try:
    from tree_sitter import Parser
    from tree_sitter_languages import get_language
except ImportError:
    TS_AVAILABLE = False

# LangChain, ChromaDB, Transformers
from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, JSONLoader, UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader, UnstructuredExcelLoader
)
import chromadb
from chromadb import Settings
from transformers import AutoModel, AutoTokenizer

# --- Konfigurasi Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# --- Direktori ---
ROOT_DIR = config.ROOT_DIR
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
ERROR_DIR_ROOT = os.path.join(ROOT_DIR, "file_error_ingest")
os.makedirs(ERROR_DIR_ROOT, exist_ok=True)

# --- Pemetaan Loader dan Bahasa ---
LOADER_MAPPING = {
    ".pdf": PyPDFLoader, ".json": lambda p: JSONLoader(p, jq_schema=".", text_content=False),
    ".html": UnstructuredHTMLLoader, ".docx": UnstructuredWordDocumentLoader, ".xlsx": UnstructuredExcelLoader,
    ".md": TextLoader, ".txt": TextLoader, ".cs": TextLoader, ".vue": TextLoader, ".py": TextLoader,
    ".js": TextLoader, ".ts": TextLoader, ".java": TextLoader, ".cshtml": TextLoader, ".yaml": TextLoader,
    ".yml": TextLoader, ".go": TextLoader,
}
LANGUAGE_MAPPING = {
    ".cs": "c_sharp", ".py": "python", ".js": "javascript", ".ts": "typescript", ".java": "java",
    ".go": "go", ".vue": "vue", ".html": "html", ".css": "css", ".md": "markdown",
    ".cshtml": "razor", ".yml": "yaml"
}

# --- Utilitas ---
def clean_content(text: str) -> str:
    """Membersihkan konten teks dengan menormalkan spasi dan menghapus karakter non-ASCII."""
    try:
        text = text.encode("utf-8", "ignore").decode("utf-8")
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        text = re.sub(r'[ \t\r\f\v]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip().lower()
    except Exception as e:
        logging.warning(f"Gagal membersihkan konten: {e}")
        return ""

def get_chunks_for_document(doc: Document, lang: Optional[str]) -> List[Document]:
    """Memecah satu dokumen menjadi beberapa chunk berdasarkan bahasanya."""
    content = doc.page_content
    source_path = doc.metadata.get("source_path", "")

    if ".txt" in source_path and ("kamus" in source_path or "dictionary" in source_path):
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        return [Document(page_content=line, metadata=doc.metadata) for line in lines]

    if TS_AVAILABLE and lang and lang not in ["markdown", "html", "css", "yaml", "razor"]:
        try:
            ts_lang = get_language(lang)
            parser = Parser()
            parser.set_language(ts_lang)
            tree = parser.parse(bytes(content, "utf8"))
        except Exception:
            pass
    
    if lang == "markdown":
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "H1"), ("##", "H2"), ("###", "H3")])
        md_chunks = splitter.split_text(content)
        for chunk in md_chunks:
            chunk.metadata = {**doc.metadata, **chunk.metadata}
        return md_chunks

    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    return splitter.split_documents([doc])

def process_file(file_path: str, repo: Optional[git.Repo]) -> Optional[Tuple[List[Document], str]]:
    """Memproses satu file: memuat, membersihkan, dan membuat dokumen awal."""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in LOADER_MAPPING:
            return None

        lang = LANGUAGE_MAPPING.get(ext)
        loader = LOADER_MAPPING[ext](file_path)
        docs = loader.load()
        if not docs or not any(d.page_content for d in docs):
            return None

        full_content = "\n\n".join(d.page_content for d in docs if d.page_content)
        cleaned_content = clean_content(full_content)
        if not cleaned_content:
            return None

        rel_path = os.path.relpath(file_path, ROOT_DIR)
        
        git_meta = {}
        if repo:
            try:
                commit = next(repo.iter_commits(paths=file_path, max_count=1))
                git_meta = {"last_commit_date": commit.committed_datetime.isoformat(), "last_commit_author": commit.author.name}
            except Exception:
                pass 

        base_meta = {"source_path": rel_path, "language": lang or "text", "file_type": ext.strip('.')}
        initial_doc = Document(page_content=cleaned_content, metadata={**base_meta, **git_meta})
        chunked_docs = get_chunks_for_document(initial_doc, lang)
        return chunked_docs, file_path
    except Exception as e:
        logging.error(f"Gagal memproses file {file_path}: {e}", exc_info=True)
        try:
            # Salin file yang bermasalah untuk inspeksi lebih lanjut ke direktori error utama
            os.makedirs(ERROR_DIR_ROOT, exist_ok=True)
            shutil.copy(file_path, ERROR_DIR_ROOT)
            logging.info(f"File yang gagal '{os.path.basename(file_path)}' telah disalin ke: {ERROR_DIR_ROOT}")
        except Exception as copy_e:
            logging.warning(f"Gagal menyalin file bermasalah {file_path}: {copy_e}")
        return None

def mean_pooling(model_output, attention_mask):
    tok_emb = model_output[0]
    mask = attention_mask.unsqueeze(-1).expand(tok_emb.size()).float()
    return torch.sum(tok_emb * mask, 1) / torch.clamp(mask.sum(1), min=1e-9)

def cls_pooling(model_output):
    return model_output.last_hidden_state[:, 0]

class ManualEmbedder:
    """Wrapper untuk model embedding dari Hugging Face."""
    def __init__(self, tokenizer, model, pool_strat, do_norm, max_len, device):
        self.tok, self.model, self.pool, self.do_norm, self.max_len, self.device = tokenizer, model, pool_strat, do_norm, max_len, device

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts: return []
        enc = self.tok(texts, padding=True, truncation=True, max_length=self.max_len, return_tensors='pt').to(self.device)
        with torch.no_grad(): out = self.model(**enc)
        sent = cls_pooling(out) if self.pool == "cls" else mean_pooling(out, enc['attention_mask'])
        if self.do_norm: sent = torch.nn.functional.normalize(sent, p=2, dim=1)
        return sent.cpu().numpy().tolist()

def build_manual_embedder(model_name: str, settings: Dict[str, Any]):
    """Membangun embedder sesuai permintaan (bukan pre-loading)."""
    logging.info(f"Membangun embedder untuk model: {model_name}...")
    token = os.getenv("HUGGING_FACE_HUB_TOKEN") if "gemma" in model_name.lower() else None
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=token)
    # Gunakan INGEST_EMBEDDING_DEVICE untuk proses ingest
    dtype = torch.float16 if config.INGEST_EMBEDDING_DEVICE == "cuda" else torch.float32
    mdl = AutoModel.from_pretrained(model_name, dtype=dtype, trust_remote_code=True, token=token).to(config.INGEST_EMBEDDING_DEVICE).eval()
    return ManualEmbedder(tok, mdl, settings['pooling'], settings['normalize'], settings['max_length'], config.INGEST_EMBEDDING_DEVICE)

def ingest_documents():
    """Alur kerja ingesti yang dioptimalkan untuk kecepatan dan efisiensi memori."""
    try:
        repo = git.Repo(ROOT_DIR, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        repo = None

    all_files = [p for p in glob.glob(os.path.join(DOCS_DIR, "**", "*"), recursive=True) if os.path.isfile(p)]
    if not all_files:
        logging.warning(f"Tidak ada file yang ditemukan di {DOCS_DIR}.")
        return

    logging.info(f"Menemukan {len(all_files)} file untuk diproses.")
    
    # === TAHAP 1: Proses File dan Chunking (Dilakukan Sekali) ===
    start_time = time.time()
    all_processed_chunks = []
    
    with (ThreadPoolExecutor if os.name == 'nt' else ProcessPoolExecutor)() as executor:
        futures = {executor.submit(process_file, fp, repo): fp for fp in all_files}
        for future in as_completed(futures):
            result = future.result()
            if result: all_processed_chunks.extend(result[0])

    if not all_processed_chunks:
        logging.error("Tidak ada chunk yang berhasil dibuat dari semua file. Proses dihentikan.")
        return

    processing_time = time.time() - start_time
    logging.info(f"Tahap 1 (File Processing) selesai dalam {processing_time:.2f} detik. Total {len(all_processed_chunks)} chunk dibuat.")

    # === TAHAP 2: Embedding (Model-by-Model untuk Hemat Memori) ===
    for model_key, model_name in config.EMBEDDING_MODELS.items():
        model_start_time = time.time()
        logging.info(f"\n{'='*10} Memulai proses untuk model: '{model_key}' {'='*10}")
        
        # 1. Muat model khusus untuk iterasi ini
        settings = config.MODEL_SETTINGS[model_key]
        embedder = build_manual_embedder(model_name, settings)
        
        client = chromadb.PersistentClient(path=config.DB_DIRS[model_key], settings=Settings(anonymized_telemetry=False))
        collection = client.get_or_create_collection(name=config.COLLECTION_NAMES[model_key], metadata={"hnsw:space": settings["distance"]})
        
        model_specific_chunks = []
        for i, chunk in enumerate(all_processed_chunks):
            new_meta = chunk.metadata.copy()
            new_meta.update({"model_used": model_key, "embedding_date": datetime.now().isoformat(), "chunk_id": f"{chunk.metadata.get('source_path', 'unknown')}::{i}"})
            model_specific_chunks.append(Document(page_content=chunk.page_content, metadata=new_meta))

        batch_size = settings["batch_size"]
        for i in range(0, len(model_specific_chunks), batch_size):
            batch = model_specific_chunks[i : i + batch_size]
            texts = [doc.page_content for doc in batch]
            ids = [doc.metadata["chunk_id"] for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            try:
                embeddings = embedder.embed_documents(texts)
                collection.upsert(ids=ids, documents=texts, metadatas=metadatas, embeddings=embeddings)
            except Exception as e:
                logging.error(f"Gagal upsert batch untuk model {model_key}: {e}", exc_info=True)
        
        # 2. Hapus referensi untuk melepaskan memori
        del embedder
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        model_time = time.time() - model_start_time
        logging.info(f"Proses untuk model '{model_key}' selesai dalam {model_time:.2f} detik.")

    total_time = time.time() - start_time
    logging.info(f"\n🎉 Semua proses ingesti selesai dalam {total_time:.2f} detik.")

if __name__ == "__main__":
    ingest_documents()
