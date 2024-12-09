# from mongodb_connection.mongodb.helper import MongoConnection
from custom_logging import logger

# from app.services.config_constants import main_database_name,entity_ruler_collection_name
# from app.services.ner_engine.ml_model.spacy import SpacyService
# from app.services.utils import DataPreprocessor
# from app.services.ner_engine.helper import ner_output_format
# from authenitcation.auth import token_required
# from custom_logging import logger
from mongodb_connection.mongodb.helper import fetch_data_from_db

# def mannual_entity_patterns_filter(collection,client_id:int=None,project_id:int=None):
#     """returns entity_patterns_filter condition"""

#     if (client_id is None )or (project_id is None):
#         return collection.find({},{"pattern" : 1,"entity" :1,"text" : 1,"pattern_id" : 1,"_id":0})

#     else:
#         return collection.find({"client_id":client_id,"project_id":project_id},{"pattern" : 1,"entity" :1,"text" : 1,"pattern_id" : 1,"_id":0})

# main_database_name='SLBConfig_Cognitive'
# entity_ruler_collections_name='EntityRuler'

# def fetch_entity_rules(main_database_name:str,entity_ruler_collections_name:str):
#     """returns entity_rules"""

#     # client = MongoConnection.getInstance()
#     # collection = client[main_database_name][entity_ruler_collections_name]
#     mc = MongoClient("mongodb://rakshit:rakshit@192.168.233.71:27017")
#     collection = mc['SLBConfig_Cognitive']['EntityRuler']
#     entity_rules = [i for i in mannual_entity_patterns_filter(collection,111111,123)]

#     return entity_rules


def get_patterns_and_pattern_ids(on_the_fly_flag: int = 0,
                                 main_database_name=None,
                                 entity_ruler_collection_name=None,
                                 client_id: int = None,
                                 project_id: int = None,
                                 input_label: str = None,
                                 input_pattern: str = None,
                                 input_pattern_id: str = None):
    if on_the_fly_flag == 0:
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
        # pattern_ids = [p['pattern_id'] for p in patterns] #p['entity']+'||'+p['pattern_id']
    else:
        pattern = [{
            "label": il,
            "pattern": [{
                'LOWER': w.lower()
            } for w in ip.split()],
            "id": ipi
        } for il, ip, ipi in zip(input_label, input_pattern, input_pattern_id)]
        # pattern_ids = pattern[0]['id']
    pattern_ids = [p['id'] for p in pattern]
    return pattern, pattern_ids


def remove_patterns_from_ruler(SpacyService, client_id, pattern_ids):
    """removes all entity_patterns from entity ruler"""
    if isinstance(pattern_ids, str):
        pattern_ids = [pattern_ids]

    for i in pattern_ids:
        try:
            SpacyService.remove_ruler(client_id, i)
            logger.info(f'{i} pattern_id is removed from the ruler')
        except:
            logger.error(f'{i} pattern_id is not present in the ruler')
            continue

def remove_patterns_from_ruler_basic(SpacyService, client_id, pattern_ids):
    """removes all entity_patterns from entity ruler"""
    if isinstance(pattern_ids, str):
        pattern_ids = [pattern_ids]

    for i in pattern_ids:
        try:
            SpacyService.remove_ruler(client_id, i)
            logger.info(f'{i} pattern_id is removed from the ruler')
        except:
            logger.info(f'{i} pattern_id is not present in the ruler')
            continue

        # print(fetch_entity_rules(main_database_name,entity_ruler_collections_name))


def mannual_entity_patterns_filter_update(er, client_id: int, project_id: int,
                                          pattern_id: int, pattern: str,
                                          entity: str, text: str):
    """returns entity_patterns_filter condition"""

    return er.update_one(
        {
            add_manual_entities_client_id: client_id,
            add_manual_entities_project_id: project_id,
            add_manual_entities_pattern_id: pattern_id
        }, {
            "$set": {
                add_manual_entities_pattern: pattern,
                add_manual_entities_entity: entity,
                add_manual_entities_text: text
            }
        })


# from pymongo import MongoClient
# mc = MongoClient("mongodb://rakshit:rakshit@192.168.233.71:27017")
# er = mc['SLBConfig_Cognitive']['EntityRuler']
# print([i for i in mannual_entity_patterns_filter(er,111111,123)])

# nlp =spacy.load('en_core_web_lg')

# config = {
# #         "phrase_matcher_attr": None,
# #         "validate": True,
#         "overwrite_ents": True,
# #         "ent_id_sep": "||",
#       }
# ruler=nlp.add_pipe("entity_ruler",config=config)

# ruler.add_patterns([{"label": "Fruit", "pattern": "apple","id": "apple"}])
# ruler.add_patterns([{"label": "F", "pattern": "apple","id": "apple"}])
# ruler.add_patterns([{"label": "Location", "pattern": "apple","id": "apple"}])
# ruler.add_patterns([{"label": "Organization", "pattern": "apple","id": "apple"}])
# ruler.add_patterns([{"label": "Place", "pattern": "apple","id": "apple"}])
# ruler.add_patterns([{"label": "Thing", "pattern": "apple","id": "apple"}])

# nlp.add_patterns([{"label": "Fruit", "pattern": "apple","id": "apple"}])
# nlp.add_patterns([{"label": "F", "pattern": "apple","id": "apple"}])
# nlp.add_patterns([{"label": "Location", "pattern": "apple","id": "apple"}])
# nlp.add_patterns([{"label": "Organization", "pattern": "apple","id": "apple"}])
# nlp.add_patterns([{"label": "Place", "pattern": "apple","id": "apple"}])
# nlp.add_patterns([{"label": "Thing", "pattern": "apple","id": "apple"}])

# ruler.remove('apple')

# nlp.remove('apple')

# ruler.patterns

# doc = nlp("A text about apple")
# print([(i.text,i.label_) for i in doc.ents])
