# ingests.py
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import glob, torch, json, git, functools, shutil, re, time
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Iterator, Optional

# Tree-sitter (optional)
TS_AVAILABLE = True
try:
    from tree_sitter import Language, Parser
    from tree_sitter_languages import get_language as get_tree_sitter_language
except Exception:
    TS_AVAILABLE = False

# LangChain, ChromaDB, Transformers
from langchain.docstore.document import Document
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, TextLoader, JSONLoader, UnstructuredHTMLLoader, UnstructuredWordDocumentLoader, UnstructuredExcelLoader
from dotenv import load_dotenv
import chromadb
from chromadb import PersistentClient, Settings
from transformers import AutoModel, AutoTokenizer

# --- Config ---
load_dotenv()
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
ERROR_DIR_ROOT = os.path.join(ROOT_DIR, "file_error_ingest")
os.makedirs(ERROR_DIR_ROOT, exist_ok=True)

EMBEDDING_MODELS = {
    "bge_m3": "BAAI/bge-m3",
    "bge_code": "BAAI/bge-code-v1",
    "gemma": "google/embeddinggemma-300m",
}
DB_DIRS = {k: os.path.join(ROOT_DIR, f"chroma_db_{k}") for k in EMBEDDING_MODELS}
MODEL_SETTINGS = {
    "bge_m3": {"chunk_size": 4096, "overlap_lines": 10, "batch_size": 8, "max_length": 8192, "pooling": "cls", "normalize": True, "distance": "cosine"},
    "bge_code": {"chunk_size": 512, "overlap_lines": 10, "batch_size": 8, "max_length": 512, "pooling": "cls", "normalize": True, "distance": "cosine"},
    "gemma": {"chunk_size": 2048, "overlap_lines": 10, "batch_size": 16, "max_length": 8192, "pooling": "mean", "normalize": True, "distance": "cosine"},
}
EMBEDDER_CACHE = {}

# --- Splitters & Loaders ---
MARKDOWN_SPLITTER = MarkdownHeaderTextSplitter(headers_to_split_on=[("#", "H1"), ("##", "H2"), ("###", "H3")])
GENERIC_TEXT_SPLITTER = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
LOADER_MAPPING = {
    ".pdf": PyPDFLoader, ".json": lambda p: JSONLoader(p, jq_schema=".", text_content=False),
    ".html": UnstructuredHTMLLoader, ".docx": UnstructuredWordDocumentLoader, ".xlsx": UnstructuredExcelLoader,
    ".md": TextLoader, ".txt": TextLoader, ".cs": TextLoader, ".vue": TextLoader, ".py": TextLoader,
    ".js": TextLoader, ".ts": TextLoader, ".java": TextLoader, ".cshtml": TextLoader, ".yaml": TextLoader, ".yml": TextLoader, ".go": TextLoader,
}
LANGUAGE_MAPPING = {ext: lang for ext, lang in {
    ".cs": "c_sharp", ".py": "python", ".js": "javascript", ".ts": "typescript", ".java": "java", ".go": "go",
    ".vue": "vue", ".html": "html", ".css": "css", ".md": "markdown", ".cshtml": "razor", ".yml": "yaml"
}.items()}

# ---------- Utilities ---------- #
def clean_content(text: str, language: Optional[str] = None) -> str:
    """
    Cleans text content by normalizing whitespace, handling encoding,
    and optionally removing comments and lowercasing based on language.
    """
    # 1. Handle encoding issues and remove non-ASCII characters
    text = text.encode("utf-8", "ignore").decode("utf-8")
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    # 2. Remove comments if it's a known code language
    if language and language not in ["markdown", "text", "yaml", "yml"]:
        # Regex for C-style (//, /*...*/), Python/Ruby (#)
        text = re.sub(r'//.*?$|/\*.*?\*/|#.*?$', '', text, flags=re.MULTILINE | re.DOTALL)

    # 3. Normalize whitespace. For Markdown, preserve newlines needed for splitting.
    if language != "markdown":
        text = re.sub(r'[ \t\r\f\v]+', ' ', text) # Replace various whitespace with a single space
        text = re.sub(r'\n{3,}', '\n\n', text) # Collapse more than 2 newlines
    else:
        text = re.sub(r' +', ' ', text) # Only collapse multiple spaces on the same line

    # 4. Lowercase for non-code or case-insensitive languages
    if not language or language in ["text", "markdown"]:
         text = text.lower()

    return text.strip()

def ast_chunker(content: str, language_name: str, max_chunk_size: int, overlap_lines: int) -> Iterator[str]:
    """
    Splits code into chunks based on its AST using tree-sitter.
    Falls back to RecursiveCharacterTextSplitter if tree-sitter fails.
    """
    try:
        ts_lang = get_tree_sitter_language(language_name)
        parser = Parser()
        parser.set_language(ts_lang)
        tree = parser.parse(bytes(content, "utf8"))
        
        # Node types that are good candidates for top-level chunks
        # This can be customized per language for better results
        split_nodes = ['function_definition', 'class_definition', 'method_definition']

        chunks = []
        current_chunk = ""
        
        def traverse(node):
            nonlocal current_chunk
            if node.type in split_nodes:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = node.text.decode('utf-8')
            else:
                for child in node.children:
                    traverse(child)

        traverse(tree.root_node)
        if current_chunk: chunks.append(current_chunk)
        
        return iter(chunks if chunks else [content])
    except Exception:
        return iter(RecursiveCharacterTextSplitter(chunk_size=max_chunk_size, chunk_overlap=overlap_lines).split_text(content))

def mean_pooling(model_output, attention_mask):
    tok_emb = model_output[0]
    mask = attention_mask.unsqueeze(-1).expand(tok_emb.size()).float()
    return torch.sum(tok_emb * mask, 1) / torch.clamp(mask.sum(1), min=1e-9)

def cls_pooling(model_output):
    return model_output.last_hidden_state[:, 0]

def build_manual_embedder(model_name: str, max_length: int, pooling: str, normalize: bool = True):
    if model_name in EMBEDDER_CACHE: return EMBEDDER_CACHE[model_name]
    token = os.getenv("HUGGING_FACE_HUB_TOKEN") if "gemma" in model_name.lower() else None
    tok = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=token)
    dtype = torch.float16 if DEVICE == "cuda" else torch.float32
    mdl = AutoModel.from_pretrained(model_name, dtype=dtype, trust_remote_code=True, token=token).to(DEVICE).eval()

    class ManualEmbedder:
        def __init__(self, tokenizer, model, max_len, do_norm, pool_strat):
            self.tok, self.model, self.max_len, self.do_norm, self.pool = tokenizer, model, max_len, do_norm, pool_strat

        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            if not texts: return []
            enc = self.tok(texts, padding=True, truncation=True, max_length=self.max_len, return_tensors='pt').to(DEVICE)
            with torch.no_grad(): out = self.model(**enc)
            sent = cls_pooling(out) if self.pool == "cls" else mean_pooling(out, enc['attention_mask'])
            if self.do_norm: sent = torch.nn.functional.normalize(sent, p=2, dim=1)
            return sent.cpu().numpy().tolist()

    embedder = ManualEmbedder(tok, mdl, max_length, normalize, pooling)
    EMBEDDER_CACHE[model_name] = embedder
    return embedder

def get_git_metadata(repo: Optional[git.Repo], file_path: str) -> Dict[str, Any]:
    try:
        origin_url = repo.remotes.origin.url if repo and repo.remotes else ""
        repo_name = origin_url.split('/')[-1].replace('.git', '') if origin_url else "local"
        commit = next(repo.iter_commits(paths=file_path, max_count=1)) if repo else None
        return {"repo_name": repo_name, "last_commit_date": commit.committed_datetime.isoformat() if commit else "", "last_commit_author": commit.author.name if commit else ""}
    except Exception: return {"repo_name": "local", "last_commit_date": "", "last_commit_author": ""}

def analyze_chunks(chunks: List[Document], model_key: str):
    if not chunks: return
    char_lengths = [len(c.page_content) for c in chunks]
    print(f"  🔍 Chunk Analysis for '{model_key}':")
    print(f"     - Count: {len(chunks)}")
    print(f"     - Avg Length: {sum(char_lengths) / len(char_lengths):.2f} chars")
    print(f"     - Min/Max Length: {min(char_lengths)} / {max(char_lengths)} chars")

def process_file(file_path: str, repo: Optional[git.Repo], chunk_size: int, overlap_lines: int, model_key: str) -> List[Document]:
    try:
        ext = os.path.splitext(file_path)[1].lower()
        lang = LANGUAGE_MAPPING.get(ext)

        loader = LOADER_MAPPING.get(ext, TextLoader)(file_path)
        docs = loader.load()
        if not docs: return []
        
        content = clean_content(
            "\n\n".join(d.page_content for d in docs if d.page_content),
            language=lang
        )
        
        chunks = []
        if ext == ".txt" and ("kamus" in file_path or "dictionary" in file_path):
            chunks = [Document(page_content=line) for line in content.strip().split('\n') if line.strip()]
        elif TS_AVAILABLE and lang and lang not in ["markdown", "html", "css"]:
            # Use AST chunker for code files
            chunks = list(ast_chunker(content, lang, max_chunk_size=chunk_size, overlap_lines=overlap_lines))
        elif lang == "markdown":
            chunks = MARKDOWN_SPLITTER.split_text(content)
        else:
            chunks = GENERIC_TEXT_SPLITTER.split_documents([Document(page_content=content)])

        rel_path = os.path.relpath(file_path, ROOT_DIR)
        git_meta = get_git_metadata(repo, file_path)
        base_meta = {"source_path": rel_path, "language": lang or "text", "model_used": model_key, "embedding_date": datetime.now().isoformat(), "file_type": ext.strip('.'), "tags": "", "relevance_score": 1.0, "feedback": ""} 
        
        out_docs = []
        for ch in chunks:
            if not ch or not getattr(ch, "page_content", None): continue
            md = {**base_meta, **git_meta, **(ch.metadata if hasattr(ch, "metadata") else {})}
            out_docs.append(Document(page_content=ch.page_content, metadata=md))

        # Jika setelah semua proses, tidak ada dokumen yang dihasilkan, anggap sebagai kegagalan sunyi
        if not out_docs:
            print(f"⚠️  Warning: No content/chunks generated from file {file_path}. Skipping.")
            return []

        return out_docs
    except Exception as e: 
        print(f"❌ Error processing {file_path}: {e}")
        try:
            # Buat direktori error spesifik untuk model yang sedang berjalan
            error_dir_for_model = os.path.join(ERROR_DIR_ROOT, model_key)
            os.makedirs(error_dir_for_model, exist_ok=True)
            
            # Salin file yang bermasalah untuk inspeksi lebih lanjut
            shutil.copy(file_path, error_dir_for_model)
            print(f"  ↪️  File yang gagal telah disalin ke: {error_dir_for_model}")
        except Exception as copy_e:
            print(f"  ⚠️ Gagal menyalin file bermasalah {file_path}: {copy_e}")
        return []

def ingest_documents():
    try: repo = git.Repo(ROOT_DIR, search_parent_directories=True)
    except git.InvalidGitRepositoryError: repo = None

    all_files = [p for p in glob.glob(os.path.join(DOCS_DIR, "**", "*"), recursive=True) if os.path.isfile(p)]
    if not all_files: return print(f"⚠️ No files in {DOCS_DIR}.")

    # Statistik yang lebih jelas
    stats = {"successful_ops": 0, "failed_ops": 0, "total_chunks": 0}
    start_time = time.time()

    for model_key, model_name in EMBEDDING_MODELS.items():
        model_start_time = time.time()
        settings = MODEL_SETTINGS[model_key]
        print(f"\n=== Embedding with '{model_name}' ({model_key}) ===")
        
        process_func = functools.partial(process_file, repo=repo, **{k: settings[k] for k in ["chunk_size", "overlap_lines"]}, model_key=model_key)
        model_files_processed = 0
        
        all_chunks = []
        with (ThreadPoolExecutor if os.name == 'nt' else ProcessPoolExecutor)() as executor:
            futures = {executor.submit(process_func, fp): fp for fp in all_files}
            for fut in as_completed(futures):
                res = fut.result()
                if res:
                    stats["successful_ops"] += 1
                    all_chunks.extend(res)
                    model_files_processed += 1
                else:
                    stats["failed_ops"] += 1
        if not all_chunks: continue
        stats["total_chunks"] += len(all_chunks)
        analyze_chunks(all_chunks, model_key)

        for i, doc in enumerate(all_chunks):
            doc.metadata["chunk_id"] = f"{doc.metadata['source_path']}::{i}"

        client = chromadb.PersistentClient(path=DB_DIRS[model_key], settings=Settings(anonymized_telemetry=False))
        collection = client.get_or_create_collection(name=f"{model_key}_collection", metadata={"hnsw:space": settings["distance"]})
        embedder = build_manual_embedder(model_name, **{k: settings[k] for k in ["max_length", "pooling", "normalize"]})

        total, bs = len(all_chunks), settings["batch_size"]
        for start in range(0, total, bs):
            end = min(start + bs, total)
            batch = all_chunks[start:end]
            texts = [d.page_content for d in batch]
            
            try:
                vecs = embedder.embed_documents(texts)
                if len(vecs) != len(batch):
                    print(f"  ⚠️ Mismatch embeddings for batch {start//bs+1}: got {len(vecs)} vectors for {len(batch)} documents. Skipping batch.")
                    continue
                collection.upsert(ids=[d.metadata["chunk_id"] for d in batch], documents=texts, metadatas=[d.metadata for d in batch], embeddings=vecs)
            except Exception as e:
                failed_files = {d.metadata.get('source_path', 'unknown') for d in batch}
                print(f"  ❌ Upsert failed for batch {start//bs+1}: {e}. Files in batch: {', '.join(failed_files)}")
        
        model_time = time.time() - model_start_time
        print(f"📊 Model '{model_key}': Ingested {len(all_chunks)} chunks from {model_files_processed} files in {model_time:.2f}s.")

    total_time = time.time() - start_time
    print(f"\n🎉 Ingestion complete in {total_time:.2f}s. Total Stats: {stats['successful_ops']} successful operations, {stats['failed_ops']} failed operations, {stats['total_chunks']} total chunks generated.")

if __name__ == "__main__":
    print(f"Running on device: {DEVICE}")
    ingest_documents()