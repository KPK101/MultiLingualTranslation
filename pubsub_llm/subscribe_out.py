from google.cloud import pubsub_v1
import sys, os
import pickle


# Configure the project name and topic name
# Note that systems needs to be authenticated with a json 
# to be able to use the pub/sub service associated with a projec
project_id = "e6691-pkk2125"
topic_name = "translation-out"


subscription_name = f'{topic_name}-sub'

# configure subscriber
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)


# delete a subscription and generate a new one. Simulates a new subscriber asking for inputs every iteration
# Also observed the improve stability of pipeline w.r.t receiving duplicates of historical data 
def gennew_sub():
    subscription_path = subscriber.subscription_path(project_id, subscription_name)
    try:
        subscriber.delete_subscription(request={"subscription": subscription_path})
    except Exception as e:
        print(f"Error deleting subscription: {e}")
    try:
        subscriber.create_subscription(
            request={
            "name": subscription_path,
            "topic": f'projects/{project_id}/topics/{topic_name}',
            "enable_exactly_once_delivery": True,
            "enable_message_ordering": True,
            }
        )
    except Exception as e:
        print(f"Error creating subscription: {e}")


# callback associated with subscription     
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    print(f"***\nReceived message: {message.data.decode('utf-8')}\n***\n")
    data = message.data.decode('utf-8')
    write_txt(data)
    print(f'Wrote new data to {save_path}')
    # message.ack()
    # gennew_sub()
    os._exit(0)

## handling faulty delete without creation of a new sub
try:
    streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
except:
    subscriber.create_subscription(
            request={
            "name": subscription_path,
            "topic": f'projects/{project_id}/topics/{topic_name}',
            "enable_exactly_once_delivery": True,
            }
        )
# subscriber
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
    
# saving data
save_path = './output_text.txt'
def write_txt(data,path=save_path):
    with open(path, "w") as file:
        file.write(data)



print(f"Waiting for messages on {subscription_path}...")
try: # if able to pull data
    streaming_pull_future.result(timeout=5)
    os._exit(0)
    
except: # timeout 
    print("Time exceeded 5s\n")
    os._exit(0)
