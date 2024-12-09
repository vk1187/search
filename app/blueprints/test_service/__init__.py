from flask import Blueprint
from flask_restx import Api, fields
from flask_restx import Resource
from custom_logging import logger
from app.services.config_constants import search_analytics_current_period, search_analytics_backlog_days, search_analytics_topk, default_current_frequency_threshold
from app.services.config_constants import api_url_prefix

bp = Blueprint('test_service', __name__, url_prefix=api_url_prefix + '/test_service')
try:
    test_query_api = Api(bp, title='Search Lego Cognitive Services', description='Testing in Semantic Service API')
except Exception as e:
    logger.exception(f'{e} Unable to generate SwaggerAPI')


test_query_api_input = test_query_api.model('Query',
                                           {'project_id': fields.Integer(required=True,example=1),
                                            'client_id': fields.Integer(required=True,example=111194),
                                            'current_interval':fields.Integer(required=True,default=search_analytics_current_period,example=search_analytics_current_period),
                                            'historical_records':fields.String(required=True,default=search_analytics_backlog_days,example=search_analytics_backlog_days),
                                            'top_records':fields.Integer(required=False,default=search_analytics_topk,example=search_analytics_topk),
                                            'current_frequency_threshold':fields.Integer(required=False,default=5,
                                            example=5),
                                            }
                                           )


from . import views


