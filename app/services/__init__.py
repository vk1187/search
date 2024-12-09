# from .config_constants import *
import json
import os
from app.services.config_constants import auto_completion_flag
from app.services.config_constants import auto_completion_max_shingle_length
from app.services.config_constants import auto_completion_min_shingle_length
from app.services.config_constants import auto_completion_phraser_flag
# from app.services.config_constants import auto_completion_phraser_flag
# from app.services.config_constants import auto_completion_phraser_flag
from app.services.model_engine.engelish_sentence_model import EnglishSentenceModelSpacyInit
from app.services.similarity_engine.sense2vec_utils import Sense2vec_Loader
# from embedding_models import GensimLoader
from app.services.utils import DataPreprocessor
from elastic_connection.elastic.helper import ElasticConnection
from sentence_transformer_factory.stc.helper import SentenceTransformerInstance

es_connection = ElasticConnection.getInstance()
# s2v = Sense2vec_Loader.getInstance()
embedder = SentenceTransformerInstance.getInstance()



configSetting_path = os.path.join("app", "services", "configSetting.json")
with open(configSetting_path,encoding='utf8') as file:
    config = json.load(file)
    file.close()
