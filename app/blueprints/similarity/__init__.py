from flask import Blueprint
from flask_restx import Api, fields

from app.services.config_constants import api_url_prefix, api_similarity_endpoint

bp = Blueprint('similarity',
               __name__,
               url_prefix=api_url_prefix + api_similarity_endpoint)

similarity_api = Api(bp,
                     title='Search Lego Cognitive Services',
                     description='Similarity Services API')

query_input = similarity_api.model(
    'Query1', {'input_query': fields.String('Latest Results')})

query_synonym_input = similarity_api.model(
    'Query', {
        'query': fields.String('Latest Results'),
        'industry_domain': fields.String(default='All'),
        'ner_expansion_flag': fields.Boolean(default=False),
        'enableSynonymExpansion': fields.Boolean(default=True),
        "client_id": fields.Integer(default=None, example=1)
    })
document_input = similarity_api.model('Document', {'document': fields.String})

from . import views
