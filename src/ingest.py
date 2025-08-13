import os
import glob
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    JSONLoader,
    UnstructuredMarkdownLoader,
    UnstructuredHTMLLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

def load_documents(docs_dir):
    documents = []
    
    file_types = {
        "*.pdf": PyPDFLoader,
        "*.txt": TextLoader,
        "*.json": lambda path: JSONLoader(path, jq_schema=".", text_content=False),
        "*.md": UnstructuredMarkdownLoader,
        "*.html": UnstructuredHTMLLoader,
        "*.docx": UnstructuredWordDocumentLoader,
        "*.xlsx": UnstructuredExcelLoader,
        "*.xls": UnstructuredExcelLoader,
        "*.cs": TextLoader,
        "*.py": TextLoader,
        "*.js": TextLoader,
        "*.ts": TextLoader,
        "*.java": TextLoader,
        "*.go": TextLoader
    }
    
    for pattern, loader_class in file_types.items():
        for file_path in glob.glob(os.path.join(docs_dir, "**", pattern), recursive=True):
            try:
                if loader_class == JSONLoader:
                    loader = loader_class(file_path)
                else:
                    loader = loader_class(file_path)
                
                docs = loader.load()
                
                for doc in docs:
                    rel_path = os.path.relpath(file_path, docs_dir)
                    parts = rel_path.split(os.sep)
                    category = parts[0] if len(parts) > 1 else "root"
                    doc.metadata["category"] = category
                    doc.metadata["source_path"] = rel_path
                
                documents.extend(docs)
                print(f"✅ Loaded {len(docs)} documents from: {file_path}")
            except Exception as e:
                print(f"❌ Error loading {file_path}: {str(e)}")
    
    return documents

def ingest_documents():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    docs_dir = os.path.join(current_dir, "../docs")
    
    if not os.path.exists(docs_dir):
        raise ValueError(f"Docs directory not found: {docs_dir}")
    
    print(f"🚀 Starting ingestion from: {docs_dir}")
    documents = load_documents(docs_dir)
    
    if not documents:
        print("⚠️ No documents found. Exiting.")
        return
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
        separators=["\n\n", "\nclass ", "\ndef ", "\n#", "\n//", "\nfunction ", "\n}", "\n</"]
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"✂️ Split {len(documents)} documents into {len(chunks)} chunks.")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=os.getenv('EMBEDDING_MODEL', 'BAAI/bge-large-en-v1.5'),
        model_kwargs={'device': 'cuda'},
        encode_kwargs={'device': 'cuda', 'batch_size': 128}
    )
    
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=os.path.join(current_dir, "../chroma_db"),
        collection_metadata={"hnsw:space": "cosine"}
    )
    
    print(f"💾 Persisted vector store with {len(chunks)} chunks in chroma_db")

if __name__ == "__main__":
    ingest_documents()