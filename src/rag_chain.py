import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

load_dotenv()

def setup_rag_chain():
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
        model="gemma3:12b-it-qat",
        temperature=float(os.getenv("OLLAMA_TEMPERATURE", "0.2")),
        num_ctx=int(os.getenv("OLLAMA_NUM_CTX", "4096")),
        num_gpu=50,
        system="""
        Anda adalah asisten programming ahli yang membantu dengan berbagai teknologi.
        Spesialisasi: .NET Core, DDD, Python, dan pengembangan web modern.
        Format jawaban: Markdown dengan highlight kode.
        """,
        callbacks=[StreamingStdOutCallbackHandler()]
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

def query_rag(question, category=None):
    rag_chain = setup_rag_chain()
    
    if category:
        rag_chain.retriever.search_kwargs["filter"] = {"category": category}
        print(f"🔍 Filtering documents by category: {category}")
    
    result = rag_chain.invoke({"query": question})
    
    print("\n\n=== 🔗 Sources ===")
    for i, doc in enumerate(result['source_documents']):
        source_path = doc.metadata.get('source_path', 'Unknown')
        doc_category = doc.metadata.get('category', 'general')
        print(f"{i+1}. {source_path} [Category: {doc_category}]")
    
    return result["result"]

if __name__ == "__main__":
    question = "Bagaimana implementasi repository pattern di DDD dengan .NET Core?"
    category = "ddd"
    
    print(f"❓ Query: {question}")
    print(f"🗂️ Using category filter: {category}")
    
    answer = query_rag(question, category)
    print("\n\n💡 Final Answer:")
    print(answer)