import gradio as gr
from query import ask

def handle_query(question):
    if not question.strip():
        return "Please enter a question.", ""
    
    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources

css = """
    #title {
        text-align: center;
        color: #2c3e50;
        font-size: 2.2em;
        font-weight: 700;
        margin-bottom: 0.2em;
    }
    #subtitle {
        text-align: center;
        color: #7f8c8d;
        font-size: 1em;
        margin-bottom: 1.5em;
    }
    #ask-btn {
        background-color: #2c3e50 !important;
        color: white !important;
        font-size: 1em !important;
        border-radius: 8px !important;
    }
    #answer-box {
        border-radius: 8px;
    }
    #sources-box {
        border-radius: 8px;
    }
"""

with gr.Blocks(title="The Unofficial Guide", css=css) as demo:

    gr.Markdown("<div id='title'>The Unofficial Guide</div>")
    gr.Markdown("<div id='subtitle'>Ask questions about Grinnell College professors — answers drawn from real student reviews.</div>")

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. Which professor has the most helpful office hours?",
            scale=5
        )

    btn = gr.Button("Ask", elem_id="ask-btn")

    gr.Markdown("### Example questions you can try:")
    with gr.Row():
        ex1 = gr.Button("Which professor has the most helpful office hours?")
        ex2 = gr.Button("Which professors are good for beginners in CS?")
        ex3 = gr.Button("What do students say about Collin Nolte's teaching style?")
        ex4 = gr.Button("Which professor focuses most on real-world applications?")

    with gr.Column():
        answer = gr.Textbox(
            label="Answer",
            lines=10,
            elem_id="answer-box"
        )
        sources = gr.Textbox(
            label="Retrieved from",
            lines=4,
            elem_id="sources-box"
        )

    # Button click
    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    # Example question buttons
    ex1.click(lambda: "Which professor has the most helpful office hours?", outputs=inp)
    ex2.click(lambda: "Which professors are good for beginners in CS?", outputs=inp)
    ex3.click(lambda: "What do students say about Collin Nolte's teaching style?", outputs=inp)
    ex4.click(lambda: "Which professor focuses most on real-world applications?", outputs=inp)

demo.launch()