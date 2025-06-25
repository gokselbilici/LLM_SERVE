import gradio as gr
import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
API_URL = "http://localhost:9999/generate"
DEFAULT_MODEL = os.getenv("MODEL_NAME", "qwen3:0.6b")

def get_available_models():
    fallback_models = ["qwen3:0.6b", "qwen2.5:0.5b"]
    for _ in range(5):
        try:
            res = requests.get(f"{API_URL}/models", timeout=3)
            if res.status_code == 200:
                model_data = res.json()
                return [m["name"] for m in model_data.get("models", [])]
        except:
            time.sleep(2)
    return fallback_models


def chat(prompt, model=DEFAULT_MODEL, stream=False):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    response = requests.post(API_URL, json=payload, stream=stream)
    if stream:
        output = ""
        for line in response.iter_lines():
            if line:
                output += line.decode("utf-8") + "\n"
        return output
    else:
        return response.json().get("response", "[No response]")
    
def pull_model(model_name):
    res = requests.post("http://localhost:9999/pull", json={"name": model_name})
    return f"Pulled model: {model_name}" if res.status_code == 200 else res.text

with gr.Blocks() as demo:
    gr.Markdown("### 🧠 Local Ollama Chat (via FastAPI)")

    with gr.Row():
        prompt_box = gr.Textbox(label="Your prompt")
        model_dropdown = gr.Dropdown(choices=get_available_models(), value=DEFAULT_MODEL, label="Model")
        stream_toggle = gr.Checkbox(value=True, label="Stream")

    output_box = gr.Textbox(label="Model Response")
    pull_result = gr.Textbox(label="Model Pull Status")

    with gr.Row():
        send_btn = gr.Button("Generate")
        pull_btn = gr.Button("Pull Selected Model")

    send_btn.click(chat, inputs=[prompt_box, model_dropdown, stream_toggle], outputs=output_box)
    pull_btn.click(pull_model, inputs=[model_dropdown], outputs=pull_result)

demo.launch()