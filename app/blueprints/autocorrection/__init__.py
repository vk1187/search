from flask import Blueprint
from flask_restx import Api
from flask_restx import fields

from app.services.config_constants import api_url_prefix,api_autocorrect_endpoint



bp = Blueprint('autocorrection',
               __name__,
               url_prefix=api_url_prefix + api_autocorrect_endpoint)

autocorrection_api = Api(bp,
                         title='Search Lego Cognitive Services',
                         description='AutoCorrection Services API')

query_input = autocorrection_api.model(
    'Query_2', {
        'input_query':
        fields.String(example='germany revenue'),
        'index_name':
        fields.String(example='cognitive_datadictionary_111194_3_2_202213_20'),
        'project_id':
        fields.Integer(example=123),
        'client_id':
        fields.Integer(example=1)
    })

from . import views
