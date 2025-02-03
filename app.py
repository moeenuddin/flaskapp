import os
import pika
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CloudAMQP connection
AMQP_URL = "amqps://hfwdoxdg:1aeRZiQ9lXXeWwlFioDsGMCqNAfi_4sU@campbell.lmq.cloudamqp.com/hfwdoxdg" #"your_cloudamqp_url"
params = pika.URLParameters(AMQP_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="image_resize")

@app.route("/",methods=["GET"])
def index():
    return render_template("index.html") #"Image reducer v1.0"
    
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    # Define your file save path
    filepath = "uploads"  # Replace with actual file path

    # Check if the file path exists
    if os.path.exists(filepath):
        print(f"File path exists: {filepath}")

    # Check for root directory
    root_dir = os.path.abspath(os.sep)  # Root directory (usually '/')
    print(f"Root Directory: {root_dir}")

    # Check for app directory (assuming it's the directory of the current script)
    app_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"App Directory: {app_dir}")

    # Check for uploads directory (adjust the path accordingly)
    uploads_dir = os.path.join(app_dir, "uploads")
    if os.path.exists(uploads_dir):
        print(f"Uploads Directory exists: {uploads_dir}")
    else:
        print(f"Uploads Directory does not exist")

    # Assuming file save code is here
    # file.save(filepath)
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Publish message to RabbitMQ
        channel.basic_publish(exchange="", routing_key="image_resize", body=filepath)
        return jsonify({"message": "File uploaded and processing started!"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
