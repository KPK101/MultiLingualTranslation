# pip install --quiet apache-beam
# pip install --quiet transformers

import apache_beam as beam
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

import logging
logging.root.setLevel(logging.ERROR)

from utils.evaluate import Evaluate



beam_pipeline = beam.Pipeline()

output_file_name = "output"

outputs = (
    beam_pipeline
    | 'write results 2' >> beam.io.WriteToText(output_file_name, file_name_suffix = ".txt")
    | 'print the text file name' >> beam.Map(print)
)

beam_pipeline.run()
