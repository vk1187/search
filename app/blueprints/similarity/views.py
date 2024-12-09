import re

from flask_restx import Resource

from app.services.config_constants import api_SynonymExpansion_industry_domain
from app.services.config_constants import api_SynonymExpansion_ner_expansion, \
    api_SynonymExpansion_enableSynonymExpansion
from app.services.config_constants import api_SynonymExpansion_query, api_SynonymExpansion_client_id
# from app.services.config_constants import relevant_query_gensim_flag
# from app.services.config_constants import relevant_query_sense2vec_flag
from app.services.similarity_engine import SynonymExpansionOutput
from load_parameters import get_parameters
from custom_logging import logger
from . import document_input
from . import query_input
from . import query_synonym_input
from . import similarity_api
from ...services.config_constants import regex_latin_characters
from ...services.similarity_engine.preprocessor_data import DataHandler
from ...services.similarity_engine.preprocessor_query import QueryHandler
from ...services.similarity_engine.vector_representation import TextEmbeddings
from ...services.utils import DataPreprocessor
from authenitcation.auth import token_required


@similarity_api.route('/query')
class Query(Resource):

    @similarity_api.expect(query_input)
    def post(self):
        text = similarity_api.payload.get('input_query', '')
        embedder = TextEmbeddings(text)
        return embedder.show_vector()


@similarity_api.route('/token_analysis')
class token_analysis(Resource):

    @similarity_api.expect(query_input)
    def post(self):
        text = similarity_api.payload.get('input_query', '')

        if text != '':
            input_query = QueryHandler(text)
            result = input_query.token_analysis()
            return result
        else:
            return ''


@similarity_api.route('/synonym_expansion')
class SynonymExpansion(Resource):
    """return similar tokens for the input words of seatch query"""

    @similarity_api.expect(query_synonym_input)
    # @token_required
    def post(self):
        """
        Post request to return synonym expansion, intent based query, entities and tokens with whitespace based on  input
        """

        try:
            parameters = get_parameters()
            relevant_query_sense2vec_flag = parameters.getboolean(
                "similarity", "relevant_query_sense2vec_flag")
            relevant_query_gensim_flag = parameters.getboolean(
                "similarity", "relevant_query_gensim_flag")
            text = re.sub(
                r" {1,}", r" ",
                similarity_api.payload.get(api_SynonymExpansion_query, ''))
            client_id = similarity_api.payload.get(
                api_SynonymExpansion_client_id, '')

            ner_expansion_flag = similarity_api.payload.get(
                api_SynonymExpansion_ner_expansion, False)
            industry_domain = similarity_api.payload.get(
                api_SynonymExpansion_industry_domain, 'All')
            enable_synonym_expansion = similarity_api.payload.get(
                api_SynonymExpansion_enableSynonymExpansion, True)
            if text != '':
                updated_text = re.sub(regex_latin_characters, ' ', text)
                # updated_text = text
                query_expansion_obj = QueryHandler(updated_text,
                                                   ner_expansion_flag,
                                                   industry_domain,
                                                   enable_synonym_expansion,
                                                   client_id)
                return query_expansion_obj.relevant_query_tokens(
                    sense2vec_flag=relevant_query_sense2vec_flag,
                    gensim_flag=relevant_query_gensim_flag)
            else:
                return SynonymExpansionOutput().return_output()
        except Exception as e:
            logger.error(
                f'[Synonym Expanison view] Unable to process the input for Synonym expansion for input: {text}'
            )
            logger.error(f'{e}')
            logger.exception(e)


@similarity_api.route('/document')
class Document(Resource):

    @similarity_api.expect(document_input)
    def post(self):
        document = similarity_api.payload.get('document', '')
        vectors = []
        text = DataPreprocessor(document)
        data_handler = DataHandler(text())
        for i in data_handler()['Splitted Documents']:
            vectors.append(TextEmbeddings(i).show_vector())
        return vectors
