#spacy model loaded
import en_core_web_lg
import en_core_web_trf
from spacy.tokens import Token

import json
from load_parameters import get_parameters

from app.services.config_constants import  entity_ruler_collection_name, \
    add_manual_entities_pattern_id, add_manual_entities_entity, add_manual_entities_pattern
from custom_logging import logger
from mongodb_connection.mongodb.helper import fetch_data_from_db
from .custom_components import custom_infix



class SpacyInit:
    spacy_model = None
    spacy_lg_model = None

    # Load spacy model  for NER Extraction
    @classmethod
    def load_spacy_model(cls):
        """Load all the spacy models at startup"""
        try:
            cls.parameters = get_parameters()
            main_database_name = cls.parameters.get("DEFAULT","main_database_name")
            spacy_transformer_enabled = json.loads(cls.parameters.get("ner","spacy_transformer_enabled").lower())
        
            if spacy_transformer_enabled == True: 
                cls.spacy_model = en_core_web_trf.load()    
            else: 
                cls.spacy_model = en_core_web_lg.load()    
            
            
            cls.spacy_model = custom_infix(cls.spacy_model)
            cls.spacy_model.add_pipe("set_custom_sentence_end_points",
                                     before='parser')
            cls.client_ids = fetch_data_from_db(
                flag="fetch_all_client_ids",
                main_database_name=main_database_name,
                entity_ruler_collection_name=entity_ruler_collection_name,
                client_id=None)
            cls.ruler = {}
            # if "entity_ruler" not in cls.spacy_model.pipe_names:
            cls.config = {
                #         "phrase_matcher_attr": None,
                #         "validate": True,
                "overwrite_ents": True,
                #         "ent_id_sep": "||",
            }
            for client in cls.client_ids:
                # cls.ruler[client] = cls.spacy_model.add_pipe("entity_ruler",name=str(client), before='ner',config=cls.config)
                cls.set_ruler(client)
                patterns = cls.create_patterns(client)
                cls.add_ruler(client, patterns)
            cls.spacy_model.max_length = 4000000
            logger.debug(f'{ "en_core_web_trf" if spacy_transformer_enabled ==True else "en_core_web_lg"}   Model Loaded')
        except Exception as e:
            logger.exception(f'{e} - Unable to load the Spacy large model')

    # The role of this method is to load the Spacy large model if transformer model is loaded using load_spacy_model()
    # if load_spacy_model() already loaded the large model then this model just return the already loaded model's reference
    @classmethod
    def load_spacy_lg_model(cls):
        """Load embeddings model at startup"""
        try:
            cls.parameters = get_parameters()
            main_database_name = cls.parameters.get("DEFAULT","main_database_name")
            spacy_transformer_enabled = json.loads(cls.parameters.get("ner","spacy_transformer_enabled").lower())
        
            if spacy_transformer_enabled == False: 
                objspacy = SpacyInit()
                cls.spacy_lg_model = objspacy.get_spacy_model()
                logger.debug("Loading of Large Model Skipped to get vector.")     
            else: 
                cls.spacy_lg_model = en_core_web_lg.load()    

                logger.debug("en_core_web_lg Model Loaded")
        except Exception as e:
            logger.exception(f'{e} - Unable to load the Spacy large model')

    @classmethod
    def create_patterns(cls, client_id):
        """Initialize patterns in ruler"""

        main_database_name = cls.parameters.get("DEFAULT","main_database_name")
        patterns = fetch_data_from_db(
            flag="fetch_entity_rules",
            main_database_name=main_database_name,
            entity_ruler_collection_name=entity_ruler_collection_name,
            client_id=client_id)
        pattern = [{
            "label":
            p[add_manual_entities_entity],
            "pattern": [{
                'LOWER': w.lower()
            } for w in p[add_manual_entities_pattern].split()],
            "id":
            p[add_manual_entities_pattern_id]
        } for p in patterns]
        return pattern

    @classmethod
    def get_ruler_names(cls):
        return cls.client_ids

    # this method will set the ruler for transformer/large model.
    @classmethod
    def set_ruler(cls, client_id):
        if client_id not in cls.ruler:
            cls.ruler[client_id] = cls.spacy_model.add_pipe(
                "entity_ruler",
                name=str(client_id),
                before='ner',
                config=cls.config)

    # This model will set the ruler for large model only. It will run only if transformer model was loaded using
    # load_spacy_model() function
    # @classmethod
    # def set_ruler_lg(cls, client_id):
    #     if client_id not in cls.ruler:
    #         cls.ruler[client_id] = cls.spacy_lg_model.add_pipe(
    #             "entity_ruler",
    #             name=str(client_id),
    #             before='ner',
    #             config=cls.config)

    # This method will return the model loaded using spacy_model reference.
    @classmethod
    def get_spacy_model(cls):
        if cls.spacy_model is not None:
            return cls.spacy_model
        else:
            cls.load_spacy_model()
            return cls.spacy_model

    # This method will return the model loaded using spacy_lg_model reference.
    @classmethod
    def get_spacy_lg_model(cls):
        if cls.spacy_lg_model is not None:
            return cls.spacy_lg_model
        else:
            cls.load_spacy_lg_model()
            return cls.spacy_lg_model

    @classmethod
    def get_ruler(cls, client_id):
        return cls.ruler[client_id]

    @classmethod
    def add_ruler(cls, client_id: int, patterns: str):
        cls.ruler[client_id].add_patterns(patterns)

    @classmethod
    def remove_ruler(cls, client_id: int, patterns: str):
        cls.ruler[client_id].remove(patterns)


def not_synonymous(token):
    # Return if any of the tokens in the doc return True for token.like_num
    return token.like_num | token.like_email | token.is_currency | token.is_digit | token.like_url | token.is_stop | token.is_punct


# Register the Doc property extension "has_number" with the getter get_has_number
Token.set_extension("not_synonymous", getter=not_synonymous)
