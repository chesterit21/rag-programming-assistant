import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

load_dotenv()

def setup_rag_chain(
    temperature: float = 0.2,
    max_tokens: int = 4096,
    gpu_layers: int = 35
):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    persist_dir = os.path.join(current_dir, "../chroma_db")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=os.getenv('EMBEDDING_MODEL', 'BAAI/bge-large-en-v1.5'),
        model_kwargs={'device': 'cuda'}
    )
    
    vector_db = Chroma(
        persist_directory=persist_dir,
        embedding_function=embeddings
    )
    
    prompt_template = """
    [INST] <<SYS>>
    Anda adalah asisten programming ahli. Gunakan konteks berikut untuk menjawab pertanyaan.
    
    Aturan:
    1. Berikan jawaban teknis dengan contoh kode jika relevan
    2. Format jawaban dalam Markdown
    3. Jika tidak tahu, jangan memaksakan jawaban
    4. Referensikan sumber jika tersedia
    <</SYS>>
    
    Konteks: {context}
    
    Pertanyaan: {question} 
    
    Jawaban:
    [/INST]
    """
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    llm = Ollama(
        base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
        model=os.getenv("OLLAMA_MODEL", "gemma3:12b-it-qat"),
        temperature=temperature,
        num_ctx=max_tokens,
        num_gpu=gpu_layers
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vector_db.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 7, "fetch_k": 20}
        ),
        chain_type_kwargs={"prompt": PROMPT},
        return_source_documents=True
    )
    
    return qa_chain

def query_rag(
    question: str,
    category: str | None = None,
    temperature: float = 0.2,
    max_tokens: int = 4096,
    gpu_layers: int = 35
):
    # Setup chain dengan parameter yang diterima, bukan dari env var
    rag_chain = setup_rag_chain(temperature, max_tokens, gpu_layers)

    if category and category.strip():
        categories = [c.strip() for c in category.replace('&', ',').replace(' ', ',').split(',') if c.strip()]
        if len(categories) == 1:
            rag_chain.retriever.search_kwargs["filter"] = {"category": categories[0]}
            print(f"🔍 Filtering documents by category: {categories[0]}")
        elif len(categories) > 1:
            or_filter = {"$or": [{"category": cat} for cat in categories]}
            rag_chain.retriever.search_kwargs["filter"] = or_filter
            print(f"🔍 Filtering documents by categories (OR): {', '.join(categories)}")

    # Langkah 1: Beri tahu UI bahwa pencarian sedang berlangsung
    yield "🔍 Mencari dokumen relevan..."

    # Langkah 2: Lakukan pengambilan dokumen (retrieval) secara manual
    retriever = rag_chain.retriever
    docs = retriever.invoke(question)
    
    # Cetak sumber ke konsol untuk debugging
    print("\n\n=== 🔗 Sources ===")
    for i, doc in enumerate(docs):
        source_path = doc.metadata.get('source_path', 'Unknown')
        doc_category = doc.metadata.get('category', 'general')
        print(f"{i+1}. {source_path} [Category: {doc_category}]")

    # Langkah 3: Beri tahu UI bahwa pembuatan jawaban dimulai
    generating_message = "✍️ Menghasilkan jawaban..."
    yield generating_message

    # Langkah 4: Format prompt secara manual dan stream langsung dari LLM
    context_text = "\n\n---\n\n".join([doc.page_content for doc in docs])
    prompt = rag_chain.combine_documents_chain.llm_chain.prompt
    llm = rag_chain.combine_documents_chain.llm_chain.llm
    
    final_prompt = prompt.format(context=context_text, question=question)

    full_response = ""
    for chunk in llm.stream(final_prompt):
        full_response += chunk
        yield generating_message + "\n\n" + full_response

if __name__ == "__main__":
    question = "berikan contoh penggunaan konsep DDD dengan membuat satu Class Model dengan nama Guru. dengan bahasa pemrograman C#. Pastikan ada Validasi nya  dan imutable"
    category = "ddd"
    
    print(f"❓ Query: {question}")
    print(f"🗂️ Using category filter: {category}")
    
    # Fungsi sekarang adalah generator, jadi kita perlu mengulanginya untuk mendapatkan hasil
    final_answer = ""
    for response_part in query_rag(question, category):
        print(response_part, end="", flush=True) # Simulasikan streaming ke konsol
        final_answer = response_part

    print("\n\n💡 Final Answer:")
    print(final_answer)