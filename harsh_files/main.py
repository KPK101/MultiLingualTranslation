# pip install --quiet apache-beam
# pip install --quiet transformers
# pip install --quiet nltk
# pip install --quiet torch

# import apache-beam libraries
import apache_beam as beam
from apache_beam.transforms.window import FixedWindows
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.trigger import *

# import other python libraries
import os
import sys
import json
import time
import logging
import argparse
logging.root.setLevel(logging.ERROR)

# import custom libraries
from utils import evaluate
from utils import make_llm 

curr_path = os.getcwd()
os.chdir(curr_path)



# setup variables

model_dir = "_model"

output_file = "./output.txt"

results = [] 


"""
Add code to clean input data
Add code to take multiple stop words

"""

#####################################################################################
# --------------------------- CUSTOM APACHE BEAM FUNCS ---------------------------- #
#####################################################################################


def save_to_file(element):
    with open(output_file, 'a') as f:
        f.write(element + '\n')
        

class SplitIntoChunks(beam.DoFn):
    def process(self, element):
        words = element.split()  
        chunk_size = 5  
        for i in range(0, len(words), chunk_size):
            yield ' '.join(words[i:i+chunk_size])

            
class SplitIntoSentences(beam.DoFn):
    def process(self, element):
        sentences = element.split('.') 
        for sentence in sentences:
            if sentence.strip():
                yield sentence.strip()

                
class ChunkIntoNSentences(beam.DoFn):
    def __init__(self, n):
        self.n = n
        self.sentences_buffer = []

    def process(self, element):
        self.sentences_buffer.append(element) 
        if len(self.sentences_buffer) == self.n:
            sentence = ". ".join(self.sentences_buffer[:]) + "."
            yield sentence  
            self.sentences_buffer.clear()  

    def finish_bundle(self):
        if self.sentences_buffer:  
            sentence = ". ".join(self.sentences_buffer[:]) + "."
            yield beam.utils.windowed_value.WindowedValue(sentence, 0, [None, None])
            
            

def infer_forward(text):
    output = llm_forward(text, max_length=1000)
    translated_text = output[0]['translation_text']
    return text + evaluate.SEP + translated_text


def infer_backward(text):
    output = llm_backward(text.split(evaluate.SEP)[1], max_length=1000)
    translated_text = output[0]['translation_text']
    return text.split(evaluate.SEP)[0] + evaluate.SEP + translated_text


def evaluate_all(text):
    global results
    results.append((evaluate.jaccard_similarity(text), evaluate.cosine_similarity(text), evaluate.eucledian_distance(text), evaluate.bleu_score(text)))

#####################################################################################
# ---------------------------- APACHE BEAM FUNCS ENDS ----------------------------- #
#####################################################################################
    
start_time = time.time()
    
if __name__ == "__main__":
    
    # declare global variables
    global llm_forward, llm_backward
    
    
    # declare argument parser
    parser = argparse.ArgumentParser(description ='Set translation parameters')
    parser.add_argument('--sourcelanguage', metavar='s', action='store', type=str, default="eng_Latn", required=False, help="source language for LLM")
    parser.add_argument('--destlanguage', metavar='d', action='store', type=str, default="fra_Latn", required=False, help="translation language for LLM")
    parser.add_argument('--modelname', metavar='m', action='store', type=str, default="facebook/nllb-200-distilled-1.3B", required=False, help="LLM model hugging face link")
    args = parser.parse_args()
    
    # delete the older output file if it exists
    output_file_path = os.path.join(curr_path, output_file)
    
    if os.path.exists(output_file_path): 
        os.remove(output_file_path)
        
    
    # check if model exists and load the model else create the model
    model_dir_path = os.path.join(curr_path, model_dir)
    
    if os.path.exists(model_dir_path): 
        model, tokenizer = make_llm.load_model(model_dir_path)
    else:
        model, tokenizer = make_llm.make_model(args.modelname)
        make_llm.save_model(model, tokenizer, model_dir_path)
        
        
    # setup inferencing objects
    source, target = args.sourcelanguage, args.destlanguage
    llm_forward = make_llm.create_llm(model=model, tokenizer=tokenizer, src_lang=source, tgt_lang=target)
    llm_backward = make_llm.create_llm(model=model, tokenizer=tokenizer, src_lang=target, tgt_lang=source)
        
    
    # run the pipeline
    with beam.Pipeline() as beam_pipeline:
        outputs = (
            beam_pipeline
            | 'read from file' >> beam.io.ReadFromText('./dataset.txt')
            | 'split data' >> beam.ParDo(SplitIntoSentences())
            | 'chunk data' >> beam.ParDo(ChunkIntoNSentences(2))
            | 'make forward translation' >> beam.Map(infer_forward) 
            | 'make backward translation' >> beam.Map(infer_backward) 
            | 'calculate performance' >> beam.Map(evaluate_all)
            | 'print' >> beam.Map(print)
        )
    
    print(results)

# | 'read file' >> beam.io.Read(StreamingFileSource(file_pattern=os.path.join(curr_path, "./testing_dataset.txt")))
# | 'window into fixed bins' >> beam.WindowInto(beam.window.SlidingWindows(2, 2))
# | 'write results 2' >> beam.io.WriteToText(output_file_name, file_name_suffix = ".txt")
# | 'print the text file name' >> beam.Map(print)
# | 'Sliding Windows' >> beam.WindowInto(beam.window.FixedWindows(100))
# | 'Extract Key' >> beam.ParDo(lambda element: str(json.loads(element.decode('utf-8'))["timestamp"]))
# | 'Create Tuples' >> beam.ParDo(create_tuples)
# | 'Save to File' >> beam.Map(save_to_file)


# options = PipelineOptions(
#     streaming=True,
#     project=PROJECT_ID,
#     region=REGION,
#     # service_account_email="lssp-pubsub-service-account@lssp-project.iam.gserviceaccount.com",
#     # service_account_key_file='./lssp-project.json'
# )
