import os
import pickle
from pathlib import Path
import re
import faiss
import numpy as np
from app.services.utils import convert_unidecode, trendingsearch_relatedsearch_widget_cleaner
from app.services.config_constants import search_analytics_collections_name, \
    relatedsearch_configuration_flags
from app.services.config_constants import job_config_collections_name, \
    relatedsearch_job_critetrion_configuration, job_projection_configuration
# from app.services.config_constants import related_search_embedding_path, related_search_query_pickle_path

from custom_logging import logger
from mongodb_connection.mongodb import mongo_client, mongo_log_client
from uuid import uuid4
import time
import glob

from load_parameters import get_parameters


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


def create_model_files():
    """Created path for saving embedding models and query pcikles"""
    embedding_path = os.path.join(
        os.getcwd(),
        'models',
        'embeddings',
    )
    query_pickle_path = os.path.join(os.getcwd(), 'models', 'query_pickles')
    os.makedirs(embedding_path, exist_ok=True)
    os.makedirs(query_pickle_path, exist_ok=True)
    return embedding_path, query_pickle_path


embedding_path, query_pickle_path = create_model_files()


def valid_queries(allowed_punctuation_pattern, token):
    try:
        if allowed_punctuation_pattern.search(token).start() not in [
                0, len(token) - 1
        ]:
            return True
        else:
            return False
    except Exception as e:
        return True


def outputFormatRelatedQueryEmbedding(status,
                                      client_id,
                                      project_id,
                                      query_pickle_name,
                                      query_vector_index_name,
                                      query_pickle_location=None,
                                      query_vector_index_location=None,
                                      tic=0):
    return {
        "status": status,
        'pickle_location': query_pickle_location,
        'vector_index_location': query_vector_index_location,
        'pickle_name': query_pickle_name,
        'vector_index_name': query_vector_index_name,
        "client_id": client_id,
        "project_id": project_id,
        "run_time": time.time(),
        'execution_time': time.time() - tic
    }


def pickle_vector_index_values(model_embedding_file, pickle_file):
    """reutrns faiss index and unique queries for all the queries present in Mongo"""

    with  open(os.path.join(os.getcwd(), pickle_file), 'rb') as read_pickle_file:
        unique_queries = pickle.load(read_pickle_file)
       
    # unique_queries = pickle.load(
    #     open(os.path.join(os.getcwd(), pickle_file), 'rb'))
    
    # with  open(os.path.join(os.getcwd(), model_embedding_file), 'rb') as read_model_embedding_file:
    #     query_index = faiss.read_index(read_model_embedding_file)


    query_index = faiss.read_index(
        os.path.join(os.getcwd(), model_embedding_file))
    return unique_queries, query_index


def pickle_vectorindex_path(project_id, client_id):
    client = mongo_client
    parameters = get_parameters()
    if project_id is not None and client_id is not None:
        job_config_database_name = parameters.get("DEFAULT",
                                                  "job_config_database_name")

        pickle_embedding_index_cursor = client[job_config_database_name][
            job_config_collections_name].find(
                {
                    "projectId": {"$in": [int(project_id), str(project_id)]},
                    "clientId": {"$in": [int(client_id), str(client_id)]},
                    **relatedsearch_job_critetrion_configuration
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


def embedding_query_index(model_embedding_file, embedder, project_id,
                          client_id):
    """reutrns faiss index and unique queries for all the queries present in Mongo"""
    file_suffix = suffix_client_project(project_id, client_id)
    parameters = get_parameters()
    search_analytics_db_name = parameters.get("DEFAULT",
                                              "search_analytics_db_name")
    if model_embedding_file.is_file():
        flag = True
        with open (os.path.join('models', 'query_pickles','queries_' + file_suffix + '.pth'), 'rb') as qp_file:
            unique_queries = pickle.load(qp_file)
            qp_file.close()
        

        # unique_queries = pickle.load(
        #     open(
        #         os.path.join('models', 'query_pickles',
        #                      'queries_' + file_suffix + '.pth'), 'rb'))
        query_index = faiss.read_index(
            os.path.join(embedding_path,
                         'embedding_' + file_suffix + '.index'))

    else:
        client = mongo_log_client
        # client = MongoConnection.getInstance()
        if project_id is not None and client_id is not None:

            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find(
                    {
                        "projectId": {"$in": [int(project_id), str(project_id)]},
                        "clientId": {"$in": [int(client_id), str(client_id)]},
                        **relatedsearch_configuration_flags
                    }, {'query', 'timestamp'})
        elif project_id is not None and client_id is None:
            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find(
                    {
                        "projectId": {"$in": [int(project_id), str(project_id)]},
                        **relatedsearch_configuration_flags
                    }, {'query', 'timestamp'})
        elif project_id is None and client_id is not None:
            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find(
                    {
                        "clientId": {"$in": [int(client_id), str(client_id)]},
                        **relatedsearch_configuration_flags
                    }, {'query', 'timestamp'})
        else:
            query_cursor = client[search_analytics_db_name][
                search_analytics_collections_name].find(
                    {**relatedsearch_configuration_flags},
                    {'query', 'timestamp'})

        all_data = [dict(i) for i in query_cursor if i.get('query', 0) != 0]
        # unique_queries  = np.unique(list(findkeys(all_data, 'query'))).tolist()
        lowercased_query = list(
            map(lambda x: x.lower().strip(), findkeys(all_data, 'query')))
        ascci_qeuries = list(map(convert_unidecode, lowercased_query))
        unique_queries = np.unique(ascci_qeuries).tolist()
        logger.debug('[Related Search] Saving unique query in  Pickel format')
        with open (os.path.join('models', 'query_pickles','queries_' + file_suffix + '.pth'), 'wb') as write_pickle_file:
            pickle.dump(list(unique_queries),write_pickle_file)
            write_pickle_file.close()

        # pickle.dump(
        #     list(unique_queries),
        #     open(
        #         os.path.join('models', 'query_pickles',
        #                      'queries_' + file_suffix + '.pth'), 'wb'))

        query_index = return_query_index(embedder, unique_queries, project_id,
                                         client_id)

    return unique_queries, query_index


def create_embedding_query_index_file(embedder, project_id, client_id):
    """reutrns faiss index and unique queries for all the queries present in Mongo"""
    file_suffix = suffix_client_project(project_id, client_id)
    parameters = get_parameters()
    search_analytics_db_name = parameters.get("DEFAULT",
                                              "search_analytics_db_name")

    # if model_embedding_file.is_file():
    #     flag = True
    #     unique_queries = pickle.load(
    #         open(os.path.join('models', 'query_pickles', 'queries_' + file_suffix + '.pth'), 'rb'))
    #     query_index = faiss.read_index(os.path.join(embedding_path, 'embedding_' + file_suffix + '.index'))

    # else:
    client = mongo_log_client
    # client = MongoConnection.getInstance()
    logger.debug(f'projectId: {type(project_id)} clientId: {type(client_id)}')
    if project_id is not None and client_id is not None:
        query_cursor = client[search_analytics_db_name][
            search_analytics_collections_name].find(
                {
                    "projectId": {"$in": [int(project_id), str(project_id)]},
                    "clientId": {"$in": [int(client_id), str(client_id)]},
                    **relatedsearch_configuration_flags
                }, {'query', 'timestamp'})

    all_data = [dict(i) for i in query_cursor if i.get('query', 0) != 0]
    # logger.debug(all_data , 'all_data from Mongodb')
    # unique_queries  = np.unique(list(findkeys(all_data, 'query'))).tolist()
    all_queries = list(map(lambda x: x.strip(), findkeys(all_data, 'query')))
    processed_qeuries = list(
        map(trendingsearch_relatedsearch_widget_cleaner, all_queries))
    unique_queries = np.unique(
        list(map(lambda x: x.lower(), processed_qeuries))).tolist()
    not_allwed_punctuations_pattern = re.compile(
        r'''[!\"#'\(\)\*\+,\/:;<=>\?@\[\\\]\^_`{\|}~’”“]''', flags=0)
    allowed_punctuation_pattern = re.compile(r"[$%&-.]", flags=0)
    unique_queries = [
        i for i in unique_queries
        if valid_queries(allowed_punctuation_pattern, i)
    ]
    unique_queries = [
        i for i in unique_queries
        if len(not_allwed_punctuations_pattern.findall(i)) == 0
    ]
    delete_old_files(client_id, project_id, "RelatedSearch")
    logger.debug('[Related Search] Saving unique query in  Pickel format')
    related_search_query_pickle_path = parameters.get("related_search",
                                                      "pickle_path")

    searchqueries_filepath = os.path.join(related_search_query_pickle_path,
                                          'queries_' + file_suffix + '.pth')
    with open(searchqueries_filepath, 'wb') as searchquery_file:
        pickle.dump(list(unique_queries), searchquery_file)
        searchquery_file.close()
    logger.debug(
        '[Related Search] Saving query embeddings in  faiss index format')
    model_embedding_filepath = return_query_index(embedder, unique_queries,
                                                  project_id, client_id)

    return searchqueries_filepath, model_embedding_filepath


def delete_old_files(client_id, project_id, job_Name):
    client = mongo_log_client
    parameters = get_parameters()
    main_database_name = parameters.get("DEFAULT","main_database_name")
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


def emebbding_file(project_id, client_id):
    """Naming convention for embedding files"""
    file_suffix = suffix_client_project(project_id, client_id)
    my_file = Path(
        os.path.join(embedding_path, "embedding_" + file_suffix + ".index"))
    return my_file


def return_query_index(embedder, unique_queries, project_id, client_id):
    """creating and saving faiss index of all the unique queries for repespective project and clients """
    file_suffix = suffix_client_project(project_id, client_id)
    parameters = get_parameters()
    related_search_embedding_path = parameters.get("related_search",
                                                   "embedding_path")
    corpus_embeddings = embedder.encode(unique_queries, convert_to_tensor=True)
    embeddings_index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
    faiss.normalize_L2(corpus_embeddings.numpy())
    embeddings_index.add_with_ids(
        corpus_embeddings.numpy(),
        np.array(range(0, len(unique_queries))).astype(np.int64))
    all_query_embeddings_filepath = os.path.join(
        related_search_embedding_path, 'embedding_' + file_suffix + '.index')
    faiss.write_index(embeddings_index, all_query_embeddings_filepath)
    return all_query_embeddings_filepath
    # return embeddings_index
