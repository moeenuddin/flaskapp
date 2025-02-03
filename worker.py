import pika
from PIL import Image
import os

# CloudAMQP connection
AMQP_URL = "amqps://hfwdoxdg:1aeRZiQ9lXXeWwlFioDsGMCqNAfi_4sU@campbell.lmq.cloudamqp.com/hfwdoxdg" #"your_cloudamqp_url"
params = pika.URLParameters(AMQP_URL)
connection = pika.BlockingConnection(params)
channel = connection.channel()
channel.queue_declare(queue="image_resize")

OUTPUT_FOLDER = "processed_images"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_image(ch, method, properties, body):
    filepath = body.decode()
    img = Image.open(filepath)
    img = img.resize((200, 200))  # Resize image to 200x200
    output_path = os.path.join(OUTPUT_FOLDER, os.path.basename(filepath))
    img.save(output_path)
    print(f"Processed: {output_path}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_consume(queue="image_resize", on_message_callback=process_image)
print("Worker is waiting for tasks...")
channel.start_consuming()
