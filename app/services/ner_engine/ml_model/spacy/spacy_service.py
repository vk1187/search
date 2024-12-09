# from Models.spacy.load_spacy import spacy_lg, spacy_sm, spacy_md, spacy_entities
# import SpacyModel
import time
from collections import defaultdict
from load_parameters import get_parameters
import json

from app.services.ner_engine.helper import ner_output_converter, ner_output_format
from .load_spacy import SpacyInit
from app.services.ner_engine.utils import cleaning_output

# from app import SpacyInit

# from ...utils import output_format


class SpacyService:
    """Spacy singelton"""
    spacy_model = None
    spacy_lg_model = None

    def __init__(self):
        objspacy = SpacyInit()
        objspacy.load_spacy_model()
        objspacy.load_spacy_lg_model()
        # SpacyService.spacy_model == objspacy.get_spacy_model()

    @classmethod
    def model(cls):
        objspacy = SpacyInit()
        # cls.spacy_model = objspacy.get_spacy_model()
        return objspacy.get_spacy_model()
    
    @classmethod
    def model_lg(cls):
        objspacy = SpacyInit()
        # cls.spacy_model = objspacy.get_spacy_model()
        return objspacy.get_spacy_lg_model()

    @classmethod
    def add_ruler(cls, client_id, patterns):
        objspacy = SpacyInit()
        # cls.spacy_model = objspacy.get_spacy_model()
        objspacy.set_ruler(client_id)
        return objspacy.add_ruler(client_id, patterns)

    @classmethod
    def remove_ruler(cls, client_id, patterns):
        objspacy = SpacyInit()
        # cls.spacy_model = objspacy.get_spacy_model()
        return objspacy.remove_ruler(client_id, patterns)

    @classmethod
    def get_ruler(cls, client_id):
        objspacy = SpacyInit()
        return objspacy.get_ruler(client_id)

    @classmethod
    def get_ruler_names(cls):
        objspacy = SpacyInit()
        return objspacy.get_ruler_names()

    # This method is for NER task. This will be called when entity extraction is performed.
    @classmethod
    def model_doc(cls, text, client_id=None):
        objspacy = SpacyInit()
        cls.spacy_model = objspacy.get_spacy_model()
        cls.parameters = get_parameters()
        spacy_transformer_enabled = json.loads(cls.parameters.get("ner","spacy_transformer_enabled").lower())

        if cls.spacy_model is not None:
            if client_id in cls.get_ruler_names():
                ruler_name = str(client_id)
                if spacy_transformer_enabled == True:
                    with cls.spacy_model.select_pipes(enable=[
                            'transformer','tok2vec', 'tagger', 'parser', 'attribute_ruler',
                            'lemmatizer', ruler_name, 'ner'
                    ]):
                        doc = cls.spacy_model(text)
                        return doc
                else:
                    with cls.spacy_model.select_pipes(enable=[
                            'tok2vec', 'tagger', 'parser', 'attribute_ruler',
                            'lemmatizer', ruler_name, 'ner'
                    ]):
                        doc = cls.spacy_model(text)
                        return doc
            else:
                if spacy_transformer_enabled == True:
                    with cls.spacy_model.select_pipes(enable=[
                            'transformer','tok2vec', 'tagger', 'parser', 'attribute_ruler',
                            'lemmatizer', 'ner'
                    ]):
                        doc = cls.spacy_model(text)
                        return doc
                else:
                    with cls.spacy_model.select_pipes(enable=[
                            'tok2vec', 'tagger', 'parser', 'attribute_ruler',
                            'lemmatizer', 'ner'
                    ]):
                        doc = cls.spacy_model(text)
                        return doc
                #Bug - need to check, not disabling clients
                # disable_clients = [str(i) for i in cls.get_ruler_names() if i != client_id]
                # cls.spacy_model.disable_pipes(disable_clients)
                # doc = cls.spacy_model(text)
                # return doc

    # This function is for vector representation for the input text. We are using only large model for it.
    # as transformers model don't have inbuilt vector representation file. That's why we are not enabling "transformer"
    # here in the pipeline as we have done in the model_doc()
    @classmethod
    def model_doc_lg(cls, text):
        objspacy = SpacyInit()
        cls.spacy_lg_model = objspacy.get_spacy_lg_model()
        
        with cls.spacy_lg_model.select_pipes(enable=[
                'tok2vec', 'tagger', 'parser', 'attribute_ruler',
                'lemmatizer', 'ner'
        ]):
            doc = cls.spacy_lg_model(text)
            return doc

    @classmethod
    def extract_entities(cls,
                         text,
                         client_id=None,
                         original=False,
                         apply_rules_flag=False):
        """extract entities from data"""
        tic = time.time()
        entities = defaultdict(set)
        # Remove below line
        # text = '.'.join(text)
        if client_id is not None:
            doc = cls.model_doc(text, client_id)
        else:
            doc = cls.model_doc(text)
        for ent in doc.ents:
            entities[ent.label_].add(ent.text)
        # print(entities)
        if apply_rules_flag:
            ner_entities = cleaning_output(entities)
            entities = ner_output_format(ner_entities, tic)
            return doc, entities
        if not original:
            ner_entities = ner_output_converter(entities)
            entities = ner_output_format(ner_entities, tic)
            # Remove below line
            # entities.update({'doc_value': text})
        return doc, entities

    # @classmethod
    # def synonmize_check(cls, text, original=False):
    #     tic = time.time()
    #     entities = defaultdict(set)
    #     doc = cls.model_doc(text)
    #     for i in doc:
    #         # i.like_num or i.like_email or i.is_currency

    #         return i.like_num or i.like_email or i.is_currency


# class SpacySerializer:
#     """Outputs Entity based on the library and model used"""

#     def serialize(self, ner_model):
#         if ner_model.library_name == 'spacy':
#             spacyservice=SpacyService()
#              output = spacyservice.spacy_entities(ner_model.text, nlp_model=ner_model.nlp)
#         return output
