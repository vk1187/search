import time

from flask_restx import Resource

from app.services.auto_correction_engine.autocorrection_factory import InputEngine
from app.services.config_constants import api_autocorrectexpansion_query
# from authenitcation.auth import token_required
from custom_logging import logger
from . import autocorrection_api
from . import query_input


@autocorrection_api.route('/output')
class Query(Resource):
    """AutoCorrectio based on Levenstien and Soundex"""

    @autocorrection_api.expect(query_input)
    # @token_required
    def post(self):
        """Post request for auto correction to return the correct word.
        :param input_query:
        :param index_name:
        :param project_id:
        :param client_id:
        """
        try:
            inp_time = time.time()
            text = autocorrection_api.payload.get('input_query', '').strip()
            index_name = autocorrection_api.payload.get('index_name', '')
            project_id = autocorrection_api.payload.get('project_id', '')
            client_id = autocorrection_api.payload.get('client_id', '')
            if isinstance(project_id, list) and len(project_id) == 1:
                project_id = project_id[0]

            # client = MongoConnection.getInstance()
            # collection = client[search_analytics_database_name][search_analytics_collections_name]
            # cursr_search_logs = collection.aggregate(
            #     search_analytics_count_pipeline(project_id, client_id, excludedDomains, delta_days))

            # return AutoCorrect(text).rectified_token()
            return InputEngine(text, index_name, project_id,
                               client_id).result(inp_time)
        except Exception as e:
            error_message = f'[autocorrection_api view] Unable to accept request for autocorrection api for input: {text}'
            logger.error(error_message)
            logger.error(e)
            logger.exception(e)


# @autocorrection_api.route('/didyoumean')
# class SearchStringCorrection(Resource):

#     @autocorrection_api.expect(query_input)
#     def post(self):
#         text = autocorrection_api.payload.get(api_autocorrectexpansion_query,
#                                               '')
#         logger.info(f'Input text is {text}')
#         if text != '':
#             autocorrrect_obj = InputEngine(text).result()['output']
#             return autocorrrect_obj.get('all', '')
#         else:
#             return ''
