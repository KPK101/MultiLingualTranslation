from google.cloud import pubsub_v1
import sys, os
import pickle

# This is not integrated in the pipeline, can be used to debug behaviour of outputs communication

# Configure the project name and topic name
# Note that systems needs to be authenticated with a json 
# to be able to use the pub/sub service associated with a project
project_id = "e6691-pkk2125"
topic_name = "translation-out"

# configure the publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)

# Take input and publish
message = input('Enter text to be translated:...\n').encode('utf-8')
future = publisher.publish(topic_path, message)
message_id = future.result()
# confirm message id - can be used for analysis (Not included in our study)
print(f"Published to {topic_name} with ID: {message_id}")
