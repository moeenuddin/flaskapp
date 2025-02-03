import os
import pika
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CloudAMQP connection
AMQP_URL = "amqps://hfwdoxdg:1aeRZiQ9lXXeWwlFioDsGMCqNAfi_4sU@campbell.lmq.cloudamqp.com/hfwdoxdg" #"your_cloudamqp_url"
#params = pika.URLParameters(AMQP_URL)
#connection = pika.BlockingConnection(params)
#channel = connection.channel()
#channel.queue_declare(queue="image_resize")

def list_files(path):
    # Check if the path exists
    if os.path.exists(path):
        # Iterate over the files and directories in the given path
        for root, dirs, files in os.walk(path):
            for file in files:
                print(os.path.join(root, file))
    else:
        print("The provided path does not exist.")

def get_rabbitmq_connection():
    try:
        params = pika.URLParameters(AMQP_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        return connection, channel
    except Exception as e:
        print(f"Error connecting to RabbitMQ: {e}")
        return None, None

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
        filepath = os.path.join(uploads_dir, file.filename) # caps 
        file.save(filepath)
        list_files(uploads_dir)

        connection, channel = get_rabbitmq_connection()
        channel.queue_declare(queue="image_resize")
        if connection is None or channel is None:
            return jsonify({"error": "Failed to connect to RabbitMQ"}), 500
        
        # Publish message to RabbitMQ
        channel.basic_publish(exchange="", routing_key="image_resize", body=filepath)
        connection.close()  # Close after use
        return jsonify({"message": "File uploaded and processing started!"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
