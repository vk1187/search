from flask import Blueprint
from flask_restx.api import Api

from app.services.config_constants import api_url_prefix, api_autosuggestion_endpoint
from custom_logging import logger

bp = Blueprint('autosuggestion',
               __name__,
               url_prefix=api_url_prefix + api_autosuggestion_endpoint)

try:
    autosuggestion_api = Api(bp,
                             title='Search Lego Cognitive Services',
                             description='NER Services API')
except Exception as e:
    logger.error(f'{e} Unable to generate SwaggerAPI')
    logger.exception(e)

# class RandomNumber(fields.Raw):
#     def output(self, key, obj):
#         return random.random()

document_input = autosuggestion_api.model('Document', {})

from . import views
