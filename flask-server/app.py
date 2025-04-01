from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import io
import json
import mongoConnect

app = Flask(__name__)

# Ensure the storage directory exists
os.makedirs("static/storage", exist_ok=True)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/get_files")
def get_file_page():
    return render_template("get_files.html")

@app.route("/upload_file")
def upload_file_page():
    return render_template("upload_file.html")

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
        converted_file, imageFormat = convert_image(file)  # Convert the image to 768x768 JPEG
        print(f"File converted: {type(converted_file)}")
        
        try:
            prediction = predict(converted_file)  # Call the predict function with the converted file
            
            # Generate a new filename with the original name and the new format
            new_filename = f"{original_filename}.{imageFormat.lower()}"
            file_path = os.path.join("static/storage", new_filename)

            # Save the converted file to the static/storage directory
            with open(file_path, "wb") as f:
                f.write(converted_file.read())

            # Create a document to upload to MongoDB
            document = {
                "file_name": new_filename,
                "prediction": prediction["label"],
                "confidence": prediction["confidence"]
            }

            # Upload the document to MongoDB
            mongoConnect.upload2DB(document)

            return jsonify({"message": "File uploaded successfully to \"static/storage/\"", "file_path": new_filename}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File upload failed"}), 500


@app.route("/get_files/<document_id>")
def get_files(document_id):
    try:
        print(f"Getting file with ID: {document_id}")
        document = mongoConnect.getDocument(document_id)

        if document:
            file_path = "storage/" + document.get("file_name", "")
            print(f"Document found: {document}")
            print(f"File path: {file_path}")

            if os.path.exists(os.path.join("static", file_path)):
                print("File found in static/storage directory.")
                return render_template("display_image.html", file_path=file_path)
            else:
                print("File not found in static/storage directory.")
                return jsonify({"error": "File not found in static/storage"}), 404
        else:
            print("Document not found in database.")
            return jsonify({"error": "Document not found in database"}), 404
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/get_file_data")
def get_file_data():
    try:
        documents = mongoConnect.getDocument()
        files = [{"file_name": doc["file_name"], "file_id": str(doc["_id"])} for doc in documents]
        return jsonify({"files": files}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

def convert_image(file, resolution="768x768", changeResolution=False, changeFormat=True, format="JPEG"):
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
        print(f"converting image to {resolution} {file.filename.split('.')[-1]}")
        if changeResolution:
            img = img.resize((width, height), Image.ANTIALIAS)
        if changeFormat:
            output = io.BytesIO()
            img.save(output, format=format)
            output.seek(0)
            # print(f"Image converted to {resolution} {format}")
            return output, format
        return img, file.filename.split(".")[-1]
    except Exception as e:
        raise ValueError(f"Image conversion failed: {str(e)}")

def predict(image):
    """
    This function predicts the type of image
    :param image: image to predict
    :return: the prediction
    """
    model = tf.keras.models.load_model('../salutAI/model.h5')
    prediction = model.predict(image)
    return prediction