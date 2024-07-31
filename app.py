from flask import Flask, request, redirect, url_for, render_template_string
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Access the Azure Storage key from environment variables
azure_storage_key = os.getenv('AZURE_STORAGE_KEY')

# Ensure the key is loaded correctly
if not azure_storage_key:
    raise ValueError("AZURE_STORAGE_KEY environment variable not set")

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Connect to Azure Blob Service using the connection string
blob_service_client = BlobServiceClient.from_connection_string(azure_storage_key)
container_name = "forwebapp"
container_client = blob_service_client.get_container_client(container_name)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            blob_client = container_client.get_blob_client(filename)
            blob_client.upload_blob(file)
            return redirect(url_for('uploaded_file', filename=filename))
    return render_template_string('''
        <!doctype html>
        <title>Upload File</title>
        <h1>Upload File</h1>
        <form action="" method="post" enctype="multipart/form-data">
          <input type="file" name="file">
          <input type="submit" value="Upload">
        </form>
    ''')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return f'File uploaded: {filename}'

if __name__ == '__main__':
    app.run(debug=True)
