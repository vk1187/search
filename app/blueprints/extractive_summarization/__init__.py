from flask import Blueprint
from flask_restx import Api, fields

from app.services.config_constants import api_url_prefix, api_extractive_summarization_endpoint
from custom_logging import logger

bp = Blueprint('extractive_summarization',
               __name__,
               url_prefix=api_url_prefix +
               api_extractive_summarization_endpoint)

try:
    api = Api(bp,
              title='Search Lego Cognitive Services',
              description='Extractive Summarization Services API')
except Exception as e:
    logger.error('Unable to generate SwaggerAPI')
    logger.exception(e)

es_input = api.model(
    'es_input', {
        'data': fields.Raw([]),
        'client_id': fields.Integer(required=False, example=111194),
        'project_id': fields.Integer(required=False, example=1),
        'sentence_count' :fields.Integer(required=False, example=2),
        'number_of_words_per_sentences' : fields.Integer(required=False, example=5)
    })

from . import views
