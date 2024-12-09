import time
from random import randint
from flask import helpers

from flask_restx import Resource
from app.services.test_service.helper import results_fixed
from app.services.config_constants import search_analytics_current_period, search_analytics_backlog_days, \
    search_analytics_topk
from custom_logging import logger
from . import test_query_api, test_query_api_input
# from app import cache
# from app_cache import cache


@test_query_api.route('/test_check')
class test_checkQuery(Resource):
    """returns the trending search terms from input historical period to till date """

    
    @test_query_api.expect(test_query_api_input)
    # @cache.memoize(10)
    def post(self,**kwargs):
        try:

            tic = time.time()
            logger.info(f"Test API for Semantic API'")
            print(f'cache is not used!{id(kwargs)}')

            if test_query_api.payload in [None, [], '', ' ', {}]:
                logger.warning(f'Please pass input parameters for [Trending Queries]')
                return {'result': "Error - No Input is passed", "eta": time.time() - tic}

            project_id = test_query_api.payload.get('project_id', None)
            client_id = test_query_api.payload.get('client_id', None)
            current_period = test_query_api.payload.get(
                'current_interval', search_analytics_current_period)
            backlog_days = test_query_api.payload.get(
                'historical_records', search_analytics_backlog_days)
            topk = test_query_api.payload.get(
                'top_records', search_analytics_topk)
            current_frequency_threshold = test_query_api.payload.get(
                'current_frequency_threshold', 5)

            try:

                return results_fixed(project_id,client_id,backlog_days,current_period,topk,current_frequency_threshold)

            except Exception as e:
                logger.error(
                    '[Test Service Search]Unable to run test service ')
                logger.error(f'[Test Service] Error : {e}')
                return {"result": None,
                        "eta": time.time() - tic}
        except Exception as e:
            logger.error(f'[test_service view] Unable to accept request for test service ')
            logger.error(f'{e}')
