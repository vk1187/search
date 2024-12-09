from flask import Flask
from flask import request
from flask.cli import load_dotenv
from flask_cors import CORS

# from app.blueprints import autosuggestion
from app_cache import cache
from .blueprints import autocorrection
from .blueprints import autosuggestion
from .blueprints import dictionaries
from .blueprints import main
from .blueprints import ner
from .blueprints import related_entities
from .blueprints import related_search
from .blueprints import similarity
from .blueprints import extractive_summarization
# from .blueprints import test_service
from .blueprints import trending_search
from .services.ner_engine.ml_model.spacy.load_spacy import SpacyInit

# gensim_models = GensimLoader()
load_dotenv()


# os.environ['GENSIM_DATA_DIR'] = os.path.join(os.getcwd(), 'models')


def register_ner_engine():
    """Initalizathe Spacy Model during API initialization"""
    spacyservice = SpacyInit()
    spacyservice.load_spacy_model()

def register_embeddings_engine():
    """Initalizathe Spacy Model during API initialization"""
    spacyservice = SpacyInit()
    spacyservice.load_spacy_lg_model()


def create_app():
    """Initialize the Flask App"""
    app = Flask(__name__)
    CORS(app)
    register_ner_engine()
    register_embeddings_engine()
    app.config.from_object('config')
    app.debug = True
    app.config['CACHE_TYPE'] = 'SimpleCache'

    cache.init_app(app)
    cache.app = app

    app.register_blueprint(main.bp)
    app.register_blueprint(ner.bp)
    app.register_blueprint(similarity.bp)
    app.register_blueprint(autocorrection.bp)
    app.register_blueprint(dictionaries.bp)
    app.register_blueprint(trending_search.bp)
    app.register_blueprint(related_search.bp)
    app.register_blueprint(autosuggestion.bp)
    app.register_blueprint(related_entities.bp)

    app.register_blueprint(extractive_summarization.bp)
    # app.register_blueprint(test_service.bp)

    @app.before_request
    def manipulate_req():
        print(request.args)

    @app.after_request
    def manipulate_res(response):
        print(response)
        return response

    return app
