from itertools import chain

# from pymongo import MongoClient
from custom_logging import logger
# from mongodb_connection import configurations
from mongodb_connection.mongodb import mongo_client
from load_parameters import get_parameters
from app.services.config_constants import mongodb_acronym_collection, mongodb_acronym_collection_key, \
    mongodb_acronym_collection_Options, mongodb_acronym_collection_Category

# database_name, mongodb_acronym_collection, \
#     mongodb_acronym_collection_key, \
#     mongodb_acronym_collection_Options, \
#     mongodb_acronym_collection_Category

# with open(mongodb_configuration_path, 'r') as file:
#     try:
#         constants = yaml.safe_load(file)
#     except yaml.YAMLError as exc:
#         logger.debug(exc)

parameters = get_parameters()
database_name = parameters.get("DEFAULT",
                               'main_database_name')  #: SLBConfig_Cognitive
# mongodb_host = constants['host'] #: localhost
# mongodb_port = constants['port'] #: 27017

mongodb_ner_collection = parameters["DEFAULT"][
    'mongodb_ner_rules_collection']  #: NERRules
# mongodb_acronym_collection = mongodb_acronym_collection  # : Acronym
# mongodb_acronym_collection_key = mongodb_acronym_collection_key  #: Key
# mongodb_acronym_collection_Options = mongodb_acronym_collection_Options  #: Options
# mongodb_acronym_collection_Category = mongodb_acronym_collection_Category  #: Category

try:
    client = mongo_client
    # client = MongoConnection.getInstance()
    db = client[database_name]
except Exception as e:
    logger.error(
        f'Please check database is  not available in Mongodb or MongodbInstance is not made :Error: {e}'
    )
    logger.error(e)
    logger.exception(e)
    print(
        f'Please check database is  not available in Mongodb or MongodbInstance is not made'
    )


def acronym_expansion(acronym_term: str, domain: str = None) -> list:
    """returns exmapsniosn for acrnyms saved in monogdb"""
    try:
        logger.debug(f'{acronym_term} --- acronym_term')
        # logger.debug(f'{db.Acronym.find({})} --- db_term')
        if domain == 'All' or domain is None:
            # result = [obj[target_col] for obj in
            #           db[acronym_collection].find({query_col: {'$in': [acronym_term.lower().strip(),
            #                                                            acronym_term.upper().strip()]}},
            #                                     {target_col: 1})]

            result = [
                obj[mongodb_acronym_collection_Options]
                for obj in db[mongodb_acronym_collection].find(
                    {
                        mongodb_acronym_collection_key: {
                            '$regex': '^' + acronym_term + '$',
                            '$options': 'i'
                        }
                    }, {mongodb_acronym_collection_Options: 1})
            ]
        else:
            result = [
                obj[mongodb_acronym_collection_Options]
                for obj in db.Acronym.find(
                    {
                        mongodb_acronym_collection_key: acronym_term,
                        mongodb_acronym_collection_Category: domain
                    }, {mongodb_acronym_collection_Options: 1})
            ]
        logger.debug(f'{result} --- result of acronym_expansion_fn')
        if len(result) >= 1:
            return list(chain.from_iterable(result))
        # elif len(result) == 1:
        #     return list(result)
        else:
            return None
    except Exception as e:
        logger.error(f'{e}')
        logger.exception(e)
        # print(e)
