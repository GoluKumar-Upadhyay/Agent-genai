from flask import Flask, request, jsonify
import re
from transformers import pipeline
import os
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify

# Load Hugging Face token from .env
load_dotenv()
HF_TOKEN = os.getenv("HUGGING_FACE_API_KEY")

# Login to Hugging Face
from huggingface_hub import login
login(token=HF_TOKEN)

# Initialize Flask
app = Flask(__name__)

# --- Load NER Models ---
print("Loading IndicNER model (ai4bharat/IndicNER)...")
indic_ner = pipeline("ner", model="ai4bharat/IndicNER", aggregation_strategy="simple")
print("IndicNER loaded.")

print("Loading English NER model (dslim/bert-base-NER)...")
en_ner = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
print("English NER loaded.")

# --- Regex Patterns for Phase 1 ---
regex_patterns = {
    r"\b\d{10}\b": "[REDACTED_PHONE]",
    r"\b\d{4}\s?\d{4}\s?\d{4}\b": "[REDACTED_AADHAR]",
    r"\b\d{5}/\d{2}\b": "[REDACTED_REG_NO]",
    r"\b\d{2}/\d{2}/\d{4}\b": "[REDACTED_DATE]",
    r"\b\d{3,5}\b": "[REDACTED_NUMBER]",
}

# --- Helper function to redact text ---
def redact_text(text):
    # Phase 1: Regex
    redacted_text = text
    for pattern, replacement in regex_patterns.items():
        redacted_text = re.sub(pattern, replacement, redacted_text)

    # Phase 2: NER
    indic_entities = indic_ner(redacted_text)
    en_entities = en_ner(redacted_text)
    all_entities = indic_entities + en_entities

    pii_entities = [e for e in all_entities if e['entity_group'] in ['PER', 'LOC']]
    pii_entities.sort(key=lambda x: x['start'], reverse=True)

    final_text_list = list(redacted_text)
    for entity in pii_entities:
        start, end = entity['start'], entity['end']
        label = entity['entity_group']
        replacement_tag = f"[REDACTED_{label}]"
        final_text_list[start:end] = list(replacement_tag)

    return "".join(final_text_list)


# --- Flask Routes ---

@app.route("/", methods=["GET"])
def home():
    # Just render the frontend HTML page
    return render_template("home.html")

@app.route('/upload',methods=["GET"])
def doc_upload_validate():
    return render_template('doc_upload_validate.html')

@app.route('/ner',methods=["GET"])
def ner_masking():
    return render_template('ner.html')




@app.route("/redact", methods=["POST"])
def redact_api():
    try:
        text = ""
        if request.is_json:
            data = request.get_json()
            text = data.get("text", "")
        else:
            text = request.data.decode("utf-8")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        redacted = redact_text(text)
        return jsonify({"redacted_text": redacted})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=True)

