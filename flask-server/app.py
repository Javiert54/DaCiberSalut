from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import io
import mongoConnect
import torch
import torch.nn as nn
from torchvision import transforms
import torch.nn.functional as F
import json

app = Flask(__name__)

# Define the model class
class Model(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(Model, self).__init__()
        self.fc = nn.Linear(input_dim, output_dim)

    def forward(self, x):
        return self.fc(x)

def get_setup_json():
    # Read the setup configuration from a JSON file
    with open("../salutAI/setup.json", "r", encoding="utf-8") as f:
        setup_json = json.load(f)
    return setup_json
    
def save_image(file, format):
    # Save the converted image to a BytesIO object for further processing
    img = Image.open(file)
    output = io.BytesIO()
    img.save(output, format=format)
    output.seek(0)  # Rewind the BytesIO object

    # Generate a new filename with the original name and the new format
    new_filename = f"{os.path.splitext(file.filename)[0]}.{format.lower()}"
    file_path = os.path.join("static/storage", new_filename)

    # Save the converted file to the static/storage directory
    with open(file_path, "wb") as f:
        f.write(output.read())

    return new_filename

# Convert the uploaded image to the desired resolution
def change_resolution(image, resolution):
    """
    Converts the image to the specified resolution
    :param image: Image file
    :param resolution: Resolution to convert to (e.g., "512x512")
    :return: resized image
    """
    try:
        img = Image.open(image)

        # Get the X and Y resolution from the given resolution string
        X_resolution, Y_resolution = map(int, resolution.split("x"))

        # Resize the image to the specified resolution
        resized_img = img.resize(size=(X_resolution, Y_resolution))

        return resized_img

    except Exception as e:
        raise ValueError(f"Image conversion failed: {str(e)}")

# Function to analyze the image and make predictions using the model
def analyze_image(image, color_mode, output_dim):
    """
    This function predicts the type of image
    :param image: image to predict
    :param color_mode: color information to be used
    :param output_dim: number of output classes
    :return: the prediction
    """    
    # Define the transformations
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # These values are for RGB images
            std=[0.229, 0.224, 0.225]
        )
    ]) if color_mode == "IMREAD_COLOR" else transforms.Compose([
        transforms.Grayscale(num_output_channels=1),  # Convert to grayscale
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5], std=[0.5])  # Use values that are suitable for grayscale
    ])

    # Apply transformations and add batch dimension (1, C, H, W)
    input_tensor = transform(image).unsqueeze(0)

    # Flatten the tensor if your model doesn't do it internally
    input_flat = input_tensor.view(1, -1)

    # Initialize the model
    input_dim = image.size[0] * image.size[1]
    model = Model(input_dim, output_dim)
    model.load_state_dict(torch.load("../salutAI/model_trained.pth"))
    model.eval()

    # Get the prediction from the model
    with torch.no_grad():  # Don't compute gradients during inference
        result = model(input_flat)

    probabilities = F.softmax(result, dim=1)
    percentages = probabilities.squeeze().tolist()
    percentages = [round(p * 100, 2) for p in percentages]

    prediction = {}
    setup = get_setup_json()
    dirs = setup['dirs']

    for i in range(len(percentages)):
        dir = dirs[f'{i}']
        label = dir.split("/")[-1]
        label_name = setup['labels_names'][label]
        prediction[label_name] = percentages[i]

    print(prediction)
    return prediction

# Ensure the storage directory exists
os.makedirs("static/storage", exist_ok=True)

# Route to render the home page
@app.route("/")
def home():
    return render_template("home.html")

# Route to render the page to get files
@app.route("/get_files_page")
def get_file_page():
    return render_template("get_files.html")

# Route to render the upload file page
@app.route("/analyze_image_page")
def analyze_image_page():
    return render_template("analyze_image.html")

# Route to handle file upload and prediction
@app.route("/analyze_image_api", methods=["POST"])
def analyze_image_api():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file:
        try:
            setup = get_setup_json()
            X_resolution_size, Y_resolution_size = setup['X_resolution_size'], setup['Y_resolution_size']
            color_mode = setup['color_mode']
            output_dim = setup['output_dim']

            resized_img = change_resolution(file, f"{X_resolution_size}x{Y_resolution_size}")
            prediction = analyze_image(resized_img, color_mode, output_dim)

            # Save the image in the storage directory
            new_filename = save_image(file, "JPEG")

            # Upload the document to MongoDB
            document = {
                "file_name": new_filename,
                "prediction": prediction
            }
            mongoConnect.upload2DB(document)
            return jsonify({"message": "The image was analyzed and uploaded successfully"}), 200
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File upload failed"}), 500

# Route to get file by its ID from the database
@app.route("/get_files/<document_id>")
def get_files(document_id):
    try:
        documentID = document_id.document_id
        print(f"Getting file with ID: {documentID}")
        document = mongoConnect.getDocument(documentID)

        if document:
            file_path = "storage/" + document.get("file_name", "")
            print(f"Document found: {document}")
            print(f"File path: {file_path}")

            if os.path.exists(os.path.join("static", file_path)):
                print("File found in static/storage directory.")
                return jsonify({"filepath": "static/"+file_path})
            else:
                print("File not found in static/storage directory.")
                return jsonify({"error": "File not found in static/storage"}), 404
        else:
            print("Document not found in database.")
            return jsonify({"error": "Document not found in database"}), 404
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# Route to get data for all uploaded files
@app.route("/get_file_data")
def get_file_data():
    try:
        documents = mongoConnect.getDocument()
        files = [{"file_name": doc["file_name"], "file_id": str(doc["_id"]), "file_prediction": str(doc["prediction"])} for doc in documents]
        return jsonify({"files": files}), 200
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

# API route to handle image analysis from POST request
@app.route("/re_analyze_image", methods=["POST"])
def re_analyze_image():
    setup = get_setup_json()
    try:
        # Get the image data from the request
        imgSrc = request.get_json()['imgSrc']  # Assuming imgSrc is the image in base64 or binary form
        converted_image = change_resolution(io.BytesIO(imgSrc), "512x512")  # Convert image to 512x512
        result = analyze_image(converted_image, "RGB", 5)  # Example color and output dimension
        return jsonify({"prediction": result.item()})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)