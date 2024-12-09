from app.services.config_constants import *
from app.services.similarity_engine import ExpansionHelper
from app.services.utils import DataPreprocessor
from custom_logging import logger


class TokenAnalysis:
    def __init__(self, search_query=None, query_tokens=None, doc=None, init_entities=None, init_tokens=None):
        # basic_split = None,
        # spacy_split = None,
        # input_expansion_list = None,
        # raw_data = None,
        # extracted_phrases = None,
        # search_query_entities = None,
        # search_query_remaining_tokens = None

        # self.basic_split = '' if basic_split is None else basic_split
        # self.spacy_split = '' if spacy_split is None else spacy_split
        # self.input_expansion_list = '' if input_expansion_list is None else input_expansion_list
        # self.raw_data = '' if raw_data is None else raw_data
        # self.extracted_phrases = '' if extracted_phrases is None else extracted_phrases
        # self.search_query_entities = '' if search_query_entities is None else search_query_entities
        # self.search_query_remaining_tokens = '' if search_query_remaining_tokens is None else search_query_remaining_tokens

        self.search_query = '' if search_query is None else search_query
        self.query_tokens = [''] if query_tokens is None else query_tokens
        self.doc = '' if doc is None else doc
        self.init_entities = '' if init_entities is None else init_entities
        self.init_tokens = '' if init_tokens is None else init_tokens

    def tokens(self):
        """returns tokens feasible thorugh input query"""
        logger.info(f'In function {self.tokens.__qualname__}')
        logger.info(f'{self.tokens.__qualname__}.basic_split-->{self.query_tokens}')
        basic_split = self.query_tokens

        spacy_split = [i.text for i in self.doc]
        logger.info(f'{self.tokens.__qualname__}.spacy_split-->{spacy_split}')
        search_query_entities = self.init_entities
        logger.info(f'{self.tokens.__qualname__}.search_query_entities-->{search_query_entities}')
        search_query_remaining_tokens = self.init_tokens
        logger.info(f'{self.tokens.__qualname__}.search_query_remaining_tokens-->{search_query_remaining_tokens}')
        input_expansion_list = ExpansionHelper.case_insensitive_unique_list(basic_split + spacy_split)
        raw_data = DataPreprocessor(' '.join(input_expansion_list), strip_punctuation_flag)()
        extracted_phrases = DataPreprocessor(self.search_query, phrase_extraction_flag)()
        return self.token_results(basic_split, spacy_split, input_expansion_list, raw_data, extracted_phrases,
                                  search_query_entities, search_query_remaining_tokens)

    def token_results(self, basic_split, spacy_split, input_expansion_list, raw_data, extracted_phrases,
                      search_query_entities, search_query_remaining_tokens):
        """output format"""
        return {tokenanalysis_basic_split: basic_split, tokenanalysis_spacy_split: spacy_split,
                tokenanalysis_input_expansion_list: input_expansion_list, tokenanalysis_raw_data: raw_data.split(),
                tokenanalysis_extracted_phrases: extracted_phrases,
                tokenanalysis_search_query_entities: search_query_entities,
                tokenanalysis_search_query_remaining_tokens: search_query_remaining_tokens}
