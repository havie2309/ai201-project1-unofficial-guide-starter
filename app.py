import gradio as gr
from query import ask

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

with gr.Blocks(title="The Unofficial Guide") as demo:
    gr.Markdown("""
    # 🎓 The Unofficial Guide
    Ask questions about professors at Grinnell College based on real student reviews.
    """)
    
    inp = gr.Textbox(
        label="Your question",
        placeholder="e.g. Which professor has the most helpful office hours?"
    )
    btn = gr.Button("Ask", variant="primary")
    
    with gr.Row():
        answer = gr.Textbox(label="Answer", lines=8)
        sources = gr.Textbox(label="Retrieved from", lines=8)
    
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

demo.launch()