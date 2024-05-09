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
import numpy as np
import matplotlib.pyplot as plt
logging.root.setLevel(logging.ERROR)

# import custom libraries
from utils import evaluate
from utils import make_llm 

curr_path = os.getcwd()
os.chdir(curr_path)

import pdb

# setup variables

model_dir = "_model"

output_file = "./output.txt"

results, chunk_size, time_taken = [], [], []

curr_time, input_stream, output_stream = 0.0, "", "" 

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
    global input_stream, curr_time
    input_stream += text
    
    start = time.time()
    output = llm_forward(text, max_length=1000)
    curr_time += time.time() - start
    
    translated_text = output[0]['translation_text']
    return text + evaluate.SEP + translated_text


def infer_backward(text):
    global output_stream
    
    output = llm_backward(text.split(evaluate.SEP)[1], max_length=1000)
    translated_text = output[0]['translation_text']
    output_stream += translated_text
    return text.split(evaluate.SEP)[0] + evaluate.SEP + translated_text


def evaluate_all(chunk_s):
    global results, input_stream, output_stream, curr_time, time_taken
    element = input_stream + evaluate.SEP + output_stream
    
    results.append((evaluate.jaccard_similarity(element), evaluate.cosine_similarity(element), evaluate.eucledian_distance(element), evaluate.bleu_score(element)))
    chunk_size.append(chunk_s)
    time_taken.append(curr_time)
    curr_time = 0.0
    
    
def softmax_and_scale(x, scale=300.0):
    exp_x = np.exp(x - np.max(x))  
    s = exp_x * scale / exp_x.sum(axis=0)
    print(s)
    return s
    

def visualize(chunk, scores, times):
    chunk = softmax_and_scale(chunk)
    
    fig, axs = plt.subplots(2, 2, figsize=(20, 20))
    
    axs[0, 0].scatter(times, [t[0] for t in scores], s=chunk)
    axs[0, 0].set_title('Jaccard similarity')
    axs[0, 0].set_xlabel('Inference time')
    axs[0, 0].set_ylabel('Score')
    axs[0, 0].grid(True)

    axs[0, 1].scatter(times, [t[1] for t in scores], s=chunk)
    axs[0, 1].set_title('Cosine similarity')
    axs[0, 1].set_xlabel('Inference time')
    axs[0, 1].set_ylabel('Score')
    axs[0, 1].grid(True)

    axs[1, 0].scatter(times, [t[2] for t in scores], s=chunk)
    axs[1, 0].set_title('Eucledian distance')
    axs[1, 0].set_xlabel('Inference time')
    axs[1, 0].set_ylabel('Score')
    axs[1, 0].grid(True)

    axs[1, 1].scatter(times, [t[3] for t in scores], s=chunk)
    axs[1, 1].set_title('BLEU score')
    axs[1, 1].set_xlabel('Inference time')
    axs[1, 1].set_ylabel('Score')
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(curr_path, "scores.png"))

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
    parser.add_argument('--dataset', metavar='t', action='store', type=str, default="dataset.txt", required=False, help="dataset to run the inference")
    args = parser.parse_args()
    
    with open(dataset, 'r') as file:
        # Read the first line
        first_line = file.readline()
        print("First line of the file:")
        print(first_line.strip())
    pdb.set_trace()
    
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
    for chunk in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 25, 50, 75, 100]:
        print(time.time(), "currently inferencing on chunk size:", chunk)
        with beam.Pipeline() as beam_pipeline:
            outputs = (
                beam_pipeline
                | 'read from file' >> beam.io.ReadFromText(os.path.join(curr_path, args.dataset))
                | 'split data' >> beam.ParDo(SplitIntoSentences())
                | 'chunk data' >> beam.ParDo(ChunkIntoNSentences(chunk))
                | 'make forward translation' >> beam.Map(infer_forward) 
                | 'make backward translation' >> beam.Map(infer_backward) 
                # | 'print' >> beam.Map(print)
            )

        evaluate_all(chunk)
    
    print(results)
    visualize(chunk_size, results, time_taken)

