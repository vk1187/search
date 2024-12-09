from Models.huggingface.load_transformers import roberta_large, model_solver, transformer_entities
from transformers import pipeline

from config import parameters


class TransformerInit:
    """To initialize all the parameters and models which are used in serialization class
    Description:

    text = input text
    library_name = huggingface
    model_name = spacy -> en_core_web_lg & huggingface ->xlm-roberta-large-finetuned-conll03-english
                The value of model can be changed ,default models are fast to load
    spacy_models = list of all the spacy models which are loaded at startup
    hf_model = default roberta model

    """

    def __init__(self, text, library_name=None, model_name=None, models=roberta_large):
        self.library_name = library_name
        self.model_name = model_name
        self.text = text
        if self.model_name is None or self.model_name == parameters['default_hf']:
            self.nlp = models
        elif self.model_name in parameters['tested_models']:
            pretrained_model = self.model_name
            tokenizer_model = self.model_name
            model_t, tokenizer_t = model_solver(pretrained_model, tokenizer_model)
            self.nlp = pipeline('ner', grouped_entities=True, model=model_t, tokenizer=tokenizer_t)
        else:
            raise ValueError(self.model_name)


class TransformerSerializer:
    """Outputs Entity based on the library and model used"""

    def serialize(self, ner_model):
        if ner_model.library_name == 'huggingface':
            output = transformer_entities(ner_model.text, nlp_model=ner_model.nlp)
        return output
