from flask import Blueprint
from flask_restx import Api
from flask_restx import fields

from app.services.config_constants import api_url_prefix, api_datadictionary_endpoint

bp = Blueprint('data_dictionaries', __name__, url_prefix=api_url_prefix + api_datadictionary_endpoint)

dictionary_api = Api(bp, title='Search Lego Cognitive Services', description='Data Dictionary Services API')

document_input = dictionary_api.model('JsonData', {'projectid_to_process': fields.List(fields.Integer(example=34)),
                                                   'data': fields.List(fields.Raw({}, example={"project_id": 34,
                                                                                               "Title": "Aggregate Industries To Sell New Lafarge Bagged Cement And Concretes",
                                                                                               "Summary": "LafargeHolcim subsidiary Aggregate Industries has launched three Lafarge branded packed cement and concrete products: High Performance Concrete; Instant Concrete; and Premium Cement. The company says that the products are “a response to rising demand from merchants and their customers alike to offer more specialised packed cement solutions,” and are suited to various domestic applications.",
                                                                                               "Tag": " Mining &amp; Cement, United Kingdom, New products / offerings, LafargeHolcim"
                                                                                               }))})

from . import views
