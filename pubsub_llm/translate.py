from google.cloud import pubsub_v1
import sys, os
import pickle
import time


def translate(text):
    return text

save_path = './input_text.txt'

with open(save_path,'w') as f:
    f.write('INIT')
    
def load_txt(path=save_path):
    with open(path, "r") as file:
        loaded_data = file.readline()
    return loaded_data



def write_txt(data,path=save_path):
    with open(path, "w") as file:
        file.write(data)

text_prev = "INIT"
text_current = "INIT"
text_out = None

###
# publish out setup
project_id = "e6691-pkk2125"
topic_name = "translation-out"
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)
###

try:
    while(True):
        
        print(f'Checking for new in input...current={text_current}')
        text_current = load_txt()
        if(text_current!=text_prev):
            print('Processing new input...')
            text_out_encoding = translate(text_current).encode('utf-8')
            future = publisher.publish(topic_path, text_out_encoding)
            message_id = future.result()
            
            print(f"Published text output to {topic_path} with ID: {message_id}\n")
            
            text_prev = text_current
            
        else:
            print('No change..checking for incoming text')
            os.system('python subscribe_in.py')
            time.sleep(2)
            
except KeyboardInterrupt:
    print('Interrupted program!')
    sys.exit(0)
