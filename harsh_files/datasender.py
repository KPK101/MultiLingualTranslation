from google.cloud import pubsub_v1
import time

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT_ID, TOPIC_NAME)

while True:
    data = "your_message_here"
    publisher.publish(topic_path, data.encode("utf-8"))
    time.sleep(5)  
