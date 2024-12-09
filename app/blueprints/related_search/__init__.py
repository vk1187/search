from flask import Blueprint
from flask_restx import Api, fields

from app.services.config_constants import api_url_prefix, api_related_search_endpoint
from custom_logging import logger

bp = Blueprint('related_search',
               __name__,
               url_prefix=api_url_prefix + api_related_search_endpoint)
try:
    related_query_api = Api(
        bp,
        title='Search Lego Cognitive Services',
        description='Related search queries Service API using SBert')
except Exception as e:
    logger.error(f'{e} Unable to generate SwaggerAPI')
    logger.exception(e)

query_input = related_query_api.model(
    'Query', {
        'query': fields.String,
        'project_Id': fields.Integer(required=False, example=1),
        'client_Id': fields.Integer(required=False, example=111194),
        'similarity_threshold_percent': fields.Float(required=False,
                                                     example=80.0),
        'top_counter': fields.Integer(required=False, example=5),
    })

embedding_input = related_query_api.model(
    'EmbeddingInput', {
        'project_id': fields.Integer(required=False, example=1),
        'client_id': fields.Integer(required=False, example=111194)
    })

from . import views
