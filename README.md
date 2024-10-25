# Multi-Lingual Translation

## A streaming pipeline for real-time multilingual translation of text with LLMs.


## Setup

### Download the repository
```
git clone https://github.com/KPK101/MultiLingualTranslation.git
```

### Move inside the repository
```
cd MultiLingualTranslation
```

### Download frameworks required
```
pip install -r requirements.txt
```

### Run the code
```
python main.py 
--sourcelanguage eng_Latn 
--destlanguage fra_Latn 
--modelname facebook/nllb-200-distilled-1.3B 
--dataset dataset.txt
```

<hr>

## Directory Tree
```
.
├── LICENSE
├── README.md
├── _model
│   ├── model
│   │   ├── config.json
│   │   ├── generation_config.json
│   │   └── pytorch_model.bin
│   └── tokenizer
│       ├── special_tokens_map.json
│       ├── tokenizer.json
│       └── tokenizer_config.json
├── dataset.txt
├── dataset.txt.bkp
├── dataset_files
│   ├── chicago_speech.txt
│   ├── dataset.txt
│   └── pmindia.v1.hi-en.tsv
├── experiments.txt
├── generate_dataset.py
├── main.py
├── requirements.txt
├── scores.png
└── utils
    ├── evaluate.py
    └── make_llm.py
```
