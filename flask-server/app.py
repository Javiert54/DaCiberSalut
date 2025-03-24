from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import io
import json
import mongoConnect

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


def convert_image(file, resolution="768x768", changeResolution=False, changeFormat=True):
    """
    This function converts the image to the specified resolution
    :param file: file to convert
    :param resolution: resolution to convert to
    :return: the converted image file
    """
    try:
        width, height = map(int, resolution.split("x"))
        img = Image.open(file)
        img = img.convert("RGB")
        if changeResolution:
            img = img.resize((width, height), Image.ANTIALIAS)
        if changeFormat:
            output = io.BytesIO()
            img.save(output, format="JPEG")
            output.seek(0)
            return output
        return img
    except Exception as e:
        raise ValueError(f"Image conversion failed: {str(e)}")


@app.route("/upload_file", methods=["POST"])
def handle_file_upload():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:

        # Get the original filename before conversion
        original_filename = os.path.splitext(file.filename)[0]
        
        # Convert the file
        converted_file = convert_image(file)  # Convert the image to 768x768 JPEG
        print(f"File converted: {type(converted_file)}")
        
        # Define a new filename for the converted file
        new_filename = f"{original_filename}.jpeg"
        file_path = os.path.join("storage", new_filename)
        
        # Save the converted file
        with open(file_path, "wb") as f:
            f.write(converted_file.read())
        document= {"file_path": file_path, "file_name": new_filename}
        print(document)
        mongoConnect.upload2DB(document)
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
    files = mongoConnect.getDocument()
    return render_template("get_file.html", files=files)