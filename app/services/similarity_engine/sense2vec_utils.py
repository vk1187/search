import os
import tarfile

import requests
from sense2vec import Sense2Vec

# from app.services.config_constants import sense2vec_model_path
from load_parameters import get_parameters
# from app.services.config_constants import synonym_counter
from app.services.similarity_engine.Expansion_helpers import ExpansionHelper
from custom_logging import logger





sense2vec_url = 'https://github.com/explosion/sense2vec/releases/download/v1.0.0/s2v_reddit_2015_md.tar.gz'

os.makedirs('models', exist_ok=True)


class Sense2VecEmbeddings:
    def __init__(self):
        try:
            self.parameters = get_parameters()
            sense2vec_model_path = parameters.get("file_paths","sense2vec_model_path")
            self.s2v_model = Sense2Vec().from_disk(sense2vec_model_path)
        except ValueError as value_error:
            logger.error(value_error)
            response = requests.get(sense2vec_url, stream=True)
            file = tarfile.open(fileobj=response.raw, mode="r|gz")
            file.extractall(path="models")
            self.s2v_model = Sense2Vec().from_disk(sense2vec_model_path)
        self.find_similar = self.s2v_model.most_similar

    def top_similar_terms(self, term, entity=None):
        """returns similar items on the basis of input term and replaces space with underscore"""
        embedding_similarity_list = []
        if entity is not None:
            search_phrase = str(term).strip().replace(' ', '_') + '|' + str(entity)
        else:
            search_phrase = self.s2v_model.get_best_sense(term)
        logger.debug(f'{search_phrase} - query to be looked in sense2vec')

        if search_phrase is not None:
            try:
                synonym_counter = self.parameters.getint("similarity","synonym_counter")
                embedding_similarity_list = self.find_similar(search_phrase, synonym_counter)
            except Exception as v:
                logger.error(f'{v} - similar terms are not available from sense2vec model')
                logger.exception(e)
        else:
            pass
        return embedding_similarity_list

    def resultant_entity(self, s2v_result, entity=None, threshold=.75):
        """
        :param s2v_result:
        :param entity:
        :param threshold: similar terms only above specified threshold are considered ;default=.75
        :return:
        """
        if entity is None:
            similar_terms = [i[0].split('|')[0].replace('_', ' ') for i in s2v_result if i[1] > threshold]
        else:
            similar_terms = [i[0].split('|')[0].replace('_', ' ') for i in s2v_result if
                             i[0].split('|')[1] == entity and i[1] > threshold]
        return similar_terms
        # return list(
        #     set([DataPreprocessor(i.split('|')[0].replace('_', ' '),
        #                           clean_punctuations_start_stop_flag)().strip().replace(' ', '_') + '|' +
        #          i.split('|')[1] for i in
        #          similar_terms]))

    def check_original_search_string(self, final_lists, search_string, topn=5):
        #     print(final_lists)
        clean_list = [' '.join(i.split('|')[0].split('_')).strip() for i in final_lists
                      if search_string.lower() != i.lower().split('|')[0]]
        return ExpansionHelper.unique_ordered_list(clean_list)[:topn]


class Sense2vec_Loader:
    """Sense2vec Singletion"""
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if Sense2vec_Loader.__instance is None:
            Sense2vec_Loader()
        return Sense2vec_Loader.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if Sense2vec_Loader.__instance is not None:
            raise Exception("Sense2vec_Loader Instance already exists")
        else:
            Sense2vec_Loader.__instance = load_sense2vec()


def load_sense2vec():
    load_sense2vec_ = Sense2VecEmbeddings()
    print('Sense2vec is loaded')
    return load_sense2vec_
