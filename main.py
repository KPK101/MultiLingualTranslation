# pip install --quiet apache-beam
# pip install --quiet transformers

import apache_beam as beam
from apache_beam.transforms.window import FixedWindows
# from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

import logging
logging.root.setLevel(logging.ERROR)

from utils.evaluate import Evaluate

import time

class StreamingFileSource(beam.io.filebasedsource.FileBasedSource):
    def read_records(self, file_name, range_tracker):
        # Continuously read chunks of data from the file
        while not range_tracker.try_claim(1):
            yield None
        with self.open_file(file_name) as file:
            file.seek(range_tracker.start_position())
            for line in file:
                yield line.strip()
                time.sleep(10)


if __name__ == "__main__":
    beam_pipeline = beam.Pipeline()

    output_file_name = "output"

    outputs = (
        beam_pipeline
            | 'read file' >> beam.io.Read(StreamingFileSource(file_pattern="./testing_dataset.txt"))
            | 'window into fixed bins' >> beam.WindowInto(beam.window.SlidingWindows(2, 2))
            | 'write results 2' >> beam.io.WriteToText(output_file_name, file_name_suffix = ".txt")
            | 'print the text file name' >> beam.Map(print)
    )

    beam_pipeline.run()
