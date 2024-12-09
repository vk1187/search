import itertools
import time
from collections import defaultdict

import numpy as np
# from flask_restx import Api
from flask_restx import Resource

# from app.services.utils import error_message
from custom_logging import logger
# from ...services.ner_engine.utils import output_format
from . import api, es_input
from load_parameters import get_parameters
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from datetime import datetime
import json
import os

# Import the LexRank summarizer

import re
from sumy.summarizers.lex_rank import LexRankSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from app.services.extractive_summarization.helper import document_preprocessing,sentence_tokenizer


@api.route('/return_summary')
class NER(Resource):
    """Class to return entities present in the given input"""

    @api.expect(es_input)
    # @token_required
    def post(self):
        """
        Post request to return summary of the given input data
        :param data: [{"record_id":1,"pages":"samople data"}]
        :param client_id:
        return entities
        """
        try:

            logger.info("Parsing the document for summary processing")
            parameters = get_parameters()
            tic = time.time()
            if api.payload in [None, [], '', ' ']:
                logger.warning(f'Please pass input parameters for [Extractive Summarization]')
                return {'result': None, 'time': time.time() - tic}
#
            try:
                language = parameters.get("extractive_summarization", "language")
                number_of_sentences = parameters.get("extractive_summarization", "summary_count")
                words_per_sentences = parameters.get("extractive_summarization", "number_of_words_per_sentences")

                client_id = api.payload['client_id']
                project_id = api.payload['project_id']
                input_data = api.payload['data'].copy()
                sentence_count = api.payload.get('sentence_count',number_of_sentences)
                number_of_words_per_sentences = api.payload.get('number_of_words_per_sentences',words_per_sentences)
                # sentence_count = api.payload['sentence_count']
                


                stemmer = Stemmer(language)
                # result={}
                summarizer = Summarizer(stemmer)
                summarizer.stop_words = get_stop_words(language)
                count = 0
                es_file_name = os.path.join("esa_input",'extractive_summarization_input_'+str(datetime.now().strftime("%d_%m_%Y_%H_%M_%S")) +'.json')
                os.makedirs(os.path.dirname(es_file_name),exist_ok=True)
                with open(es_file_name,'w',encoding='utf8') as file:
                    json.dump(api.payload,file)
                tic = time.time()
                for data_dictionary in api.payload['data']:
                    
                    preprocessed_text=sentence_tokenizer(data_dictionary['pages'])
                    
                    
                    count += 1
                    # print(f'Summarizing for Record {count} : {data_dictionary["id"]} ', end='\n')
                    logger.info(f'Summarizing for Record {count} : {data_dictionary["id"]}')
                    preprocessed_text = document_preprocessing(preprocessed_text,words_per_sentence_threshold=number_of_words_per_sentences)
                    results = ''
                    page_parser = PlaintextParser.from_string(
                        '. '.join(list(map(str.capitalize,preprocessed_text))), Tokenizer(language))
                    
                    for sentence in summarizer(page_parser.document, int(sentence_count)):
                        sentence = re.sub(r'\.{2,}', '.', str(sentence))
                        results+=' '+str(sentence)
                        # results.append(' '.join(sentence._text))
                    data_dictionary["summary"]=results.strip()
                    del data_dictionary['pages']


            except Exception as exception_all:
                logger.error(exception_all)
                logger.exception(exception_all)
                return {'result': None, 'time': time.time() - tic,'status':False}

            # result = {
            #     doc_id: cleaning_output(temp_dict[doc_id])
            #     for doc_id in temp_dict
            # }
            # del temp_dict


# results
# result_spacy_ner = SpacyService.extract_entities(document)
# logger.debug(f'{result_spacy_ner} -- OutputFormat')
# document = api.payload['document']
# return result_spacy_ner[1]
            return {'result': api.payload, 'time': time.time() - tic,'status':True}
        except Exception as exc:
            logger.error(
                '[ExtractiveSumarization] View is not able to process the input'
            )
            logger.exception(f'{exc}')
