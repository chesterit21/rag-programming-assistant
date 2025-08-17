import os
import glob
import torch
import json
import git
import tempfile
import functools
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Iterator, Optional
from tree_sitter import Language, Parser
from tree_sitter_languages import get_language as get_tree_sitter_language

from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, JSONLoader, UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader, UnstructuredExcelLoader, WebBaseLoader
)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from transformers import AutoModel, AutoTokenizer

# --- Konfigurasi & Deteksi Perangkat --- #
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Running on device: {DEVICE}")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")

# --- Konfigurasi Multi-Embedding --- #
EMBEDDING_MODELS = {
    "bge_code": "BAAI/bge-code-v1"
    #"sfr_code": "Salesforce/SFR-Embedding-Code-2B_R" #--tambahkan ini jika GPU kuat.
}

DB_DIRS = {
    "bge_code": os.path.join(ROOT_DIR, "chroma_db_bge_code"),
    "sfr_code": os.path.join(ROOT_DIR, "chroma_db_sfr_code")
}

# --- Konfigurasi Spesifik Model (UNTUK TUNING) --- #
MODEL_SETTINGS = {
    "bge_code": {
        "chunk_size": 4096,
        "overlap_lines": 10,
        "batch_size": 2,
    },
    "sfr_code": {
        "chunk_size": 2048, # Ukuran lebih kecil untuk model yang lebih besar
        "overlap_lines": 10,
        "batch_size": 1,      # Ukuran batch lebih kecil untuk menghemat memori GPU
    }
}

# --- Pemecah Teks (Text Splitters) --- #
MARKDOWN_SPLITTER = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3")],
    strip_headers=False, return_each_line=False
)

# --- AST-based Code Chunker --- #
def ast_chunker(
    code: str,
    language: Language,
    max_chunk_size: int = 4096,
    overlap_lines: int = 10
) -> Iterator[Dict[str, Any]]:
    """Memecah kode menggunakan AST dan menyertakan overlap."""
    parser = Parser()
    parser.set_language(language)
    tree = parser.parse(bytes(code, "utf8"))
    
    chunks = []
    current_chunk_code = ""
    
    # Iterasi melalui node tingkat atas (fungsi, kelas, dll.)
    for node in tree.root_node.children:
        node_code = node.text.decode("utf8")
        
        if len(current_chunk_code) + len(node_code) > max_chunk_size:
            if current_chunk_code:
                chunks.append(current_chunk_code)
            current_chunk_code = node_code
        else:
            current_chunk_code += "\n" + node_code
            
    if current_chunk_code:
        chunks.append(current_chunk_code)

    # Terapkan overlap
    overlapped_chunks = []
    for i, chunk_text in enumerate(chunks):
        metadata = {"start_line": 0} # Placeholder, bisa diperkaya
        if i > 0:
            prev_chunk_lines = chunks[i-1].splitlines()
            overlap = "\n".join(prev_chunk_lines[-overlap_lines:])
            chunk_text = overlap + "\n" + chunk_text
        
        overlapped_chunks.append(Document(page_content=chunk_text, metadata=metadata))
        
    return overlapped_chunks

# --- Pemuat & Pemroses Dokumen --- #
LOADER_MAPPING = {
    ".pdf": PyPDFLoader, ".json": lambda p: JSONLoader(p, jq_schema=".", text_content=False),
    ".html": UnstructuredHTMLLoader, ".docx": UnstructuredWordDocumentLoader,
    ".xlsx": UnstructuredExcelLoader, ".xls": UnstructuredExcelLoader,
    ".md": TextLoader, ".txt": TextLoader, ".cs": TextLoader, ".vue": TextLoader,
    ".py": TextLoader, ".js": TextLoader, ".ts": TextLoader, ".java": TextLoader,
    ".cshtml": TextLoader, ".go": TextLoader,
}

LANGUAGE_MAPPING = {
    ".cs": "c_sharp", ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".java": "java", ".go": "go", ".vue": "vue", ".html": "html", ".css": "css",
    ".md": "markdown", ".cshtml": "razor"
}

def get_git_metadata(repo: git.Repo, file_path: str) -> Dict[str, Any]:
    """Mendapatkan metadata Git untuk sebuah file."""
    try:
        repo_name = repo.remotes.origin.url.split('/')[-1].replace('.git', '')
        last_commit = next(repo.iter_commits(paths=file_path, max_count=1))
        return {
            "repo_name": repo_name,
            "last_commit_date": last_commit.committed_datetime.isoformat(),
            "last_commit_author": last_commit.author.name,
        }
    except Exception:
        return {
            "repo_name": "local",
            "last_commit_date": "",
            "last_commit_author": "",
        }

def process_file(file_path: str, repo: Optional[git.Repo], chunk_size: int, overlap_lines: int) -> List[Document]:
    """Memuat, memecah, dan memberi metadata pada satu file lokal."""
    try:
        ext = os.path.splitext(file_path)[1].lower()
        language_name = LANGUAGE_MAPPING.get(ext)
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        if language_name and language_name not in ["markdown", "razor", "html", "css"]:
            ts_language = get_tree_sitter_language(language_name)
            chunks = ast_chunker(content, ts_language, max_chunk_size=chunk_size, overlap_lines=overlap_lines)
        elif language_name == "markdown":
            chunks = MARKDOWN_SPLITTER.split_text(content)
        else: # Fallback untuk file teks biasa atau yang tidak didukung AST
            loader = TextLoader(file_path)
            docs = loader.load()
            # Simple splitter as fallback
            chunks = [Document(page_content=doc.page_content, metadata=doc.metadata) for doc in docs]

        # Tambahkan metadata yang kaya
        rel_path = os.path.relpath(file_path, ROOT_DIR)
        git_meta = get_git_metadata(repo, file_path) if repo else {}
        
        for chunk in chunks:
            chunk.metadata.update({
                "source_path": rel_path,
                "language": language_name or "text",
                **git_meta
            })
        
        print(f"✅ Processed and chunked: {rel_path}")
        return chunks

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return []

def ingest_documents():
    """Fungsi utama untuk menyerap semua dokumen dan membuat embedding ganda."""
    try:
        repo = git.Repo(ROOT_DIR, search_parent_directories=True)
    except git.InvalidGitRepositoryError:
        print("⚠️ Not a git repository. Git metadata will not be available.")
        repo = None

    all_files = [p for p in glob.glob(os.path.join(DOCS_DIR, "**", "*"), recursive=True) if os.path.isfile(p)]
    
    for model_key, model_name in EMBEDDING_MODELS.items():
        db_dir = DB_DIRS[model_key]
        settings = MODEL_SETTINGS[model_key]
        chunk_size = settings["chunk_size"]
        overlap_lines = settings["overlap_lines"]
        batch_size = settings["batch_size"]

        print(f"\n--- Processing for model: {model_name} with settings: {settings} ---")

        # 1. Chunking
        print(f"🚀 Starting parallel chunking for {model_key}...")
        all_chunks = []
        process_func = functools.partial(process_file, repo=repo, chunk_size=chunk_size, overlap_lines=overlap_lines)
        
        with ProcessPoolExecutor() as executor:
            future_to_file = {executor.submit(process_func, file_path): file_path for file_path in all_files}
            for future in as_completed(future_to_file):
                try:
                    all_chunks.extend(future.result())
                except Exception as e:
                    print(f"❌ A worker process failed for {future_to_file[future]}: {e}")
        
        if not all_chunks:
            print(f"⚠️ No content could be chunked for model {model_key}. Skipping.")
            continue

        print(f"\n✅ Total chunks created for {model_key}: {len(all_chunks)}")
        chunk_ids = [f"{chunk.metadata['source_path']}_{i}" for i, chunk in enumerate(all_chunks)]

        # 2. Embedding
        def process_with_embeddings(embeddings_object):
            """Helper function to process chunks with a given embedding object."""
            vector_db = Chroma(
                persist_directory=db_dir,
                embedding_function=embeddings_object,
                collection_metadata={"hnsw:space": "cosine"}
            )
            total_chunks = len(all_chunks)
            for i in range(0, total_chunks, batch_size):
                try:
                    batch_chunks = all_chunks[i:i + batch_size]
                    batch_ids = chunk_ids[i:i + batch_size]
                    print(f"  -> Upserting batch {i//batch_size + 1}/{(total_chunks + batch_size - 1)//batch_size}...")

                    # Ekstrak konten dan metadata untuk metode upsert
                    batch_documents = [chunk.page_content for chunk in batch_chunks]
                    batch_metadata = [chunk.metadata for chunk in batch_chunks]

                    # Ekstrak konten dan metadata untuk metode upsert
                    batch_documents = [chunk.page_content for chunk in batch_chunks]
                    batch_metadata = [chunk.metadata for chunk in batch_chunks]

                    # Hitung embeddings secara eksplisit
                    batch_embeddings = embeddings_object.embed_documents(batch_documents)
                    
                    vector_db._collection.upsert(
                        ids=batch_ids,
                        documents=batch_documents,
                        metadatas=batch_metadata,
                        embeddings=batch_embeddings # Teruskan embeddings yang sudah dihitung
                    )
                except Exception as e:
                    print(f"  ❌ Failed to upsert batch {i//batch_size + 1}. Error: {e}")
                    # Anda bisa menambahkan logika di sini, misalnya mencatat log
                    # kegagalan untuk ditinjau nanti.
            print(f"✅ Ingestion for mqodel '{model_key}' complete.")

        if model_key == 'bge_code':
            if DEVICE == 'cuda':
                with tempfile.TemporaryDirectory() as tmpdir:
                    print(f"   -> Menggunakan direktori sementara untuk memaksa float16 untuk bge-code: {tmpdir}")
                    
                    tokenizer = AutoTokenizer.from_pretrained(model_name)
                    model = AutoModel.from_pretrained(model_name, torch_dtype=torch.float16)
                    model.save_pretrained(tmpdir)
                    tokenizer.save_pretrained(tmpdir)
                    
                    embeddings = HuggingFaceEmbeddings(
                        model_name=tmpdir,
                        model_kwargs={'device': DEVICE},
                        encode_kwargs={'normalize_embeddings': True, 'batch_size': batch_size}
                    )
                    process_with_embeddings(embeddings)
            else:
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': DEVICE},
                    encode_kwargs={'normalize_embeddings': True, 'batch_size': batch_size}
                )
                process_with_embeddings(embeddings)
        elif model_key == 'sfr_code':
            if DEVICE == 'cuda':
                print("   -> Using manual embedding for sfr_code with float16")
                
                tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
                model = AutoModel.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    trust_remote_code=True
                ).to(DEVICE)

                def mean_pooling(model_output, attention_mask):
                    token_embeddings = model_output[0]
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
                    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                    return sum_embeddings / sum_mask

                class ManualEmbedder:
                    def embed_documents(self, texts: List[str]) -> List[List[float]]:
                        encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt').to(DEVICE)
                        with torch.no_grad():
                            model_output = model(**encoded_input)
                        sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
                        sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
                        return sentence_embeddings.cpu().numpy().tolist()

                    def embed_query(self, text: str) -> List[float]:
                        return self.embed_documents([text])[0]

                embeddings = ManualEmbedder()
                process_with_embeddings(embeddings)
            else: # CPU for sfr_code
                embeddings = HuggingFaceEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': DEVICE, 'trust_remote_code': True},
                    encode_kwargs={'normalize_embeddings': True, 'batch_size': batch_size}
                )
                process_with_embeddings(embeddings)

    print("\n🎉 All ingestions complete. Vector stores are ready.")


print("Script top-level execution finished. Entering main block...", flush=True)

if __name__ == "__main__":
    print("Inside main block. Calling ingest_documents()...", flush=True)
    ingest_documents()
