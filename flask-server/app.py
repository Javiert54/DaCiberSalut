from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)

# Ensure the storage directory exists
os.makedirs("storage", exist_ok=True)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/upload_file")
def upload_file():
    return render_template("upload_file.html")

@app.route("/upload_file", methods=["POST"])
def handle_file_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        file_path = os.path.join("storage", file.filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

    return jsonify({"error": "File upload failed"}), 500

@app.route("/get_file/<file_name>")
def get_file(file_name):
    file_path = os.path.join("storage", file_name)
    if os.path.exists(file_path):
        return jsonify({"file_path": file_path}), render_template("get_file.html"), 200

    return jsonify({"error": "File not found"}), 404

@app.route("/get_file")
def get_files():
    files = os.listdir("storage")
    return render_template("get_file.html", files=files)