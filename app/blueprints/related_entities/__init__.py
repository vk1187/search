from flask import Blueprint
from flask_restx import Api, fields

from app.services.config_constants import api_url_prefix, api_related_entity_endpoint
from custom_logging import logger

bp = Blueprint('related_entities', __name__, url_prefix=api_url_prefix + api_related_entity_endpoint)

try:
    api = Api(bp, title='Search Lego Cognitive Services', description='Related Entities Services API')
except Exception as e:
    logger.error(f'{e} Unable to generate SwaggerAPI')
    logger.exception(e)

document_input = api.model('input_query', {
    'client_id': fields.Integer(required=True, example=111194),
    'project_id': fields.Integer(required=True, example=1),
    'isClicked': fields.Boolean(required=False, default=False, example=False),
    # 'embedding_index_filename':fields.String(example='embedding_111194_3_d6a5999b38224eef94bf45aeb35abc51.index', required=True),
    # 'entity_pickle_filename':fields.String(example='unique_entity_111194_3_93481745dd214f39b699fc186017b4fe.pth', required=True),
    'top_counter': fields.Integer(required=True, default=5, example=5),
    'search_query': fields.String(example='USA', required=True),
    'similarity_threshold_percent': fields.Float(required=False, example=80.0), })

# entity_input = api.model('list_of_entities',
#                          {
#                              'client_id': fields.Integer(required=True, example=111194),
#                           'project_id': fields.Integer(required=True, example=3),

#                           'entities': fields.List(fields.String, required=True),
#                           'similarity_threshold_percent': fields.Float(required=False,example=80.0),
#                           }
#                          )


entity_input_filenames = api.model('filename_of_entities',
                                   {
                                       'client_id': fields.Integer(required=True, example=111194),
                                       'project_id': fields.Integer(required=True, example=1),

                                       'entities': fields.Raw()
                                   }
                                   )

from . import views
