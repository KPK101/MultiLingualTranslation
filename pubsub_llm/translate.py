from google.cloud import pubsub_v1
import sys, os
import pickle
import time


def translate(text): # a placeholder for the LLM - makes experimenting easier. 
    return text

save_path = './input_text.txt'

with open(save_path,'w') as f: # initiaize input document with the INIT keyword
    f.write('INIT')
    
def load_txt(path=save_path): # load text from a file
    with open(path, "r") as file:
        loaded_data = file.readline()
    return loaded_data



def write_txt(data,path=save_path): # write text to a file
    with open(path, "w") as file:
        file.write(data)

text_prev = "INIT" # init
text_current = "INIT" # init
text_out = None # output 

###
# publish out setup
# configuring the output topic
project_id = "e6691-pkk2125"
topic_name = "translation-out"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)
###

try:
    # Try a look after every iteration
    while(True):
        
        print(f'Checking for new in input...current={text_current}')
        # load latest input
        text_current = load_txt()
        # check if there is a change
        if(text_current!=text_prev):
            # Then process
            print('Processing new input...')
            # translate the input text and encode (This function is a placeholder and does not actually translate)
            text_out_encoding = translate(text_current).encode('utf-8') 
            # Publish the computed output to the output topic
            future = publisher.publish(topic_path, text_out_encoding)
            message_id = future.result()
            
            print(f"Published text output to {topic_path} with ID: {message_id}\n")
            # update latest input
            text_prev = text_current
            
        else:
            # If there is no change, wait and loop again
            print('No change..checking for incoming text')
            # subscribe incoming texts. If a new input is received, it update the text data for recognizing a difference in text_prev and text_current
            os.system('python subscribe_in.py')
            # sleep for 2 seconds
            time.sleep(2)

# interrupt and stop program
except KeyboardInterrupt:
    print('Interrupted program!')
    sys.exit(0)
