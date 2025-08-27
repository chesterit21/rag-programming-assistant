import gradio as gr
from rag_chain import query_rag
import re
import os
from typing import List
import datetime

def chat_interface(message: str, history: List[List[str]], category: str, temperature: float, max_tokens: int, gpu_layers: int):
    """Fungsi utama untuk interaksi chatbot, mengelola state dan streaming."""
    history = history or []
    history.append([message, ""])
    # Langsung kosongkan input box dan perbarui history
    yield history, "", history

    # Riwayat yang dikirim ke RAG tidak menyertakan giliran saat ini
    history_for_rag = history[:-1]
    
    response_generator = query_rag(
        question=message,
        chat_history=history_for_rag,
        temperature=temperature,
        max_tokens=max_tokens,
        gpu_layers=gpu_layers
    )

    # Streaming respons dari generator
    for chunk in response_generator:
        if "✍️ Menghasilkan jawaban..." in chunk:
            response_text = chunk.split("✍️ Menghasilkan jawaban...\n\n")[-1]
            history[-1][1] = response_text
        else:
            history[-1][1] = f"*({chunk})*"
        
        # Terus perbarui chatbot dan state history
        yield history, "", history

def save_as_txt(chat_history: List[List[str]], category: str):
    """Menyimpan seluruh riwayat percakapan ke dalam file teks."""
    # Debugging print statement
    print(f"DEBUG: History received by save_as_txt: {chat_history}")

    if not chat_history:
        return "Tidak ada percakapan untuk disimpan."

    if not chat_history[-1][1] or "*(" in chat_history[-1][1]:
        return "Gagal menyimpan: Jawaban terakhir belum selesai."

    first_question = chat_history[0][0]
    summary = '-'.join(first_question.lower().split()[:5])
    base_filename = re.sub(r'[^a-z0-9-]', '', summary) or "percakapan"
    
    category = category or "general"
    category_slug = re.sub(r'[\s/\\:*?"<>|]', '-', category.lower())
    docs_path = "docs"
    category_path = os.path.join(docs_path, category_slug)
    os.makedirs(category_path, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.txt"
    file_path = os.path.join(category_path, filename)

    formatted_conversation = f"# Topik Percakapan: {first_question}\n"
    formatted_conversation += f"## Kategori: {category}\n\n"
    
    for i, (user_msg, ai_msg) in enumerate(chat_history):
        formatted_conversation += f"--- Giliran Ke-{i+1} ---\n"
        formatted_conversation += f"Pengguna: {user_msg}\n\n"
        formatted_conversation += f"Asisten: {ai_msg}\n\n"

    with open(file_path, "w", encoding='utf-8') as f:
        f.write(formatted_conversation)
        
    return f"Percakapan disimpan ke {file_path}"

with gr.Blocks(theme=gr.themes.Soft(), title="SFCore Assistant") as iface:
    gr.Markdown("# SFCore Assistant\nAsisten Pemrograman dengan RAG, Ollama, dan Memori Percakapan")
    
    with gr.Row():
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Chat", elem_id="chatbot", height=600, show_label=False)
            with gr.Row():
                msg_box = gr.Textbox(
                    label="Pesan", 
                    placeholder="Ketik pertanyaan Anda di sini...",
                    lines=4,
                    scale=8,
                    show_label=False,
                )
                submit_btn = gr.Button("Kirim", variant="primary", scale=1, min_width=150)
            gr.Markdown("<small>Tekan Ctrl+Enter untuk mengirim pesan.</small>")

        with gr.Column(scale=1):
            gr.Markdown("### Konfigurasi")
            category = gr.Textbox(label="Kategori Konteks", placeholder="e.g., csharp, oop, ddd")
            save_btn = gr.Button("Simpan Seluruh Percakapan", variant="secondary")
            save_status = gr.Textbox(label="Status Simpan", interactive=False)
            
            with gr.Accordion("Pengaturan Lanjutan", open=False):
                temperature = gr.Slider(0, 1, value=0.2, label="Temperature")
                max_tokens = gr.Slider(128, 8192, value=4096, label="Max Tokens")
                gpu_layers = gr.Slider(0, 100, value=35, label="GPU Layers")
            
            clear_btn = gr.ClearButton([msg_box, chatbot], value="Mulai Percakapan Baru")

    # State untuk menyimpan riwayat percakapan
    chat_history = gr.State([])

    # Kumpulkan semua input untuk efisiensi
    common_inputs = [msg_box, chat_history, category, temperature, max_tokens, gpu_layers]
    # Tentukan output untuk fungsi chat, sekarang termasuk chat_history
    chat_outputs = [chatbot, msg_box, chat_history]

    # Hubungkan event ke fungsi
    submit_btn.click(
        fn=chat_interface,
        inputs=common_inputs,
        outputs=chat_outputs
    )
    msg_box.submit(
        fn=chat_interface,
        inputs=common_inputs,
        outputs=chat_outputs
    )
    
    save_btn.click(
        fn=save_as_txt, 
        inputs=[chat_history, category],
        outputs=save_status
    )

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7865, share=False)