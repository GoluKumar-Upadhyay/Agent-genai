from flask import Flask, render_template, request
from utils.doc_validation import classify_and_extract
from flask import Flask, request, jsonify, render_template
from utils.doc_ner import redact_text


app = Flask(__name__)

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

@app.route("/validate", methods=["POST"])
def validate():
    category = request.form.get("category")
    file = request.files.get("document")

    if not file or not category:
        return jsonify({
            "error": "Missing file or category"
        }), 400

    # Call your existing function
    result = classify_and_extract(file, category)

    # Return JSON directly
    return jsonify(result)




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

if __name__ == "__main__":
    app.run(debug=True)
