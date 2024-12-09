import time

from flask_restx import Resource

from app.services.auto_suggestion_engine.helper import auto_suggestion_generation, \
    output_format, sentence_splitter, \
    transform_data
from app.services.config_constants import auto_completion_max_shingle_length, \
    ExcludeAlphaNumericSuggestionFlag
# from app.services.ner_engine.ml_model.spacy import SpacyService
from custom_logging import logger
from . import autosuggestion_api, document_input
import json
# import mem_top

@autosuggestion_api.route('/return_suggestions')
class AutoSuggestion(Resource):
    """Class to return ngram suggestions based on the the given input document"""

    @autosuggestion_api.expect(document_input)
    # @token_required
    def post(self):
        """
        Post request for calling auto suggestion engine
        :param SuggestionGrm_Limit:
        :param AutoSuggestionInputData
        :param ExcludeAlphaNumericSuggestion

        """
        try:
            logger.info(
                "[autosuggestion_api] Parsing the document for generation of auto suggestions"
            )
            tic = time.time()
            if autosuggestion_api.payload in [None, [], '', ' ']:
                logger.error(
                    'Please pass input parameters for [autosuggestion_api]')
                return {'suggestions': None, 'time': time.time() - tic}

            try:
                # logger.debug(mem_top.mem_top())
                max_shingle = autosuggestion_api.payload.get(
                    'SuggestionGrm_Limit', auto_completion_max_shingle_length)
                input_data = autosuggestion_api.payload.get(
                    'AutoSuggestionInputData', [])
                exclude_alpha_numeric_suggestion = autosuggestion_api.payload.get(
                    'ExcludeAlphaNumericSuggestion',
                    ExcludeAlphaNumericSuggestionFlag)
                # json.dump(autosuggestion_api.payload, open("autosuggestion_api_input.json", "w"))
                # logger.debug(mem_top.mem_top())
                with open('autosuggestion_input_api.json','w',encoding='utf8') as f:
                    json.dump(autosuggestion_api.payload,f)
                
                data = transform_data(input_data)
                
                # logger.debug(mem_top.mem_top())
                data = sentence_splitter(data)
                # logger.debug(mem_top.mem_top())
                result = auto_suggestion_generation(
                    data,
                    max_shingle_length=max_shingle + 1,
                    ExcludeAlphaNumericSuggestion=exclude_alpha_numeric_suggestion
                )
                # logger.debug(mem_top.mem_top())
                del data

            except Exception as e:
                logger.exception(e)
                logger.error(e)
                return {'suggestions': None, 'time': time.time() - tic}
            # json.dump(output_format(result,'suggestions', tic=tic), open('new_suggestions_output.json', 'w', encoding='utf-8'))
            return output_format(result, 'suggestions', tic=tic)
        except Exception as api_error:

            logger.error(
                '[autosuggestion_api] View is not able to process the input')
            logger.exception(api_error)
            logger.error(api_error)
            return {
                'suggestions': None,
                'time': time.time() - tic,
                "error_message": api_error
            }
