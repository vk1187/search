import time

from flask_restx import Resource

from app.services.config_constants import search_analytics_current_period, search_analytics_backlog_days, \
    search_analytics_topk
from app.services.trending_search_engine import trending_search_factory
from app.services.trending_search_engine.helper import historical_frequency, preprocessing_trending_search_dataframe
from authenitcation.auth import token_required
from custom_logging import logger
from . import trending_query_api, trending_query_api_input,trending_query_user_specific_api_input


from load_parameters import get_parameters


@trending_query_api.route('/return_trending_queries')
class TrendingQuery(Resource):
    """returns the trending search terms from input historical period to till date """

    @trending_query_api.expect(trending_query_api_input)
    # @token_required
    def post(self):
        try:
            parameters = get_parameters()
            tic = time.time()
            logger.info(f"Finding Trending queries")
            if trending_query_api.payload in [None, [], '', ' ', {}]:
                logger.warning(
                    f'Please pass input parameters for [Trending Queries]')
                return {
                    'result': "Error - No Input is passed",
                    "eta": time.time() - tic,
                    "status": False
                }

            default_threshold = parameters.getint(
                "trending_search", "default_current_frequency_threshold")
            excluded_domains_defaultvalue = parameters.get(
                "trending_search", "excludedDomains_defaultvalue")
            project_id = int(trending_query_api.payload.get('project_id', -1))
            client_id = int(trending_query_api.payload.get('client_id', -1))
            logger.info(
                f"Finding Trending queries for client_id {client_id} and project_id {project_id} "
            )
            current_period = trending_query_api.payload.get(
                'current_interval', search_analytics_current_period)
            backlog_days = trending_query_api.payload.get(
                'historical_records', search_analytics_backlog_days)
            topk = trending_query_api.payload.get('top_records',
                                                  search_analytics_topk)
            current_frequency_threshold = trending_query_api.payload.get(
                'current_frequency_threshold', default_threshold)
            excludedDomains = trending_query_api.payload.get(
                'excludedDomains', excluded_domains_defaultvalue)

            try:
                delta_days = historical_frequency(mode=backlog_days)
                df_pivot, current_interval, input_query_time = preprocessing_trending_search_dataframe(
                    project_id, client_id, delta_days,
                    current_frequency_threshold, current_period,
                    excludedDomains)
                query_zscores = trending_search_factory.main(
                    df_pivot, current_interval, topk, input_query_time)
                if query_zscores is None:
                    return {
                        "result": None,
                        "eta": time.time() - tic,
                        "status": False
                    }
                else:
                    return {
                        'result':
                        query_zscores,
                        'eta':
                        time.time() - tic,
                        'status':
                        False if
                        (query_zscores is None) or len(query_zscores) == 0
                        or any(x is None for x in query_zscores) else True
                    }
            except Exception as e:
                logger.error(
                    '[Trending Search] Either Dataframe is not created/some of the column name is not aligned with mongodb/No Result is there in the database'
                )
                logger.error(f'[Trending Search] Error : {e}')
                logger.exception(e)
                return {
                    "result": None,
                    "eta": time.time() - tic,
                    "status": False
                }
        except Exception as e:
            logger.error(
                f'[trending_search view] Unable to accept request for trending search api '
            )
            logger.error(f'{e}')
            logger.exception(e)



@trending_query_api.route('/return_user_specific_trending_queries')
class TrendingQuery(Resource):
    """returns the trending search terms from input historical period to till date """

    @trending_query_api.expect(trending_query_user_specific_api_input)
    # @token_required
    def post(self):
        try:
            parameters = get_parameters()
            tic = time.time()
            logger.info(f"Finding Trending queries")
            if trending_query_api.payload in [None, [], '', ' ', {}]:
                logger.warning(
                    f'Please pass input parameters for [Trending Queries]')
                return {
                    'result': "Error - No Input is passed",
                    "eta": time.time() - tic,
                    "status": False
                }

            default_threshold = parameters.getint(
                "trending_search", "default_current_frequency_threshold")
            excluded_domains_defaultvalue = None 
            # if parameters.get("trending_search", "excludedDomains_defaultvalue") is "None"
            user_id = trending_query_api.payload.get('user_id', None)
            if user_id is None:
                excluded_domains_defaultvalue=parameters.get("trending_search", "excludedDomains_defaultvalue")

            project_id = int(trending_query_api.payload.get('project_id', -1))
            client_id = int(trending_query_api.payload.get('client_id', -1))
            logger.info(
                f"Finding Trending queries for client_id {client_id} and project_id {project_id} "
            )
            current_period = trending_query_api.payload.get(
                'current_interval', search_analytics_current_period)
            backlog_days = trending_query_api.payload.get(
                'historical_records', search_analytics_backlog_days)
            topk = trending_query_api.payload.get('top_records',
                                                  search_analytics_topk)
            current_frequency_threshold = trending_query_api.payload.get(
                'current_frequency_threshold', default_threshold)
            excludedDomains = trending_query_api.payload.get(
                'excludedDomains', excluded_domains_defaultvalue)

            try:
                delta_days = historical_frequency(mode=backlog_days)
                df_pivot, current_interval, input_query_time = preprocessing_trending_search_dataframe(
                    project_id, client_id, delta_days,
                    current_frequency_threshold, current_period,
                    excludedDomains,user_id)
                query_zscores = trending_search_factory.main(
                    df_pivot, current_interval, topk, input_query_time)
                if query_zscores is None:
                    return {
                        "result": None,
                        "eta": time.time() - tic,
                        "status": False
                    }
                else:
                    return {
                        'result':
                        query_zscores,
                        'eta':
                        time.time() - tic,
                        'status':
                        False if
                        (query_zscores is None) or len(query_zscores) == 0
                        or any(x is None for x in query_zscores) else True
                    }
            except Exception as e:
                logger.error(
                    '[Trending Search] Either Dataframe is not created/some of the column name is not aligned with mongodb/No Result is there in the database'
                )
                logger.error(f'[Trending Search] Error : {e}')
                logger.exception(e)
                return {
                    "result": None,
                    "eta": time.time() - tic,
                    "status": False
                }
        except Exception as e:
            logger.error(
                f'[trending_search view] Unable to accept request for trending search api '
            )
            logger.error(f'{e}')
            logger.exception(e)
