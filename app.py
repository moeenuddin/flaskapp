import os
import pika
from flask import Flask, request, jsonify, render_template

import mysql.connector
from mysql.connector import Error
from urllib.parse import urlparse

# Get the MySQL URL from environment variables
mysql_url = os.getenv("MYSQL_URL")
print(f" url : {MYSQL_URL}")

if mysql_url:
    try:
        # Parse the MySQL URL
        parsed_url = urlparse(mysql_url)

        # Extract MySQL connection details
        mysql_config = {
            "host": parsed_url.hostname,
            "port": parsed_url.port or 3306,  # Default MySQL port
            "user": parsed_url.username,
            "password": parsed_url.password,
            "database": parsed_url.path.lstrip("/"),  # Remove leading "/"
        }

        # Establish the connection
        connectionDB = mysql.connector.connect(**mysql_config)

        if connectionDB.is_connected():
            print("Connected to MySQL successfully!")
            cursor = connectionDB.cursor()

            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255),
                    data LONGBLOB
                )
            """)

            #connectionDB.close()
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
else:
    print("MYSQL_URL environment variable is not set.")



app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Function to save image
def save_image(image_path):
    with open(image_path, "rb") as file:
        binary_data = file.read()
    
    sql = "INSERT INTO images (name, data) VALUES (%s, %s)"
    cursor = connectionDB.cursor()
    cursor.execute(sql, (image_path, binary_data))
    connectionDB.commit()
    print(f"Image '{image_path}' saved successfully.")


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
        # Example Usage
        save_image(filepath)
        # Close Connection
        cursor.close()
        conn.close()


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
