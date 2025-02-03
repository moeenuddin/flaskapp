import os
import pika
from flask import Flask, request, jsonify

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
    print("Image reducer v1.0")
    
@app.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        
        # Publish message to RabbitMQ
        channel.basic_publish(exchange="", routing_key="image_resize", body=filepath)
        return jsonify({"message": "File uploaded and processing started!"})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
