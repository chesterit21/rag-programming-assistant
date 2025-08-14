import gradio as gr
from rag_chain import query_rag
import json
import datetime
import re

def ask_question(question, category, temperature, max_tokens, gpu_layers):
    # Panggil fungsi RAG dan teruskan parameter secara langsung
    yield from query_rag(
        question=question,
        category=category,
        temperature=temperature,
        max_tokens=max_tokens,
        gpu_layers=gpu_layers
    )

def save_as_txt(question, answer, category):
    # Create a summary from the question
    summary = '-'.join(question.lower().split()[:5])
    summary = re.sub(r'[^a-z0-9-]', '', summary)
    
    # Sanitize category
    category_slug = re.sub(r'\s+', '-', category.lower())
    category_slug = re.sub(r'[^a-z0-9-]', '', category_slug)

    filename = f"{category_slug}-{summary}.txt"
    with open(filename, "w") as f:
        f.write(f"# Title: {question}\n\n")
        f.write(f"## Category: {category}\n\n")
        f.write(f"### Answer\n\n{answer}")
    return f"Saved to {filename}"

def save_as_json(question, answer, category):
    # Generate document_id from question
    document_id = re.sub(r'\s+', '-', question.lower())
    document_id = re.sub(r'[^a-z0-9-]', '', document_id)

    # Parse markdown answer into chunks
    chunks = []
    lines = answer.split('\n')
    heading = "Introduction"
    content = ""

    # Check for initial content before the first heading
    first_heading_index = -1
    for i, line in enumerate(lines):
        if line.startswith('## '):
            first_heading_index = i
            break
    
    if first_heading_index > 0:
        initial_content = "\n".join(lines[:first_heading_index]).strip()
        if initial_content:
            chunks.append({"heading": heading, "content": initial_content})
    
    # Process content from the first heading onwards
    if first_heading_index != -1:
        lines = lines[first_heading_index:]

    heading_found = False
    for line in lines:
        if line.startswith('## '):
            if content.strip() and heading_found:
                chunks.append({"heading": heading, "content": content.strip()})
            heading = line.replace('## ', '').strip()
            content = ""
            heading_found = True
        else:
            content += line + '\n'
    
    if content.strip() and heading_found:
        chunks.append({"heading": heading, "content": content.strip()})
    elif not chunks:
        # Handle case where there are no headings
        chunks.append({"heading": "Content", "content": answer.strip()})


    data = {
        "document_id": document_id,
        "title": question,
        "category": category,
        "chunks": chunks
    }

    filename = f"{document_id}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    return f"Saved to {filename}"

with gr.Blocks(theme=gr.themes.Soft(), title="RAG Programming Assistant") as iface:
    gr.Markdown("# RAG Programming Assistant\nAsisten Programming dengan RAG dan Ollama")
    with gr.Row():
        with gr.Column(scale=1):
            question = gr.Textbox(label="Pertanyaan", lines=5, placeholder="Ajukan pertanyaan teknis...")
            category = gr.Textbox(label="Kategori (opsional)", placeholder="ddd, asp.netcore, dll.")
            with gr.Accordion("Pengaturan Lanjutan", open=False):
                temperature = gr.Slider(0, 1, value=0.2, label="Temperature")
                max_tokens = gr.Slider(128, 8192, value=4096, label="Max Tokens")
                gpu_layers = gr.Slider(0, 100, value=35, label="GPU Layers")
            with gr.Row():
                submit_btn = gr.Button("Kirim", variant="primary")
                clear_btn = gr.ClearButton()


        with gr.Column(scale=2):
            answer = gr.Markdown(label="Jawaban", elem_id="chatbot")
            with gr.Row():
                save_txt_btn = gr.Button("Save as TXT")
                save_json_btn = gr.Button("Save as JSON")
            save_status = gr.Textbox(label="Status", interactive=False)


    # Hubungkan tombol ke fungsi
    submit_btn.click(
        fn=ask_question,
        inputs=[question, category, temperature, max_tokens, gpu_layers],
        outputs=answer
    )
    
    save_txt_btn.click(fn=save_as_txt, inputs=[question, answer, category], outputs=save_status)
    save_json_btn.click(fn=save_as_json, inputs=[question, answer, category], outputs=save_status)
    
    clear_btn.click(lambda: [None, None, None], outputs=[question, answer, save_status])


if __name__ == "__main__":
    iface.launch(server_name="0.0.0.0", server_port=7860, share=False)
