import json
import os
import time

import nltk
import numpy as np
import truecase
from flask_restx import Resource

# from app.services.config_constants import pasf_entities, relatedentity_similarity_threshold_default_percent, \
#     widget_top_counter
from app.services.ner_engine.ml_model.spacy import SpacyService
from app.services.related_entities.helper import emebedding_entity_path, read_query_index, read_idx2tok, \
    entity_pickle_vectorindex_path
from app.services.related_entities.related_entity_factory import RelatedEntity
from app.services.utils import DataPreprocessor
from authenitcation.auth import token_required
from custom_logging import logger
from . import api, document_input, entity_input_filenames

from load_parameters import get_parameters

nltk.download('punkt')


@api.route('/return_related_entities')
class RelatedEntities(Resource):
    """Class to return entities present in the given input"""

    @api.expect(document_input)
    # @token_required
    def post(self):
        """
        Post request to return similar entities based on the given entity for client_id,project_id
        """
        try:
            parameters = get_parameters()
            pasf_entities = parameters.get("related_entity",
                                           "allowed_entities")
            default_threshold_percent = parameters.getint(
                "related_entity", "default_threshold_percent")
            widget_top_counter = parameters.getint("related_entity",
                                                   "widget_top_counter")

            logger.info(f"Parsing the input for related entities")
            # print(api.payload)
            # print
            tic = time.time()
            data = api.payload.copy()
            search_term = None if not isinstance(
                data.get('search_query', None), str) else data.get(
                    'search_query', None).strip()
            client_id = int(data.get('client_id', -1))
            project_id = int(data.get('project_id', -1))
            isClicked = data.get('isClicked', False)
            top_counter = data.get('top_counter', widget_top_counter)
            # embedding_index_filename = data.get('embedding_index_filename',None)
            # entity_pickle_filename = data.get('entity_pickle_filename',None)
            similarity_threshold_percent = data.get(
                'similarity_threshold_percent', default_threshold_percent)

            if data in [None, [], '', ' '
                        ] or search_term in [None, [], '', ' ']:
                logger.warning(
                    f'Please pass valid input parameters for [related entities]'
                )
                return {
                    'related_entities': None,
                    'time': time.time() - tic,
                    "status": False
                }
            # Reading Pickle Files
            entity_pickle_filename, embedding_index_filename = entity_pickle_vectorindex_path(
                project_id, client_id) #file name
            faiss_entity_index_path, entity_tok2idx_path = emebedding_entity_path(
                embedding_index_filename, entity_pickle_filename) #file complete path
            faiss_entity_index, entity_data = read_query_index(
                faiss_entity_index_path), read_idx2tok(entity_tok2idx_path) # reading file
            entity_idx2tok = entity_data["idx2tok"]
            entity_idx2entities = entity_data["idx2entities"]
            tok_filter = {j: 1 for i, j in entity_idx2tok.items()}
            entity_tok2idx = entity_data["tok2idx"]

            # Preprocessing the input
            data_obj = DataPreprocessor(search_term)
            data_obj.clean_punctuations_start_stop()
            clean_term = data_obj.document

            # Calling the NER engine
            nlp_search_term, custom_entities = SpacyService.extract_entities(
                clean_term, client_id)
            entity_index = entity_tok2idx.get(nlp_search_term.text.lower(), -1)

            # Check if the search term(entity) is not present already in the index
            if entity_index != -1:
                query_entity = [entity_idx2entities[entity_index]]
            else:
                query_entity = [
                    i for i in custom_entities['entities']
                    if len(nlp_search_term.ents) == 1 and (
                        nlp_search_term.ents[0].text == nlp_search_term.text)
                    and len(custom_entities['entities'][i]) == 1
                    and i in pasf_entities
                ]
                # logger.debug(
                #     f'{nlp_search_term.ents},{nlp_search_term.ents[0].text}')
            if query_entity:
                spacy_transformer_enabled = json.loads(parameters.get("ner","spacy_transformer_enabled").lower())
                if spacy_transformer_enabled == True:
                    inp_text = nlp_search_term.text # Converting transformers/Large Model entity output to plain text
                    inp_text = truecase.get_true_case(
                            "," +
                            inp_text)[1:].strip()
                    query_text = SpacyService.model_doc_lg(inp_text) # Passing plain entity text to model
                    query_vector = query_text.vector[None, :] # getting entity vector
                else: 
                    query_vector = nlp_search_term.vector[None, :]
                

                if np.all((query_vector == 0)):
                    raise Exception(
                        f"Query vector is all zeros for {nlp_search_term.text} i.e Vector Embedding does not exist in the spacy model"
                    )
                # if (tok_filter[search_term]==1) or  (len(nlp_search_term.ents) == 1 and (nlp_search_term.ents[0].text == nlp_search_term.text)):

                # return related entities based on input and pickles
                related_entities_list = RelatedEntity.search(
                    entity_idx2tok=entity_idx2tok,
                    entity_idx2entities=entity_idx2entities,
                    query_index=faiss_entity_index,
                    query_vector=query_vector,
                    query_entity=query_entity,
                    input_query=search_term,
                    top_counter=top_counter,
                    similarity_threshold_percent=similarity_threshold_percent /
                    100)
                return {
                    'related_entities': related_entities_list,
                    'time': time.time() - tic,
                    "status": True if len(related_entities_list) > 0 else False
                }
            else:
                return {
                    'related_entities': None,
                    'time': time.time() - tic,
                    "status": False
                }

        except Exception as e:
            logger.error(
                f'[RelatedEntities.return_related_entities] View is not able to process the input term {search_term}'
            )
            logger.error(f'{e}')
            logger.exception(f'{e}')
            return {
                'related_entities': None,
                'time': time.time() - tic,
                "status": False
            }


def outputFormatEntityVectorIndexing(status,
                                     client_id,
                                     project_id,
                                     entity_pickle_name,
                                     entity_vector_index_name,
                                     entity_pickle_location=None,
                                     entity_vector_index_location=None,
                                     tic=0):
    return {
        "status": status,
        "client_id": client_id,
        "project_id": project_id,
        'pickle_location': entity_pickle_location,
        'vector_index_location': entity_vector_index_location,
        'pickle_name': entity_pickle_name,
        'vector_index_name': entity_vector_index_name,
        'run_time': time.time(),
        'execution_time': time.time() - tic
    }


@api.route('/create_vector_represenation')
class EntityVectorIndexing(Resource):
    """Class to save vector representation of entities and save in faiss index"""

    @api.expect(entity_input_filenames)
    # @token_required
    def post(self):
        """
        create embeddings and save in faiss index
        """
        try:

            logger.info("Parsing the document for EntityVectorIndexing'")
            # print(api.payload)
            # print
            entity_pickle_name = None
            entity_vector_repr_name = None
            tic = time.time()
            data = api.payload.copy()
            client_id = data.get('client_id', None)
            project_id = data.get('project_id', None)
            entities = data.get('entities', None)
            # json.dump(api.payload, open("PASF_all_entities.json", "w"))
            if data in [None, [], '', ' ']:
                logger.warning(
                    f'[create_vector_represenation] Please pass valid values in API'
                )
                return outputFormatEntityVectorIndexing(
                    False,
                    client_id,
                    project_id,
                    entity_pickle_name,
                    entity_vector_repr_name,
                    tic=tic)

            if client_id is None or project_id is None or entities is None or len(
                    list(entities.keys())) == 0:
                logger.warning(
                    f'[create_vector_represenation] Please pass valid values in API'
                )
                return outputFormatEntityVectorIndexing(
                    False,
                    client_id,
                    project_id,
                    entity_pickle_name,
                    entity_vector_repr_name,
                    tic=tic)

            entity_pickle_name, entity_vector_repr_name = RelatedEntity.save_indexes(
                entities, project_id, client_id)
            basename_entity_pickle = os.path.basename(entity_pickle_name)
            basename_entity_embeddings_index = os.path.basename(
                entity_vector_repr_name)
            dirname_entity_pickle = os.path.dirname(entity_pickle_name)
            dirname_entity_embeddings_index = os.path.dirname(
                entity_vector_repr_name)

            if (entity_pickle_name is not None) and (entity_vector_repr_name
                                                     is not None):
                return outputFormatEntityVectorIndexing(
                    True, client_id, project_id, basename_entity_pickle,
                    basename_entity_embeddings_index, dirname_entity_pickle,
                    dirname_entity_embeddings_index, tic)

            else:
                return outputFormatEntityVectorIndexing(
                    False,
                    client_id,
                    project_id,
                    entity_pickle_name,
                    entity_vector_repr_name,
                    tic=tic)

        except Exception as e:
            logger.debug(
                '[EntityVectorIndexing] View is not able to process the input')
            logger.error(f'{e}')
            logger.exception(e)
            return outputFormatEntityVectorIndexing(False, client_id,
                                                    project_id,
                                                    entity_pickle_name,
                                                    entity_vector_repr_name,
                                                    tic)
