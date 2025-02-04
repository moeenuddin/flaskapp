import pika
from PIL import Image
import os
import mysql.connector
from mysql.connector import Error
import io

# CloudAMQP connection
AMQP_URL = "amqps://hfwdoxdg:1aeRZiQ9lXXeWwlFioDsGMCqNAfi_4sU@campbell.lmq.cloudamqp.com/hfwdoxdg" #"your_cloudamqp_url"
params = pika.URLParameters(AMQP_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="image_resize")

app_dir = os.path.dirname(os.path.abspath(__file__))
print(f"App Directory: {app_dir}")

OUTPUT_FOLDER = "processed_images"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Database connection details (modify or fetch from environment)
mysql_url = os.getenv("MYSQL_URL")


def get_db_connection():
    """Establish a database connection using MYSQL_URL."""
    from urllib.parse import urlparse

    if not mysql_url:
        raise ValueError("MYSQL_URL environment variable is not set.")

    parsed_url = urlparse(mysql_url)

    return mysql.connector.connect(
        host=parsed_url.hostname,
        port=parsed_url.port or 3306,
        user=parsed_url.username,
        password=parsed_url.password,
        database=parsed_url.path.lstrip("/")
    )



def retrieve_blob_and_save(image_id, output_path, new_size=(200, 200)):
    """Retrieve image blob from MySQL, convert it to an image, resize, and save locally."""
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve the image BLOB from MySQL
        query = "SELECT image_blob FROM images_table WHERE id = %s"
        cursor.execute(query, (image_id,))
        result = cursor.fetchone()

        if result is None:
            print(f"No image found for ID {image_id}")
            return
        
        image_blob = result[0]

        # Convert BLOB to image
        image = Image.open(io.BytesIO(image_blob))

        # Resize image
        image_resized = image.resize(new_size)

        # Ensure the output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Save image locally
        image_resized.save(output_path, format="JPEG")

        print(f"Image saved at: {output_path}")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def process_image(ch, method, properties, body):
    filepath = body.decode() # "uploads/filename.jpeg"
    uploads_dir_filepath = os.path.join(app_dir, filepath)
    uploads_dir = os.path.join(app_dir, "uploads")
    print(f"App file path: {uploads_dir_filepath}")
    if os.path.exists(uploads_dir):
        print(f"Uploads Directory exists: {uploads_dir}")
    else:
        print(f"Uploads Directory does not exist")
    # Check if the path exists
    uploads_dir = "/var/lib/containers/railwayapp/bind-mounts/626efc24-bacc-44b3-9d5b-b3cd3ff77d88/vol_qodjv4vgxlsj33kt"
    if os.path.exists(uploads_dir):
        # Iterate over the files and directories in the given path
        for root, dirs, files in os.walk(uploads_dir):
            for file in files:
                print(os.path.join(root, file))
    else:
        print("The provided path does not exist.")
    
    
    # Example usage
    retrieve_blob_and_save(image_id=1, output_path="processed_images/"+os.path.basename(filepath))

    #img = Image.open(uploads_dir_filepath) #filepath
    #img = img.resize((200, 200))  # Resize image to 200x200
    #output_path = os.path.join(OUTPUT_FOLDER, os.path.basename(filepath))
    #print(f"Output directory path: {output_path}")
    #img.save(output_path)
    #print(f"Processed: {output_path}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue="image_resize", on_message_callback=process_image)
print("Worker is waiting for tasks...")
channel.start_consuming()
