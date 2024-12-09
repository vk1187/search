from flask import Blueprint
from flask_restx import Api, fields

from app.services.config_constants import api_url_prefix
from app.services.config_constants import search_analytics_current_period, search_analytics_backlog_days, \
    search_analytics_topk, excludedDomains_examplevalue
from custom_logging import logger

from load_parameters import get_parameters
parameters = get_parameters()

default_threshold = parameters.getint("trending_search",
                                      "default_current_frequency_threshold")
excludedDomains_defaultvalue = parameters.get("trending_search",
                                              "excludedDomains_defaultvalue")

bp = Blueprint('trending_search',
               __name__,
               url_prefix=api_url_prefix + '/trending_search')
try:
    trending_query_api = Api(bp,
                             title='Search Lego Cognitive Services',
                             description='Trending search queries Service API')
except Exception as e:
    logger.exception(f'{e} Unable to generate SwaggerAPI')

trending_query_api_input = trending_query_api.model(
    'Query_trending_query_api_input', {
        'project_id':
        fields.Integer(required=True, example=1),
        'client_id':
        fields.Integer(required=True, example=111194),
        'current_interval':
        fields.Integer(required=True,
                       default=search_analytics_current_period,
                       example=search_analytics_current_period),
        'historical_records':
        fields.String(required=True,
                      default=search_analytics_backlog_days,
                      example=search_analytics_backlog_days),
        'top_records':
        fields.Integer(required=False,
                       default=search_analytics_topk,
                       example=search_analytics_topk),
        'current_frequency_threshold':
        fields.Integer(required=False,
                       default=default_threshold,
                       example=default_threshold),
        "excludedDomains":
        fields.String(required=False,
                      default=excludedDomains_defaultvalue,
                      example=excludedDomains_examplevalue)
    })

trending_query_user_specific_api_input = trending_query_api.model(
    'Query_trending_query_user_specific_api_input', {
        'user_id':fields.String(required=True, example="TestAdmin@evalueserve.com"),
        'project_id':
        fields.Integer(required=True, example=1),
        'client_id':
        fields.Integer(required=True, example=111194),
        'current_interval':
        fields.Integer(required=True,
                       default=search_analytics_current_period,
                       example=search_analytics_current_period),
        'historical_records':
        fields.String(required=True,
                      default=search_analytics_backlog_days,
                      example=search_analytics_backlog_days),
        'top_records':
        fields.Integer(required=False,
                       default=search_analytics_topk,
                       example=search_analytics_topk),
        'current_frequency_threshold':
        fields.Integer(required=False,
                       default=default_threshold,
                       example=default_threshold)
    })

from . import views
