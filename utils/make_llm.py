

# ! pip install --quiet apache-beam
# ! pip install --quiet transformers


import os
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


def make_model(model_name):
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return model, tokenizer


def save_model(model, token, folder):
    model.save_pretrained(os.path.join(folder, "model"))
    tokenizer.save_pretrained(os.path.join(folder, "tokenizer"))


def load_model(folder):
    model = AutoModelForSeq2SeqLM.from_pretrained(os.path.join(folder, "model"))
    tokenizer = AutoTokenizer.from_pretrained(os.path.join(folder, "tokenizer"))
    return model, tokenizer


if __name__ == "__main__":
    model = 'facebook/nllb-200-distilled-1.3B'

    model, tokenizer = make_model(model)

    save_model(model, tokenizer, "data")

    model, tokenizer = load_model("data")

