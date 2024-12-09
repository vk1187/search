import os
import pickle
from pathlib import Path
from uuid import uuid4

import faiss
import numpy as np

from app.services.config_constants import job_config_collections_name, \
    relatedentity_job_critetrion_configuration, job_projection_configuration
from app.services.config_constants import search_analytics_collections_name
from custom_logging import logger
from mongodb_connection.mongodb import mongo_client

from load_parameters import get_parameters

import os
import glob

from custom_logging import logger
from mongodb_connection.mongodb import mongo_log_client

embedding_path = os.path.join(
        os.getcwd(),
        'entity_files',
        'entity_embeddings',
    )
def create_entity_model_files():
    """Created path for saving embedding models and query pcikles"""
    embedding_path = os.path.join(
        os.getcwd(),
        'entity_files',
        'entity_embeddings',
    )
    query_pickle_path = os.path.join(os.getcwd(), 'entity_files',
                                     'entity_pickles')
    os.makedirs(embedding_path, exist_ok=True)
    os.makedirs(query_pickle_path, exist_ok=True)
    return embedding_path, query_pickle_path


# embedding_path, query_pickle_path = create_entity_model_files()


def suffix_client_project(project_id=None, client_id=None):
    """Naming convention for pickle files"""
    if project_id is not None and client_id is not None:
        file_suffix = str(client_id) + "_" + str(project_id)

    elif project_id is not None and client_id is None:
        file_suffix = str(project_id)

    elif project_id is None and client_id is not None:
        file_suffix = str(client_id)

    else:
        file_suffix = 'full'

    return file_suffix + '_' + str(uuid4().hex)


def emebedding_entity_path(embedding_index_filename, entity_pickle_filename):
    # file_suffix = suffix_client_project(project_id, client_id)
    faiss_entity_index_path = os.path.join(os.getcwd(),
                                           embedding_index_filename)
    entity_idx2tok_path = os.path.join(os.getcwd(), entity_pickle_filename)
    return faiss_entity_index_path, entity_idx2tok_path


def read_query_index(faiss_entity_index_path):
    return faiss.read_index(faiss_entity_index_path)


def read_idx2tok(entity_idx2tok_path):
    with open(entity_idx2tok_path, 'rb') as entity_file:
        pickle_data =  pickle.load(entity_file)
        entity_file.close()
    return pickle_data
    # return pickle.load(open(entity_idx2tok_path, 'rb'))


def write_query_index(unique_ents_vecotrs, project_id, client_id):
    """creating and saving faiss index of all the unique queries for repespective project and clients """
    try:
        parameters = get_parameters()
        file_suffix = suffix_client_project(project_id, client_id)

        related_entity_embedding_path = parameters.get("related_entity",
                                                       "embedding_path")
        corpus_embeddings = unique_ents_vecotrs
        query_index = faiss.IndexIDMap(faiss.IndexFlatIP(300))
        faiss.normalize_L2(corpus_embeddings)
        query_index.add_with_ids(
            corpus_embeddings,
            np.array(range(0, len(unique_ents_vecotrs))).astype(np.int64))

        embedding_path_location = os.path.join(
            os.path.join(related_entity_embedding_path,
                         'embedding_' + file_suffix + '.index'))
        os.makedirs(os.path.dirname(embedding_path_location), exist_ok=True)
        faiss.write_index(query_index, embedding_path_location)
        return embedding_path_location
    except Exception as e:
        logger.error(f'[write_query_index] {e}')
        logger.exception(e)
        return None


def entity_pickle_vectorindex_path(project_id, client_id):
    client = mongo_client
    parameters = get_parameters()
    job_config_database_name = parameters.get("DEFAULT",
                                              "job_config_database_name")
    if project_id is not None and client_id is not None:

        pickle_embedding_index_cursor = client[job_config_database_name][
            job_config_collections_name].find(
                {
                    "projectId": {"$in": [int(project_id), str(project_id)]},
                    "clientId": {"$in": [int(client_id), str(client_id)]},
                    **relatedentity_job_critetrion_configuration
                }, {**job_projection_configuration})

        pickle_embedding_index_data_list = list(pickle_embedding_index_cursor)
        pickle_embedding_index_data = pickle_embedding_index_data_list[0]

        pickle_location = pickle_embedding_index_data.get(
            'pickle_location', None)
        vector_index_location = pickle_embedding_index_data.get(
            'vector_index_location', None)
        pickle_name = pickle_embedding_index_data.get('pickle_name', None)
        vector_index_name = pickle_embedding_index_data.get(
            'vector_index_name', None)
        pickle_path = os.path.join(pickle_location, pickle_name)
        vector_index_path = os.path.join(vector_index_location,
                                         vector_index_name)
        return pickle_path, vector_index_path
    else:
        return None, None


def write_entity_pickles(entity_tokens, project_id, client_id):
    """creating and saving faiss index of all the unique queries for repespective project and clients """
    try:
        parameters = get_parameters()
        related_entity_pickle_path = parameters.get("related_entity",
                                                    "pickle_path")

        file_suffix = suffix_client_project(project_id, client_id)
        file_name = os.path.join(related_entity_pickle_path,
                                 'unique_entity_' + file_suffix + '.pth')
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        with open(file_name, 'wb+') as unique_entity_file:
            pickle.dump(entity_tokens, unique_entity_file)
            unique_entity_file.close()
        return file_name
    except Exception as e:
        logger.error(f'[write_entity_pickles] {e}')
        logger.exception(e)
        return None


def findkeys(node, kv):
    """return values of the keys from the nested dicitonary """
    if isinstance(node, list):
        for i in node:
            for x in findkeys(i, kv):
                yield x
    elif isinstance(node, dict):
        if kv in node:
            yield node[kv]
        for j in node.values():
            for x in findkeys(j, kv):
                yield x


config_flags = {"manual_flag": "true", "autoCorrection_flag": "false"}


def embedding_query_index(model_embedding_file, embedder, project_id,
                          client_id):
    """reutrns faiss index and unique queries for all the queries present in Mongo"""
    file_suffix = suffix_client_project(project_id, client_id)
    parameters = get_parameters()
    search_analytics_db_name = parameters.get("DEFAULT",
                                              "search_analytics_db_name")
    if model_embedding_file.is_file():
        flag = True
        with open(
                os.path.join('models', 'query_pickles',
                             'queries_' + file_suffix + '.pth'), 'rb') as file:
                                
            unique_queries = pickle.load(file)
            file.close()
                # open(
                #     os.path.join('models', 'query_pickles',
                #                 'queries_' + file_suffix + '.pth'), 'rb'))
        query_index = faiss.read_index(
            os.path.join(embedding_path,
                         'embedding_' + file_suffix + '.index'))

    else:
        client = mongo_client
        # client = MongoConnection.getInstance()
        if project_id is not None and client_id is not None:

            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find(
                    {
                        "projectId": {"$in": [int(project_id), str(project_id)]},
                        "clientId": {"$in": [int(client_id), str(client_id)]},
                        **config_flags
                    }, {'query', 'timestamp'})
        elif project_id is not None and client_id is None:
            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find(
                    {
                        "projectId": {"$in": [int(project_id), str(project_id)]},
                        **config_flags
                    }, {'query', 'timestamp'})
        elif project_id is None and client_id is not None:
            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find(
                    {
                        "clientId": {"$in": [int(client_id), str(client_id)]},
                        **config_flags
                    }, {'query', 'timestamp'})
        else:
            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find({**config_flags},
                                                        {'query', 'timestamp'})

        all_data = [dict(i) for i in query_cursor if i.get('query', 0) != 0]
        # unique_queries  = np.unique(list(findkeys(all_data, 'query'))).tolist()
        unique_queries = np.unique(
            list((map(lambda x: x.lower().strip(),
                      findkeys(all_data, 'query'))))).tolist()
        logger.debug('[Related Search] Saving unique query in  Pickel format')
        with  open(
                os.path.join('models', 'query_pickles',
                             'queries_' + file_suffix + '.pth'), 'wb') as write_file:
            pickle.dump(list(unique_queries),write_file)                    
            # pickle.dump(
            #     list(unique_queries),
            #     open(
            #         os.path.join('models', 'query_pickles',
            #                     'queries_' + file_suffix + '.pth'), 'wb'))

        query_index = return_query_index(embedder, unique_queries, project_id,
                                         client_id)

    return unique_queries, query_index


def emebbding_file(project_id, client_id):
    """Naming convention for embedding files"""
    file_suffix = suffix_client_project(project_id, client_id)
    my_file = Path(
        os.path.join(embedding_path + "embedding_" + file_suffix + ".index"))
    return my_file


def return_query_index(embedder, unique_queries, project_id, client_id):
    """creating and saving faiss index of all the unique queries for repespective project and clients """
    file_suffix = suffix_client_project(project_id, client_id)
    corpus_embeddings = embedder.encode(unique_queries, convert_to_tensor=True)
    query_index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
    faiss.normalize_L2(corpus_embeddings.numpy())
    query_index.add_with_ids(
        corpus_embeddings.numpy(),
        np.array(range(0, len(unique_queries))).astype(np.int64))
    faiss.write_index(
        query_index,
        os.path.join(embedding_path, 'embedding_' + file_suffix + '.index'))
    return query_index


def delete_old_files(client_id, project_id, job_Name):
    client = mongo_log_client
    parameters = get_parameters()
    main_database_name = parameters.get("DEFAULT", "main_database_name")
    query_cursor = client[main_database_name]["ModelConfiguration"].find(
        {
            "projectId": {"$in": [int(project_id), str(project_id)]},
            "clientId": {"$in": [int(client_id), str(client_id)]},
            "jobName": job_Name
        }, {
            'vector_index_location': 1,
            'vector_index_name': 1,
            'pickle_location': 1,
            'pickle_name': 1,
            "_id": 0
        })
    query_cursor = list(query_cursor)
    pl = [(i['pickle_location'].replace("\\", "/"), i['pickle_name'])
          for i in query_cursor]

    latest_pickle_path = [os.path.join(i[0], i[1]) for i in pl]
    vl = [(i['vector_index_location'].replace("\\",
                                              "/"), i['vector_index_name'])
          for i in query_cursor]
    latest_vector_path = [os.path.join(i[0], i[1]) for i in vl]

    all_files_vl = [
        i for j in vl for i in glob.glob(os.path.join(j[0], '*'))
        if i.find(str(client_id) + '_' + str(project_id)) > 0
    ]

    all_files_pl = [
        i for j in pl for i in glob.glob(os.path.join(j[0], '*'))
        if i.find(str(client_id) + '_' + str(project_id)) > 0
    ]

    vl_deleted = list(
        set([i for i in all_files_vl if i not in latest_vector_path]))
    pl_deleted = list(
        set([i for i in all_files_pl if i not in latest_pickle_path]))
    for file_name in vl_deleted + pl_deleted:
        logger.debug(f"Deleting File {file_name}")
        # sleep(1)
        try:
            os.remove(file_name)
        except Exception as e:
            logger.error(e)
            logger.exception(e)
            logger.debug("Unable to delete file")
            continue
