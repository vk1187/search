import string
from collections import Counter
from custom_logging import logger

import numpy as np

from app.services.ner_engine.helper import ner_output_converter
from mongodb_connection.mongodb.helper import fetch_mannual_rules
from mongodb_connection.mongodb.utils import clean_data_based_on_rules

# from app.services.utils import global_clean_punctuations_start_stop
# from .ml_model.spacy.spacy_service import SpacyService

clean_punctuations_start_stop_special_char = '`‑”‘—’‒“–'


def global_clean_punctuations_start_stop(document, ignore_dot=False):
    special_char = clean_punctuations_start_stop_special_char
    all_symbols = string.punctuation + special_char
    if ignore_dot:
        all_symbols = all_symbols.replace('.', '')
    try:
        if (document[0] == document[-1]) & (
                document[0] in all_symbols) & len(document) == 1:
            document = ''

        elif document[-1] in all_symbols:

            document = document[:-1]
            document = global_clean_punctuations_start_stop(document)
        elif document[0] in all_symbols:
            document = document[1:]
            document = global_clean_punctuations_start_stop(document)
        else:
            pass
        return document
    except Exception as e:
        #             print(f'{e}')
        return document


def duplicate_entity_values(ner_entities):
    """return Duplicate entity values from the ner_entities output"""
    entity_values = list(np.concatenate(list(ner_entities.values())).ravel())
    return [
        item for item, count in Counter(entity_values).items() if count > 1
    ]


def cleaning_output(entities):
    # Add doc_id for testing purpose
    """applies cleaning rule on the entities """

    try:
            
        ner_entities = ner_output_converter(entities)
        ignore_values = duplicate_entity_values(ner_entities)
        list_of_rules = fetch_mannual_rules(rule_type="ner_postprocessing")
        list_of_automated_rules = fetch_mannual_rules(rule_type="ner_postprocessing_automated")
        list_of_rules=list_of_automated_rules+list_of_rules
        for key in ner_entities:
            ner_entities[key] = clean_data_based_on_rules(
                input_values=ner_entities.get(key),
                entity_name=key,
                values_to_ignore=ignore_values,
                list_of_rules=list_of_rules,
                #   spacy_model=SpacyService.model()
            )
        return ner_entities
    except Exception as exc:
        logger.error(exc)
        logger.exception(exc)
        # ner_entities[key] = [global_clean_punctuations_start_stop(i,ignore_dot=True) for i in ner_entities[key]]
        # any([1 for k in SpacyService.model()(text) if k.pos_ in i.get('values')]):
        #             ner_entities[key] = [i for i in ner_entities[key] if i.lower() != text.lower()]

    # testing purpose
    # if [i for i in ner_entities['Organization'] if i.lower().split()[0]=='the'] or [i for i in ner_entities['Location'] if i.lower().split()[0]=='the']:
    #     print('yes',doc_id)
    # return ner_entities
