import os
import time

from flask_restx import Resource

# from sentence_transformer_factory.stc.helper import SentenceTransformerInstance
from app.services import embedder as SentenceTransformerEmbedder
# from app.services.config_constants import relatedentity_similarity_threshold_default_percent, widget_top_counter
from app.services.related_search_engine.helper import create_embedding_query_index_file, pickle_vector_index_values, \
    pickle_vectorindex_path, outputFormatRelatedQueryEmbedding
from app.services.related_search_engine.related_search_factory import RelatedSearch
from app.services.similarity_engine.operator_management import QueryOperationHandler
from app.services.utils import flatten
from authenitcation.auth import token_required
from custom_logging import logger
from . import related_query_api, query_input, embedding_input

from load_parameters import get_parameters



@related_query_api.route('/return_related_queries')
class RelatedQuery(Resource):
    """returns related search terms for the input search term through sentence transformer model"""

    @related_query_api.expect(query_input)
    # @token_required
    def post(self):
        try:
            parameters = get_parameters()
            default_threshold_percent = parameters.getint(
                "related_search", "default_threshold_percent")
            widget_top_counter = parameters.getint("related_search",
                                                   "widget_top_counter")

            tic = time.time()
            logger.info(f"[Related Search] Finding Related queries'")

            if related_query_api.payload in [
                    None, [], '', ' ', {}
            ] or related_query_api.payload.get(
                    'query', None) in [None, [], '', ' ', {}]:
                logger.warning(
                    f'Please pass input parameters for [related query]')
                return {
                    'result': "Error - No Input/invalid Input is passed",
                    "eta": time.time() - tic,
                    "status": False
                }

            query = related_query_api.payload.get('query', None)
            project_id = int(related_query_api.payload.get('project_Id', -1))
            client_id = int(related_query_api.payload.get('client_Id', -1))
            similarity_threshold_percent = related_query_api.payload.get(
                'similarity_threshold_percent', default_threshold_percent)
            top_counter = related_query_api.payload.get(
                'top_counter', widget_top_counter)

            if query is None:
                return {
                    'result': "Error - No Input is passed",
                    "eta": time.time() - tic,
                    "status": False
                }

            pickle_path, vector_index_path = pickle_vectorindex_path(
                project_id, client_id)
            unique_queries, query_index = pickle_vector_index_values(
                vector_index_path, pickle_path)

            self.query_operator_obj = QueryOperationHandler(query)
            token_to_be_removed = list(
                flatten(self.query_operator_obj.negative_tokens))
            updated_search_query, _, _, _ = self.query_operator_obj()

            output = RelatedSearch.search(
                index=query_index,
                query=(query, updated_search_query),
                model=SentenceTransformerEmbedder,
                corpus=unique_queries,
                threshold_score=similarity_threshold_percent / 100,
                negative_tokens=token_to_be_removed,
                widget_counter=top_counter)

            return {
                'result': output,
                'eta': time.time() - tic,
                "status": False if
                (output is None) or len(output) == 0 else True
            }
        except Exception as e:
            logger.error(
                f'[related search view] Unable to process the input for related search term for search term: {query}'
            )
            logger.error(f'{e}')
            logger.exception(e)
            return {
                'result': "Error - No Input is passed",
                "eta": time.time() - tic,
                "status": False
            }


@related_query_api.route('/create_query_embeddings')
class RelatedQueryEmbedding(Resource):
    """returns related search terms for the input search term through sentence transformer model"""

    @related_query_api.expect(embedding_input)
    # @token_required
    def post(self):
        try:

            tic = time.time()
            logger.info(
                f"[Related Search] Creating Related queries Embeddings")
            query_pickle_name, query_vector_index_name = None, None
            project_id = related_query_api.payload.get('project_id', None)
            client_id = related_query_api.payload.get('client_id', None)
            logger.info(
                f"[Related Search] Creating Related queries Embeddings for project_id {project_id} and client_id {client_id}"
            )

            if related_query_api.payload in [None, [], '', ' ', {}]:
                logger.warning(
                    f'Please pass input parameters for [related query]')
                return outputFormatRelatedQueryEmbedding(
                    False, client_id, project_id, query_pickle_name,
                    query_vector_index_name, None, None, tic)

            if (project_id is None) or (client_id is None):
                return outputFormatRelatedQueryEmbedding(
                    False, client_id, project_id, query_pickle_name,
                    query_vector_index_name, None, None, tic)

            # model_embedding_file = emebbding_file(project_id, client_id)
            # embedder = SentenceTransformerInstance.getInstance()
            searchqueries_filepath, model_embedding_filepath = create_embedding_query_index_file(
                SentenceTransformerEmbedder, project_id, client_id)
            basename_searchqueries_pickle = os.path.basename(
                searchqueries_filepath)
            basename_embeddings_index = os.path.basename(
                model_embedding_filepath)
            dirname_searchqueries_pickle = os.path.dirname(
                searchqueries_filepath)
            dirname_embeddings_index = os.path.dirname(
                model_embedding_filepath)

            # output = RelatedSearch.search(index=query_index,
            #                                        query=query,
            #                                        model=embedder,
            #                                        corpus=unique_queries,
            #                                        threshold_score=similarity_threshold_percent/100
            #                                        )

            return outputFormatRelatedQueryEmbedding(
                True, client_id, project_id, basename_searchqueries_pickle,
                basename_embeddings_index, dirname_searchqueries_pickle,
                dirname_embeddings_index, tic)

            # {'result': output,
            #         'eta': time.time() - tic,
            #         "status":False if (output is None) or len(output)==0 else True}
        except Exception as e:

            logger.error(
                f'[related search view] Unable to process the input for related search term  during pickle creation'
            )
            logger.error(f'{e}')
            logger.exception(e)
            return outputFormatRelatedQueryEmbedding(False,
                                                     client_id,
                                                     project_id,
                                                     query_pickle_name,
                                                     query_vector_index_name,
                                                     tic=tic)
