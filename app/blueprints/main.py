from flask import Blueprint
from flask_restx import Api, Resource

from custom_logging import logger

bp = Blueprint('main', __name__)

api = Api(bp)

logger.info('HomePage')

@api.route('/')
class Index(Resource):
    """default message at home screen"""
    def get(self):
        """default message at home screen"""
        return {'output': 'Welcome'}
