import pika
from PIL import Image
import os

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
    
    img = Image.open(uploads_dir_filepath) #filepath
    img = img.resize((200, 200))  # Resize image to 200x200
    output_path = os.path.join(OUTPUT_FOLDER, os.path.basename(filepath))
    print(f"Output directory path: {output_path}")
    img.save(output_path)
    print(f"Processed: {output_path}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue="image_resize", on_message_callback=process_image)
print("Worker is waiting for tasks...")
channel.start_consuming()
