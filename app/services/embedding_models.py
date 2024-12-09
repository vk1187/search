import os
import re

from gensim import downloader
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.test.utils import datapath, get_tmpfile

# from app.services.config_constants import glove_wiki, synonym_counter, google_word2vec
from app.services.similarity_engine.Expansion_helpers import ExpansionHelper
from custom_logging import logger
from load_parameters import get_parameters


class GensimLoader:
    """Loads the gensim model for word2vec/glove"""

    def __init__(self):
        self.parameters = get_parameters()
        glove_wiki = self.parameters.get("pretrained_model_names", "glove_wiki")
        google_word2vec = self.parameters.get("pretrained_model_names",
                                         "google_word2vec")
        enable_google_word2vec = self.parameters.getboolean(
            "similarity", "enable_google_word2vec")
        enable_glove = self.parameters.getboolean("similarity", "enable_glove")

        if enable_google_word2vec:
            self.word2vec = self.load_model(google_word2vec)
            # self.word2vec
        if enable_glove:
            self.glove = self.load_model(glove_wiki)

    def load_model(self, model_path: str):
        """loading model"""
        os.environ['GENSIM_DATA_DIR'] = 'models'
        # os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), 'models')
        model = downloader.load(model_path)
        print("Gensim Model is loaded successfully")
        return model  # return ' '

    def model_similarity(self, text, model='word2vec'):

        synonym_counter = self.parameters.getint("similarity", "synonym_counter")
        if model == 'word2vec':
            return self.word2vec.most_similar(text, topn=synonym_counter)
        elif model == 'glove':
            return self.glove.most_similar(text, topn=synonym_counter)
        else:
            logger.warning(
                'Model Name is not defined - default model word2vec is used')
            return self.word2vec.most_similar(text, topn=synonym_counter)

    def post_processing(self, text, model_name):
        """replaces space with underscores and find similarity of tokens with the specified model and returns a unique list of this"""
        unique_embedding_similarity_list = []
        # try:
        for text_iter in [
                text,
                text.replace(' ', '_'),
                text.split(),
                text.lower(),
                text.lower().split(),
                text.replace(' ', '_').lower()
        ]:
            try:
                logger.debug(f'Text to find similarity : {text_iter}')
                standard_embedding_op = self.model_similarity(
                    text_iter, model_name)

                processed_results = [(word.lower().replace('_', ' '), similarity) 
                     for word, similarity in standard_embedding_op 
                     if not re.search('[^a-z\s\']', word.lower().replace('_', ' ')) 
                     and not re.search(r'\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?«»“”‘’]))', word.lower().replace('_', ' '))]
                standard_embedding_op = processed_results[:7]

                embedding_similarity_list = [
                    i[0] for i in standard_embedding_op
                ]
                unique_embedding_similarity_list = ExpansionHelper.case_insensitive_unique_list(
                    embedding_similarity_list)
                break
            except ValueError as ve:
                logger.error(
                    f'{text_iter} : Value not present in {model_name}')
                continue
            except KeyError as ke:
                logger.error(f'{text_iter} : key not present in {model_name}')
                continue
            except Exception as e:
                logger.error(f'{e}')
                continue
        # except Exception as e:
        #     logger.error(f'{e} -  Key not found in {self.model_name}')
        return unique_embedding_similarity_list


def convert_glove_word2vec(glove_path):
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.getcwd())),
                             'models')
    temp_path = os.path.basename(glove_path).rsplit('.',
                                                    1)[0] + '_word2vec.txt'

    glove_file = datapath(os.path.join(base_path, glove_path))
    tmp_file = get_tmpfile(temp_path)
    _ = glove2word2vec(glove_file, tmp_file)
    model = KeyedVectors.load_word2vec_format(tmp_file)
    return model


# if __name__ == '__main__':
#     import os
#
#     print(api._load_info())
#
#     print(os.getcwd())
# print(os.pardir)
# print(os.path.join(os.path.dirname(os.path.join(os.getcwd()), os.pardir)), 'models')
# model_converted = convert_glove_word2vec('glove.840B.300d.txt')
# print(os.path.basename('models/glove.840B.300d.txt').rsplit('.', 1)[0] + '_word2vec.txt')
# print(os.path.abspath(os.path.join(os.path.dirname(os.getcwd()), os.pardir)))
