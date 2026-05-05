from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

app = Flask(__name__)
CORS(app)

MODEL_NAME = "Qwen/Qwen2-0.5B"
tokenizer = None
model = None


def load_model():
    global tokenizer, model
    print(f"Loading model {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float32,
        device_map="auto",
    )
    model.eval()
    print("Model loaded successfully.")


def build_prompt(text: str) -> str:
    return (
        "Translate from Spanish to Italian.\n"
        "Spanish: Me llamo Juan. Italian: Mi chiamo Juan.\n"
        "Spanish: Buenos días. Italian: Buongiorno.\n"
        "Spanish: ¿Dónde está el baño? Italian: Dov'è il bagno?\n"
        f"Spanish: {text} Italian:"
    )


def extract_translation(generated: str, prompt: str) -> str:
    # Strip the prompt prefix from the generated text
    if generated.startswith(prompt):
        generated = generated[len(prompt):]
    # Take only the first line (stops at newline or next "Spanish:")
    first_line = re.split(r"\n|Spanish:", generated)[0]
    return first_line.strip()


@app.route("/health", methods=["GET"])
def health():
    if model is None:
        return jsonify({"status": "loading", "message": "Model not ready yet"}), 503
    return jsonify({"status": "ok", "model": MODEL_NAME})


@app.route("/translate", methods=["POST"])
def translate():
    if model is None:
        return jsonify({"error": "Model is not loaded yet. Please try again in a moment."}), 503

    data = request.get_json(silent=True)
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text' field in request body."}), 400

    text = data["text"].strip()
    if not text:
        return jsonify({"error": "The 'text' field cannot be empty."}), 400
    if len(text) > 500:
        return jsonify({"error": "Text is too long. Maximum 500 characters allowed."}), 400

    try:
        prompt = build_prompt(text)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=80,
                do_sample=False,
                temperature=1.0,
                repetition_penalty=1.3,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id,
            )

        new_tokens = outputs[0][input_len:]
        generated = tokenizer.decode(new_tokens, skip_special_tokens=True)
        translation = extract_translation(generated, "")

        if not translation:
            return jsonify({"error": "The model could not produce a translation. Try rephrasing the input."}), 500

        return jsonify({"translation": translation})

    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500


if __name__ == "__main__":
    load_model()
    app.run(host="0.0.0.0", port=5000, debug=False)
