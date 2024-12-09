import time
from collections import defaultdict

import utils
from transformers import pipeline, AutoModelForTokenClassification, AutoTokenizer

from config import parameters


def model_solver(pretrained_model, tokenizer_model):
    "Loads the pretrained model to output its model and tokenizer which is used in transformer_entities nlp_model"
    print('Loading Model :', str(tokenizer_model))
    model = AutoModelForTokenClassification.from_pretrained(pretrained_model)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_model)
    return model, tokenizer


def load_huggingface_tf_en():
    "Load HuggingFace Transformer default Model"
    pretrained_model = parameters['default_hf']
    tokenizer_model = parameters['default_hf']
    model_t, tokenizer_t = model_solver(pretrained_model, tokenizer_model)
    transformer_nlp_model = pipeline('ner', grouped_entities=True, model=model_t, tokenizer=tokenizer_t)
    return transformer_nlp_model


roberta_large = load_huggingface_tf_en()


def transformer_entities(text, nlp_model):
    "Finds entity using pretrained transformer english models"
    tic = time.time()
    entities = defaultdict(set)
    output = nlp_model(text)
    for i in output:
        entities[i['entity_group']].add(i['word'])
    entities = utils.output_format(entities, tic)
    return entities
