from flask import Flask, render_template, request
from utils.doc_validation import classify_and_extract
from flask import Flask, request, jsonify, render_template



app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    # Just render the frontend HTML page
    return render_template("home.html")





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




