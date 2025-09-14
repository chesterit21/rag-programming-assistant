# rag_chain.py
import os
import torch
import tiktoken
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings import Embeddings
from langchain_chroma import Chroma
from langchain.prompts import PromptTemplate
from sentence_transformers import CrossEncoder
from typing import List, Dict, Any
from transformers import AutoModel, AutoTokenizer

# Impor instance konfigurasi terpusat
from rag_config import config

print(f"Running on device: {config.DEVICE}")

def mean_pooling(model_output, attention_mask):
    """Performs mean pooling on the token embeddings."""
    token_embeddings = model_output[0]  # (batch, seq_len, hidden)
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask

def cls_pooling(model_output):
    """Performs CLS pooling by taking the embedding of the [CLS] token."""
    return model_output.last_hidden_state[:, 0]

class ManualHuggingFaceEmbeddings(Embeddings):
    """
    A robust manual implementation for Hugging Face embeddings that mimics
    the LangChain Embeddings interface.
    """
    def __init__(self, tokenizer, model, pooling_strategy="mean", normalize=True):
        self.pooling_strategy = pooling_strategy
        self.tokenizer = tokenizer
        self.model = model
        self.normalize = normalize

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []
        
        encoded_input = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors='pt'
        ).to(self.model.device)
        
        with torch.no_grad():
            model_output = self.model(**encoded_input)
        
        if self.pooling_strategy == "cls":
            sentence_embeddings = cls_pooling(model_output)
        else: # default to mean
            sentence_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
        
        if self.normalize:
            sentence_embeddings = torch.nn.functional.normalize(sentence_embeddings, p=2, dim=1)
            
        return sentence_embeddings.detach().cpu().numpy().tolist()

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

def build_manual_embedder(model_name: str, device: str, pooling_strategy: str):
    """Builds a manual embedder by loading a model and tokenizer directly from Hugging Face."""
    token = None
    if "gemma" in model_name.lower():
        token = os.getenv("HUGGING_FACE_HUB_TOKEN")

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=token)
    dtype = torch.float16 if device == "cuda" else torch.float32
    model = AutoModel.from_pretrained(model_name, dtype=dtype, trust_remote_code=True, token=token)
    model.to(device)

    model.eval()
    return ManualHuggingFaceEmbeddings(tokenizer, model, pooling_strategy=pooling_strategy)

class RAGSystem:
    """Mengelola semua komponen RAG dan memuat model saat dibutuhkan."""
    def __init__(self, cfg: 'RAGConfig'):
        self.config = cfg
        self.vector_dbs: Dict[str, Chroma] = {}
        self.embeddings: Dict[str, Embeddings] = {}
        self.cross_encoder = None
        self.llm = None
        self.tokenizer = None
        self.prompt_with_context = None
        self.prompt_no_context = None
        self.prompt_question_rewrite = None

    def _initialize_tokenizer(self):
        if self.tokenizer is None:
            print("Initializing tokenizer for context management...")
            self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def _initialize_embeddings(self):
        if not self.embeddings:
            print("Initializing embedding models...")
            for key, model_name in self.config.EMBEDDING_MODELS.items():
                # Gunakan RAG_EMBEDDING_DEVICE untuk proses RAG
                print(f" -> Loading model: {model_name} on {self.config.RAG_EMBEDDING_DEVICE}")

                if key == "gemma":
                    print("    - Using LangChain's HuggingFaceEmbeddings for Gemma (SentenceTransformer model).")
                    token = os.getenv("HUGGING_FACE_HUB_TOKEN")
                    model_kwargs = {'device': self.config.RAG_EMBEDDING_DEVICE, 'trust_remote_code': True}
                    if token:
                        model_kwargs['token'] = token

                    self.embeddings[key] = HuggingFaceEmbeddings(
                        model_name=model_name,
                        model_kwargs=model_kwargs,
                        encode_kwargs={'normalize_embeddings': True}
                    )
                else:
                    pooling_strategy = "cls"
                    print(f"    - Using '{pooling_strategy}' pooling strategy for {key}.")
                    self.embeddings[key] = build_manual_embedder(
                        model_name=model_name,
                        device=self.config.RAG_EMBEDDING_DEVICE,
                        pooling_strategy=pooling_strategy
                    )

    def _initialize_vectordbs(self):
        if not self.vector_dbs:
            self._initialize_embeddings()
            print("Loading vector databases...")
            for key, db_dir in self.config.DB_DIRS.items():
                if not os.path.exists(db_dir):
                    raise FileNotFoundError(f"Vector DB not found for '{key}' at {db_dir}. Run ingest.py.")
                collection_name = self.config.COLLECTION_NAMES.get(key)
                db = Chroma(
                    persist_directory=db_dir,
                    embedding_function=self.embeddings[key],
                    collection_name=collection_name
                )
                self.vector_dbs[key] = db
                try:
                    count = db._collection.count()
                    print(f" -> Collection '{collection_name}' loaded with {count} documents.")
                except Exception as e:
                    print(f" -> Gagal menghitung dokumen di '{collection_name}': {e}")

    def _initialize_cross_encoder(self):
        if self.cross_encoder is None:
            print(f"Initializing Cross-Encoder on {self.config.CROSS_ENCODER_DEVICE}...")
            self.cross_encoder = CrossEncoder(self.config.CROSS_ENCODER_MODEL, device=self.config.CROSS_ENCODER_DEVICE)

    def _initialize_llm_and_prompts(self, temperature, max_tokens, gpu_layers):
        if self.llm is None:
            effective_gpu_layers = gpu_layers if self.config.DEVICE == "cuda" else 0
            self.llm = Ollama(
                base_url=self.config.OLLAMA_BASE_URL,
                model=self.config.OLLAMA_MODEL,
                temperature=temperature,
                num_ctx=max_tokens,
                num_gpu=effective_gpu_layers,
                stop=["\nPengguna:", "\nAsisten:", "\nUser:", "\nAssistant:", "<start_of_turn>", "<end_of_turn>"]
            )
        
        if self.prompt_with_context is None:
            self.prompt_with_context = PromptTemplate(
                template=self.config.PROMPT_WITH_CONTEXT_ID,
                input_variables=["chat_history", "context", "question"]
            )
        
        if self.prompt_no_context is None:
            self.prompt_no_context = PromptTemplate(
                template=self.config.PROMPT_NO_CONTEXT_ID,
                input_variables=["chat_history", "question"]
            )

        if self.prompt_question_rewrite is None:
            self.prompt_question_rewrite = PromptTemplate(
                template=self.config.PROMPT_QUESTION_REWRITE_ID,
                input_variables=["chat_history", "question"]
            )

rag_system = RAGSystem(config)

def _format_history(chat_history: List[List[str]]) -> str:
    if not chat_history:
        return "Tidak ada riwayat percakapan."
    buffer = [f"Pengguna: {user_msg}\nAsisten: {ai_msg}" for user_msg, ai_msg in chat_history]
    return "\n".join(buffer)

def _rewrite_question_with_history(question: str, chat_history_str: str) -> str:
    if not chat_history_str or chat_history_str == "Tidak ada riwayat percakapan.":
        return question

    prompt = rag_system.prompt_question_rewrite.format(chat_history=chat_history_str, question=question)
    
    print(f"\n---✍️  Merevisi Pertanyaan---")
    print(f"Pertanyaan Asli: {question}")
    
    rewritten_question = rag_system.llm.invoke(prompt).strip()
    
    print(f"Pertanyaan Revisi: {rewritten_question}")
    print("---------------------------\n")
    
    return rewritten_question

def _rrf_fuse(results: List[List[any]], k=60) -> List[any]:
    """Menggabungkan hasil pencarian menggunakan Reciprocal Rank Fusion (RRF)."""
    fused_scores = {}
    for docs in results:
        for rank, doc in enumerate(docs):
            doc_id = doc.metadata.get("chunk_id", doc.page_content)
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {"score": 0, "doc": doc}
            fused_scores[doc_id]["score"] += 1 / (rank + k)

    reranked_results = sorted(fused_scores.values(), key=lambda x: x["score"], reverse=True)
    return [item["doc"] for item in reranked_results]

def rerank_documents(query: str, docs: List) -> List:
    if not docs:
        return []
    rag_system._initialize_cross_encoder()
    model_inputs = [[query, doc.page_content] for doc in docs]
    scores = rag_system.cross_encoder.predict(model_inputs)
    doc_scores = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    top_n = rag_system.config.TOP_N_RERANKED
    reranked_docs = [doc for doc, score in doc_scores[:top_n]]
    print(f"\n=== 🏆 Re-ranked Sources (Top {top_n}) ===")
    for i, (doc, score) in enumerate(doc_scores[:top_n]):
        source_path = doc.metadata.get('source_path', 'Unknown')
        print(f"{i+1}. {source_path} [Relevance Score: {score:.4f}]")
    return reranked_docs

def _build_context(docs: List, max_tokens: int) -> str:
    """Membangun string konteks yang tidak melebihi batas token."""
    rag_system._initialize_tokenizer()
    context_text = ""
    total_tokens = 0

    for doc in docs:
        doc_content = f"Source: {doc.metadata.get('source_path', 'N/A')}\n\n{doc.page_content}"
        doc_tokens = len(rag_system.tokenizer.encode(doc_content))
        
        if total_tokens + doc_tokens > max_tokens:
            print(f"Context limit reached. Used {total_tokens} tokens. Stopping context build.")
            break
            
        context_text += "\n\n---\n\n" + doc_content
        total_tokens += doc_tokens
        
    return context_text

def query_rag(
    question: str,
    chat_history: List[List[str]],
    temperature: float = 0.1,
    max_tokens: int = 8192,
    gpu_layers: int = 35
):
    """
    Alur kerja RAG lengkap yang dioptimalkan untuk DeepCoder.
    """
    effective_max_tokens = config.DEEPCODER_CONTEXT_SIZE - 4096 
    rag_system._initialize_llm_and_prompts(temperature, effective_max_tokens, gpu_layers)
    
    history_str = _format_history(chat_history)
    rewritten_question = _rewrite_question_with_history(question, history_str)
    
    yield "🔍 Melakukan pencarian ganda..."
    rag_system._initialize_vectordbs()
    all_retrieved_docs = []
    for key, vector_db in rag_system.vector_dbs.items():
        instruction = config.TASK_DESCRIPTIONS.get(key, "")
        query_text = instruction + rewritten_question
        print(f" -> Querying with '{key}'. Instruction: {'Yes' if instruction else 'No'}")

        retriever = vector_db.as_retriever(search_kwargs={"k": config.INITIAL_K})
        docs = retriever.invoke(query_text)
        all_retrieved_docs.append(docs)
        print(f" -> Ditemukan {len(docs)} dokumen dengan '{key}'.")

    yield "🤝 Menggabungkan hasil pencarian (RRF)..."
    fused_docs = _rrf_fuse(all_retrieved_docs)

    yield "🎯 Melakukan peringkat ulang dokumen..."
    reranked_docs = rerank_documents(rewritten_question, fused_docs)

    yield "✍️ Membangun konteks dan menghasilkan jawaban..."
    
    prompt_overhead = 2000 
    context_token_limit = effective_max_tokens - prompt_overhead
    context_text = _build_context(reranked_docs, context_token_limit)

    if not context_text:
        print("⚠️ No context built after retrieval and reranking. Using no-context prompt.")
        final_prompt = rag_system.prompt_no_context.format(chat_history=history_str, question=question)
    else:
        final_prompt = rag_system.prompt_with_context.format(chat_history=history_str, context=context_text, question=question)

    full_response = ""
    for chunk in rag_system.llm.stream(final_prompt):
        full_response += chunk
        yield full_response

if __name__ == "__main__":
    # Contoh penggunaan
    # from rag_config import RAGConfig
    # rag_system = RAGSystem(RAGConfig())
    # # Inisialisasi dan jalankan query
    pass

