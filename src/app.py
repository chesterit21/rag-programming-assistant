import gradio as gr
from rag_chain import query_rag
import re
import os
from typing import List
import datetime
import csv

FEEDBACK_FILE = os.path.join(os.path.dirname(__file__), "..", "feedback_log.csv")

def handle_feedback(feedback: gr.LikeData, history: List[List[str]]):
    """Mencatat feedback (suka/tidak suka) dari pengguna ke dalam file CSV."""
    # feedback.index adalah tuple (row_index, 0 atau 1). Kita butuh row_index.
    row_index = feedback.index[0]

    if not history or row_index >= len(history):
        return "Gagal mencatat feedback: riwayat tidak cocok."

    user_msg, ai_msg = history[row_index]
    feedback_type = "👍 SUKA" if feedback.liked else "👎 TIDAK SUKA"

    if not ai_msg or "*(" in ai_msg:
        return "Silakan tunggu respons selesai sebelum memberikan feedback."

    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)
    file_exists = os.path.isfile(FEEDBACK_FILE)
    with open(FEEDBACK_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "feedback_type", "user_question", "ai_response"])
        timestamp = datetime.datetime.now().isoformat()
        writer.writerow([timestamp, feedback_type, user_msg, ai_msg])
    return f"Feedback diterima: {feedback_type}"

def chat_interface(message: str, history: List[List[str]], temperature: float, max_tokens: int, gpu_layers: int):
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
    history_to_save = list(chat_history)

    if not history_to_save:
        return "Tidak ada percakapan untuk disimpan."

    # Periksa giliran terakhir. Jika jawaban AI belum selesai (streaming) atau kosong,
    # kita ganti dengan pesan placeholder agar pertanyaan pengguna tetap tersimpan.
    last_user_msg, last_ai_msg = history_to_save[-1]
    if not last_ai_msg or "*(" in last_ai_msg:
        history_to_save[-1] = [last_user_msg, "[Jawaban Asisten belum selesai atau tidak ada]"]

    # Filter keluar giliran yang pertanyaannya kosong (seharusnya tidak terjadi, tapi untuk keamanan)
    history_to_save = [turn for turn in history_to_save if turn[0]]
    
    first_question = history_to_save[0][0]
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
    
    for i, (user_msg, ai_msg) in enumerate(history_to_save):
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
            chatbot = gr.Chatbot(label="Chat", elem_id="chatbot", height=600, show_label=False, likeable=True)
            with gr.Row():
                msg_box = gr.Textbox(
                    label="Pesan", 
                    placeholder="Ketik pertanyaan Anda di sini...",
                    lines=3,
                    scale=7,
                    show_label=False,
                )
                submit_btn = gr.Button("Kirim", variant="primary", scale=1, min_width=120)
                stop_btn = gr.Button("Berhenti", variant="stop", scale=1, min_width=120)
            gr.Markdown("<small>Tekan Ctrl+Enter untuk mengirim pesan.</small>")

        with gr.Column(scale=1):
            gr.Markdown("### Konfigurasi")
            category = gr.Textbox(label="Kategori Konteks", placeholder="e.g., csharp, oop, ddd")
            save_btn = gr.Button("Simpan Seluruh Percakapan", variant="secondary")
            save_status = gr.Textbox(label="Status Simpan", interactive=False)
            
            gr.Markdown("### Feedback")
            feedback_status = gr.Textbox(label="Status Feedback", interactive=False)
            
            with gr.Accordion("Pengaturan Lanjutan", open=False):
                temperature = gr.Slider(0, 1, value=0.2, label="Temperature")
                max_tokens = gr.Slider(128, 8192, value=4096, label="Max Tokens")
                gpu_layers = gr.Slider(0, 100, value=35, label="GPU Layers")
            
            clear_btn = gr.ClearButton([msg_box, chatbot], value="Mulai Percakapan Baru")

    # State untuk menyimpan riwayat percakapan
    chat_history = gr.State([])

    # Kumpulkan semua input untuk efisiensi
    common_inputs = [msg_box, chat_history, temperature, max_tokens, gpu_layers]
    # Tentukan output untuk fungsi chat, sekarang termasuk chat_history
    chat_outputs = [chatbot, msg_box, chat_history]

    # Hubungkan event ke fungsi
    # Event untuk mengirim pesan, dibuat bisa dibatalkan (cancellable)
    submit_event = submit_btn.click(
        fn=chat_interface,
        inputs=common_inputs,
        outputs=chat_outputs
    )
    msg_event = msg_box.submit(
        fn=chat_interface,
        inputs=common_inputs,
        outputs=chat_outputs
    )

    # Event untuk tombol berhenti, yang akan membatalkan event pengiriman
    stop_btn.click(
        fn=None,
        cancels=[submit_event, msg_event]
    )
    
    save_btn.click(
        fn=save_as_txt, 
        inputs=[chat_history, category],
        outputs=save_status
    )

    chatbot.like(
        fn=handle_feedback,
        inputs=[chat_history],
        outputs=[feedback_status]
    )

if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7865, share=False)