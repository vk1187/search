from elasticsearch import Elasticsearch

import config_e as config

es_conn = None


def connect_elastic(ip, port):
    # Connect to an elasticsearch node with the given ip and port
    global es_conn

    es_conn = Elasticsearch([{"host": ip, "port": port}])
    if es_conn.ping():
        print("Connected to elasticsearch...")
    else:
        print("Elasticsearch connection error...")
    return es_conn


def create_qa_index():
    # Define the index mapping
    index_body = {
        "mappings": {
            "properties": {
                "question": {
                    "type": "text"
                },
                "answer": {
                    "type": "text"
                },
                "question_vec": {
                    "type": "dense_vector",
                    "dims": 300
                },
                "answer_vec": {
                    "type": "dense_vector",
                    "dims": 300
                },
                "q_id": {
                    "type": "long"
                }
            }
        }
    }
    try:
        # Create the index if not exists
        if not es_conn.indices.exists(config.settings.INDEX_NAME):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es_conn.indices.create(
                index="covid-qa", body=index_body, ignore=[400, 404]
            )
            print("Created Index -> covid-qa")
        else:
            print("Index covid-qa exists...")
    except Exception as ex:
        logger.error(f'{ex}')
        logger.exception(e)
        # print(str(ex))


def reindex_qa():
    try:
        if es_conn.indices.exists(config.settings.INDEX_NAME):
            es_conn.indices.delete(index=config.settings.INDEX_NAME, ignore=[400, 404])
            print("Deleted Index -> ", config.settings.INDEX_NAME)
        else:
            print("Index -> ", config.settings.INDEX_NAME, " does not exist")
    except Exception as ex:
        logger.error(f'{ex}')
        logger.exception(ex)


def insert_qa(body):
    if not es_conn.indices.exists(config.settings.INDEX_NAME):
        create_qa_index()
    # Insert a record into the es index
    es_conn.index(index=config.settings.INDEX_NAME, body=body, id=int(body['q_id']))
    # print("QA successfully inserted...")


def semantic_search(query_vec, thresh=1.2, top_n=10):
    # Retrieve top_n semantically similar records for the given query vector
    if not es_conn.indices.exists(config.settings.INDEX_NAME):
        return "No records found"
    s_body = {
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": "0.3*cosineSimilarity(params.query_vector,'answer_vec') + 0.7*cosineSimilarity(params.query_vector,'question_vec') + 1.0",
                    "params": {"query_vector": query_vec}
                }
            }
        }
    }
    # Semantic vector search with cosine similarity
    result = es_conn.search(index=config.settings.INDEX_NAME, body=s_body)
    total_match = len(result["hits"]["hits"])
    print("Total Matches: ", str(total_match))
    # print(result)
    data = []
    if total_match > 0:
        q_ids = []
        for hit in result["hits"]["hits"]:
            if hit['_score'] > thresh and hit['_source']['q_id'] not in q_ids and len(data) <= top_n:
                print(
                    "--\nscore: {} \n question: {} \n answer: {}\n--".format(hit["_score"], hit["_source"]['question'],
                                                                             hit["_source"]['answer']))
                q_ids.append(hit['_source']['q_id'])
                data.append({'question': hit["_source"]['question'], 'answer': hit["_source"]['answer']})
    return data


def keyword_search(query, thresh=1.2, top_n=10):
    # Retrieve top_n records using TF-IDF scoring for the given query vector
    if not es_conn.indices.exists(config.settings.INDEX_NAME):
        return "No records found"
    k_body = {
        "query": {
            "match": {
                "question": query
            }
        }
    }

    # Keyword search
    result = es_conn.search(index=config.settings.INDEX_NAME, body=k_body)
    total_match = len(result["hits"]["hits"])
    print("Total Matches: ", str(total_match))
    # print(result)
    data = []
    if total_match > 0:
        q_ids = []
        for hit in result["hits"]["hits"]:
            if hit['_score'] > thresh and hit['_source']['q_id'] not in q_ids and len(data) <= top_n:
                print(
                    "--\nscore: {} \n question: {} \n answer: {}\n--".format(hit["_score"], hit["_source"]['question'],
                                                                             hit["_source"]['answer']))
                q_ids.append(hit['_source']['q_id'])
                data.append({'question': hit["_source"]['question'], 'answer': hit["_source"]['answer']})
    return data
