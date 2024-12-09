from flask import Blueprint
from flask_restx import Api, fields

from app.services.config_constants import api_url_prefix, api_ner_endpoint
from custom_logging import logger

bp = Blueprint('ner', __name__, url_prefix=api_url_prefix + api_ner_endpoint)

try:
    api = Api(bp,
              title='Search Lego Cognitive Services',
              description='NER Services API')
except Exception as e:
    logger.error(f'{e} Unable to generate SwaggerAPI')
    logger.exception(e)

# document_input = api.model('Document', {})
wild = fields.Wildcard(fields.String)
wildcard_fields = {'*': wild}
# document_input = api.model('Document',{'data': fields.List(fields.Nested(model=api.model('Document2', {'text': fields.String(required=True), 'id': fields.String(required=True)}))) , 'client_Id': fields.Integer(required=False,example=1)})
document_input = api.model(
    'Document', {
        'data': fields.Raw([]),
        'client_id': fields.Integer(required=False, example=1)
    })

# similarity_api = Api(bp, title='Search Lego Cognitive Services', description='Similarity Services API')

manual_entity_input = api.model(
    'manual_entity_input',
    {
        'project_id':
        fields.Integer(required=False, example=1),
        'client_id':
        fields.Integer(required=True, example=111194),
        'data':
        fields.Raw([],
                   example=[{
                       "entity": "ORG",
                       "pattern": "EVS",
                       "pattern_id": "EVS"
                   }, {
                       "entity": "LOC",
                       "pattern": "vivek vihar",
                       "pattern_id": "vv"
                   }]),
        # 'label': fields.Raw([],example=['ORG','LOC']),
        # 'pattern': fields.Raw([],example=['Evalueserve','vivek vihar']),
        # "pattern_id":fields.Raw([], example=['evalueserve','vv']),
        'on_the_fly_flag':
        fields.Integer(required=True, example=1),
        'delete_pattern_ids':
        fields.Raw([])
    })

from . import views
