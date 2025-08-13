import gradio as gr
from rag_chain import query_rag
import os

def ask_question(question, category, temperature, max_tokens, gpu_layers):
    os.environ["OLLAMA_TEMPERATURE"] = str(temperature)
    os.environ["OLLAMA_NUM_CTX"] = str(max_tokens)
    os.environ["OLLAMA_NUM_GPU"] = str(gpu_layers)
    return query_rag(question, category)

iface = gr.Interface(
    fn=ask_question,
    inputs=[
        gr.Textbox(label="Pertanyaan", lines=3, placeholder="Ajukan pertanyaan teknis..."),
        gr.Textbox(label="Kategori (opsional)", placeholder="ddd, asp.netcore, dll."),
        gr.Slider(0, 1, value=0.2, label="Temperature"),
        gr.Slider(128, 16384, value=4096, label="Max Tokens"),
        gr.Slider(0, 100, value=50, label="GPU Layers")
    ],
    outputs=gr.Markdown(label="Jawaban"),
    title="Programming Assistant RAG",
    description="Asisten Programming dengan RAG dan Ollama",
    examples=[
        ["Bagaimana implementasi Repository Pattern di DDD?", "ddd", 0.2, 4096, 50],
        ["Bagaimana cara membuat Web API di ASP.NET Core?", "asp.netcore", 0.3, 2048, 50]
    ]
)

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860)