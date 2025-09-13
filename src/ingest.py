# ingests.py

import os
# Atasi peringatan deadlock dari tokenizer saat menggunakan ProcessPoolExecutor
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import glob
import torch
import json
import git
import functools
import shutil
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Iterator, Optional

# Tree-sitter (opsional, dengan fallback)
TS_AVAILABLE = True
try:
    from tree_sitter import Language, Parser
    from tree_sitter_languages import get_language as get_tree_sitter_language
except Exception:
    TS_AVAILABLE = False
    print("⚠️ Tree-sitter not available. Falling back to basic chunking for code.")
    Language = None
    Parser = None
    get_tree_sitter_language = None

# LangChain & loaders
from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, JSONLoader, UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader, UnstructuredExcelLoader, WebBaseLoader
)
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv

# ChromaDB (pakai client langsung agar bisa add embeddings precomputed)
import chromadb
from chromadb import PersistentClient, Settings

# HF Transformers untuk manual embedder
from transformers import AutoModel, AutoTokenizer, BitsAndBytesConfig

# --- Konfigurasi & Deteksi Perangkat --- #
load_dotenv()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on device: {DEVICE}")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
ERROR_DIR_ROOT = os.path.join(ROOT_DIR, "file_error_ingest")
os.makedirs(ERROR_DIR_ROOT, exist_ok=True)

# --- Konfigurasi Embedding --- #
EMBEDDING_MODELS = {
    "bge_m3":  "BAAI/bge-m3",
    "bge_code": "BAAI/bge-code-v1",
    "gemma": "google/embeddinggemma-300m",
}

DB_DIRS = {
    "bge_m3":  os.path.join(ROOT_DIR, "chroma_db_bge_m3"),
    "bge_code": os.path.join(ROOT_DIR, "chroma_db_bge_code"),
    "gemma": os.path.join(ROOT_DIR, "chroma_db_gemma"),
}

MODEL_SETTINGS = {
    # BGE-M3: Multi-lingual multi-function (text/code), context panjang
    "bge_m3": {
        "chunk_size": 4096,
        "overlap_lines": 10,
        "batch_size": 8,
        "max_length": 8192,
        "pooling": "cls", # Praktik terbaik untuk BGE adalah 'cls' pooling
        "normalize": True,
        "distance": "cosine",
    },
    # BGE-CODE: fokus code, context 4k
    "bge_code": {
        "chunk_size": 512, # Sesuaikan dengan max_length
        "overlap_lines": 10,
        "batch_size": 8,
        "max_length": 512, # bge-code-v1 memiliki konteks 512 token
        "pooling": "cls", # Praktik terbaik untuk BGE adalah 'cls' pooling
        "normalize": True,
        "distance": "cosine",
    },
    "gemma": {
        "chunk_size": 2048,
        "overlap_lines": 10,
        "batch_size": 16, # Model 300M ringan, bisa pakai batch size besar
        "max_length": 8192, # Konteks tetap 8k
        "pooling": "mean",
        "normalize": True,
        "distance": "cosine",
    },
}

# --- Pemecah Teks (Text Splitters) --- #
MARKDOWN_SPLITTER = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")],
    strip_headers=False, return_each_line=False
)

GENERIC_TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    # Ukuran chunk yang lebih kecil untuk dokumen umum agar lebih fokus.
    chunk_size=2000, 
    chunk_overlap=200
)

# --- Loader mapping --- #
LOADER_MAPPING = {
    ".pdf": PyPDFLoader,
    ".json": lambda p: JSONLoader(p, jq_schema=".", text_content=False),
    ".html": UnstructuredHTMLLoader,
    ".docx": UnstructuredWordDocumentLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".xls": UnstructuredExcelLoader,
    ".md": TextLoader,
    ".txt": TextLoader,
    ".cs": TextLoader,
    ".vue": TextLoader,
    ".py": TextLoader,
    ".js": TextLoader,
    ".ts": TextLoader,
    ".java": TextLoader,
    ".cshtml": TextLoader,
    ".yaml": TextLoader,
    ".yml": TextLoader,
    ".go": TextLoader,
}

LANGUAGE_MAPPING = {
    ".cs": "c_sharp", ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".go": "go", ".vue": "vue", ".html": "html", ".css": "css",
    ".md": "markdown", ".cshtml": "razor","yml": "yaml"
}


# ---------- Utilities ---------- #

def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # (batch, seq_len, hidden)
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask

def cls_pooling(model_output):
    """Performs CLS pooling by taking the embedding of the [CLS] token."""
    # [:, 0] mengambil embedding dari token pertama (CLS) untuk setiap item di batch
    return model_output.last_hidden_state[:, 0]


def build_manual_embedder(model_name: str, max_length: int, pooling_strategy: str, normalize: bool = True):
    """
    Manual embedder (GPU jika ada) untuk model HF apa pun yang output last_hidden_state (BERT/BGE).
    """
    # Dapatkan token dari environment variable jika modelnya adalah Gemma (gated model)
    token = None
    if "gemma" in model_name.lower():
        token = os.getenv("HUGGING_FACE_HUB_TOKEN")
        if not token:
            print("⚠️  Hugging Face token not found for Gemma. Trying without token. If download fails, set HUGGING_FACE_HUB_TOKEN in your .env file.")

    # Model dan tokenizer diunduh sekali dan disimpan di cache Hugging Face.
    # Eksekusi selanjutnya akan memuat dari cache lokal, memungkinkan operasi offline.
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=token)

    # Muat model dengan presisi optimal: float16 di GPU, float32 di CPU.
    # Ini memberikan keseimbangan terbaik antara kecepatan dan akurasi.
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    mdl = AutoModel.from_pretrained(model_name, dtype=dtype, trust_remote_code=True, token=token)
    # Memindahkan model ke perangkat yang terdeteksi (GPU/CPU) untuk eksekusi lokal.
    mdl.to(DEVICE)

    mdl.eval()

    class ManualEmbedder:
        def __init__(self, tokenizer, model, max_len, do_norm):
            # Simpan strategi pooling untuk digunakan dalam embed_documents
            self.pooling_strategy = pooling_strategy
            self.tok = tokenizer
            self.model = model
            self.max_len = max_len
            self.do_norm = do_norm

        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            if not texts:
                return []
            enc = self.tok(
                texts, padding=True, truncation=True,
                max_length=self.max_len, return_tensors='pt'
            ).to(DEVICE)
            with torch.no_grad():
                out = self.model(**enc)
            
            # Panggil fungsi pooling yang sesuai berdasarkan strategi
            sent = cls_pooling(out) if self.pooling_strategy == "cls" else mean_pooling(out, enc['attention_mask'])

            if self.do_norm:
                sent = torch.nn.functional.normalize(sent, p=2, dim=1)
            return sent.detach().cpu().numpy().tolist()

        def embed_query(self, text: str) -> List[float]:
            return self.embed_documents([text])[0]

    return ManualEmbedder(tok, mdl, max_length, normalize)


def get_git_metadata(repo: Optional[git.Repo], file_path: str) -> Dict[str, Any]:
    try:
        if repo and repo.remotes:
            origin_url = repo.remotes.origin.url if 'origin' in [r.name for r in repo.remotes] else ""
        else:
            origin_url = ""
        repo_name = origin_url.split('/')[-1].replace('.git', '') if origin_url else "local"
        last_commit = next(repo.iter_commits(paths=file_path, max_count=1)) if repo else None
        return {
            "repo_name": repo_name,
            "last_commit_date": (last_commit.committed_datetime.isoformat() if last_commit else ""),
            "last_commit_author": (last_commit.author.name if last_commit else ""),
        }
    except Exception:
        return {"repo_name": "local", "last_commit_date": "", "last_commit_author": ""}


def ast_chunker(
    code: str,
    language_name: Optional[str],
    max_chunk_size: int = 4096,
    overlap_lines: int = 10
) -> Iterator[Document]:
    """
    AST-based chunker menggunakan tree-sitter bila tersedia, fallback ke line-based bila tidak.
    """
    if not TS_AVAILABLE or language_name is None:
        # fallback: line-based chunking kasar
        lines = code.splitlines()
        chunks = []
        current = []
        current_len = 0
        for ln in lines:
            add = len(ln) + 1
            if current_len + add > max_chunk_size and current:
                chunks.append("\n".join(current))
                current = [ln]
                current_len = add
            else:
                current.append(ln)
                current_len += add
        if current:
            chunks.append("\n".join(current))
        # overlap
        docs = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev_lines = chunks[i-1].splitlines()
                overlap = "\n".join(prev_lines[-overlap_lines:])
                chunk = overlap + "\n" + chunk
            docs.append(Document(page_content=chunk, metadata={"start_line": 0}))
        return iter(docs)

    # Tree-sitter path
    try:
        if get_tree_sitter_language is None:
            # Fallback if tree-sitter is not available
            return ast_chunker(code, None, max_chunk_size, overlap_lines)
        ts_lang = get_tree_sitter_language(language_name)
    except Exception:
        # Jika grammar tidak ada, fallback
        return ast_chunker(code, None, max_chunk_size, overlap_lines)

    if Parser is None:
        # Fallback to line-based chunking if Parser is not available
        return ast_chunker(code, None, max_chunk_size, overlap_lines)
    parser = Parser()
    parser.set_language(ts_lang)
    tree = parser.parse(bytes(code, "utf8"))

    chunks: List[str] = []
    current_chunk_code = ""

    for node in tree.root_node.children:
        try:
            node_code = node.text.decode("utf8")
        except Exception:
            continue
        if len(current_chunk_code) + len(node_code) > max_chunk_size:
            if current_chunk_code:
                chunks.append(current_chunk_code)
            current_chunk_code = node_code
        else:
            current_chunk_code += ("\n" if current_chunk_code else "") + node_code

    if current_chunk_code:
        chunks.append(current_chunk_code)

    docs: List[Document] = []
    for i, chunk_text in enumerate(chunks):
        if i > 0:
            prev_chunk_lines = chunks[i-1].splitlines()
            overlap = "\n".join(prev_chunk_lines[-overlap_lines:])
            chunk_text = overlap + "\n" + chunk_text
        docs.append(Document(page_content=chunk_text, metadata={"start_line": 0}))
    return iter(docs)


def process_file(file_path: str, repo: Optional[git.Repo], chunk_size: int, overlap_lines: int) -> List[Document]:
    try:
        print(f"Processing file: {file_path}")
        ext = os.path.splitext(file_path)[1].lower()
        language_name = LANGUAGE_MAPPING.get(ext)
        
        # 1. Muat konten mentah dari file
        LoaderCls = LOADER_MAPPING.get(ext)
        if not LoaderCls:
            print(f"⚠️ No loader found for extension {ext}, skipping file {file_path}")
            return []
        
        loader = LoaderCls(file_path)
        loaded_docs = loader.load()
        if not loaded_docs:
            return []
        
        # Gabungkan konten jika loader menghasilkan beberapa dokumen (misalnya, per halaman PDF)
        content = "\n\n".join([doc.page_content for doc in loaded_docs if doc.page_content])
        
        # 2. Pilih strategi chunking yang tepat
        chunks = []
        # Penanganan khusus untuk file kamus dalam format .txt
        if ext == ".txt" and ("kamus" in file_path or "dictionary" in file_path):
            print(f"  -> Treating {os.path.basename(file_path)} as a dictionary file.")
            # Setiap baris yang tidak kosong dianggap sebagai satu dokumen/definisi utuh.
            lines = content.strip().split('\n')
            chunks = [Document(page_content=line) for line in lines if line.strip()]
        elif language_name and language_name not in ["markdown", "razor", "html", "css", "yaml"]:
            # Gunakan AST chunker untuk kode
            chunk_iterator = ast_chunker(content, language_name, max_chunk_size=chunk_size, overlap_lines=overlap_lines)
            chunks = list(chunk_iterator)
        elif language_name == "markdown":
            # Gunakan Markdown splitter
            # Markdown splitter menghasilkan Document, jadi tidak perlu konversi
            split_docs = MARKDOWN_SPLITTER.split_text(content)
            # Pastikan hanya objek Document yang valid yang diproses
            chunks = [doc for doc in split_docs if hasattr(doc, 'page_content')]
        else:
            # Fallback ke splitter umum untuk PDF, DOCX, TXT, dll.
            # Kita gunakan splitter ini pada konten yang sudah digabung.
            chunks = GENERIC_TEXT_SPLITTER.split_documents(loaded_docs)

        # 3. Tambahkan metadata ke setiap chunk
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        git_meta = get_git_metadata(repo, file_path) if repo else {}

        out_docs: List[Document] = []
        for ch in chunks:
            if not ch or not getattr(ch, "page_content", None):
                continue
            md = ch.metadata if hasattr(ch, "metadata") else {}
            md.update({
                "source_path": rel_path,
                "language": language_name or "text",
                **git_meta
            })
            out_docs.append(Document(page_content=ch.page_content, metadata=md))

        print(f"✅ Processed and chunked: {rel_path} -> {len(out_docs)} chunks")
        return out_docs

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return []

def ingest_documents():
    # Git repo untuk metadata
    try:
        repo = git.Repo(ROOT_DIR, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print("⚠️ Not a git repository. Git metadata will not be available.")
        repo = None

    # Kumpulkan file
    all_files = [p for p in glob.glob(os.path.join(DOCS_DIR, "**", "*"), recursive=True) if os.path.isfile(p)]
    if not all_files:
        print(f"⚠️ Tidak ada file di {DOCS_DIR}.")
        return

    for model_key, model_name in EMBEDDING_MODELS.items():
        settings = MODEL_SETTINGS[model_key]
        db_dir = DB_DIRS[model_key]
        error_dir = os.path.join(ERROR_DIR_ROOT, model_key)
        os.makedirs(error_dir, exist_ok=True)

        print(f"\n=== Embedding model: {model_name} ({model_key}) ===")
        print(f"Settings: {settings}")

        # 1) Chunking paralel
        print(f"🚀 Chunking parallel untuk {model_key}...")
        all_chunks: List[Document] = []
        process_file_args = {
            "chunk_size": settings["chunk_size"],
            "overlap_lines": settings["overlap_lines"]
        }
        process_func = functools.partial(process_file, repo=repo, **process_file_args)

        # NOTE: Tree-sitter bisa bermasalah di multiprocessing di beberapa OS;
        # jika error, ubah ke ThreadPoolExecutor atau proses serial.
        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(process_func, fp): fp for fp in all_files}
            for fut in as_completed(futures):
                try:
                    res = fut.result()
                    if res:
                        all_chunks.extend(res)
                except Exception as e:
                    print(f"❌ Worker gagal utk {futures[fut]}: {e}")

        if not all_chunks:
            print(f"⚠️ Tidak ada chunk untuk {model_key}. Skip.")
            continue

        print(f"✅ Total chunks: {len(all_chunks)}")
        chunk_ids = [f"{d.metadata['source_path']}::{i}" for i, d in enumerate(all_chunks)]

        # Tambahkan chunk_id ke metadata setiap dokumen untuk identifikasi unik saat retrieval
        for i, doc in enumerate(all_chunks):
            doc.metadata["chunk_id"] = chunk_ids[i]

        # 2) Buat client dan siapkan collection ChromaDB.
        # Client dibuat di sini untuk memastikan koneksi tetap hidup selama proses upsert.
        print(f"💽 Initializing ChromaDB client for {db_dir}...")
        os.makedirs(db_dir, exist_ok=True)
        # Menambahkan setting untuk menonaktifkan anonimisasi telemetri
        chroma_settings = Settings(anonymized_telemetry=False)
        client = chromadb.PersistentClient(path=db_dir, settings=chroma_settings)

        collection_name = f"{model_key}_collection"
        collection = client.get_or_create_collection(name=collection_name, metadata={"hnsw:space": settings.get("distance", "cosine")})
        print(f"  -> Collection '{collection_name}' ready. Current count: {collection.count()}")

        # 3) Siapkan embedder, pilih metode yang tepat untuk setiap model
        if model_key == "gemma":
            print("  -> Using LangChain's HuggingFaceEmbeddings for Gemma (SentenceTransformer model).")
            print("     (Proses unduh model mungkin memakan waktu beberapa menit saat pertama kali dijalankan...)")
            # Gunakan token untuk gated model
            token = os.getenv("HUGGING_FACE_HUB_TOKEN")
            model_kwargs = {'device': DEVICE, 'trust_remote_code': True}
            if token:
                model_kwargs['token'] = token
            
            embedder = HuggingFaceEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs={'normalize_embeddings': settings.get("normalize", True), 'batch_size': settings["batch_size"]}
            )
        elif DEVICE == "cuda":
            # Manual embedder untuk model BGE yang lebih fleksibel
            print("     (Proses unduh model mungkin memakan waktu beberapa menit saat pertama kali dijalankan...)")
            embedder = build_manual_embedder(
                model_name=model_name,
                max_length=settings["max_length"],
                pooling_strategy=settings["pooling"],
                normalize=settings.get("normalize", True),
            )

        # 4) Upsert batched
        total = len(all_chunks)
        bs = settings["batch_size"]
        for start in range(0, total, bs):
            end = min(start + bs, total)
            batch_docs = all_chunks[start:end]
            batch_ids = chunk_ids[start:end]
            texts = [d.page_content for d in batch_docs]
            metas = [d.metadata for d in batch_docs]

            print(f"  -> Upserting batch {start//bs + 1}/{(total + bs - 1)//bs} (size={len(texts)})")
            try:
                # Compute embeddings
                if hasattr(embedder, "embed_documents"):
                    vecs = embedder.embed_documents(texts)
                else:
                    # LangChain embedder fallback (should have embed_documents)
                    vecs = embedder.embed_documents(texts)  # type: ignore

                # Simpan ke ChromaDB
                import numpy as np
                embeddings_np = np.array(vecs, dtype=np.float32).tolist()
                collection.upsert(
                    ids=batch_ids,
                    documents=texts,
                    metadatas=metas,
                    embeddings=embeddings_np
                )
            except Exception as e:
                print(f"  ❌ Gagal upsert batch {start//bs + 1}: {e}")
                print("  -> Menyalin file bermasalah untuk inspeksi...")
                for d in batch_docs:
                    src_rel = d.metadata.get("source_path")
                    if src_rel:
                        src_abs = os.path.join(ROOT_DIR, src_rel)
                        dst = os.path.join(error_dir, os.path.basename(src_rel))
                        try:
                            if os.path.exists(src_abs):
                                shutil.copy2(src_abs, dst)
                                print(f"    -> Copied {src_rel} -> {dst}")
                        except Exception as ce:
                            print(f"    -> Gagal copy {src_rel}: {ce}")

        print(f"✅ Ingestion selesai untuk model '{model_key}' ({model_name}).")

    print("\n🎉 Semua ingestion selesai. Vector stores siap dipakai.")


if __name__ == "__main__":
    ingest_documents()
