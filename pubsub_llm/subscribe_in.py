from google.cloud import pubsub_v1
import sys, os
import pickle



# Configure the project name and topic name
# Note that systems needs to be authenticated with a json 
# to be able to use the pub/sub service associated with a project
project_id = "e6691-pkk2125"
topic_name = "translation-in"


subscription_name = f'{topic_name}-sub' # as set by convention

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

# write subscribed data to a file 
save_path = './input_text.txt'
def write_txt(data,path=save_path):
    with open(path, "w") as file:
        file.write(data)

# callback associated with subscription
def callback(message: pubsub_v1.subscriber.message.Message) -> None:
    # Print message for real-time observation
    print(f"***\nReceived message: {message.data.decode('utf-8')}\n***\n")
    data = message.data.decode('utf-8')
    write_txt(data)
    print(f'Wrote new data to {save_path}') # write data
    message.ack() # acknowledge
    gennew_sub() # delete and create
    os._exit(0) # exit 


streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback) # monitor

print(f"Waiting for messages on {subscription_path}...") 
try: # if able to pull
    streaming_pull_future.result(timeout=5)
    os._exit(0)
     
except: # Timeout of 5s selected
    print("Time exceeded 5s\n")
