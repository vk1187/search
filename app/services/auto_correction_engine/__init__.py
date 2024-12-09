import pickle

# from app.services.auto_correction_engine.helpers import check_entity_candidates
# from app.services.auto_correction_engine.soundex import Soundex
# from app.services.config_constants import autocorrect_probabilities_file_path
# from app.services.config_constants import autocorrect_vocab_count_file_path
# from app.services.config_constants import autocorrect_vocab_file_path
# from app.services.config_constants import autocorrect_vocab_soundex_file_path
from elastic_connection.elastic.helper import search_results, candidates_query, project_query
from app.services import es_connection

# __all__ = [Soundex, check_entity_candidates]
# gl_vocab_counts = pickle.load(open(autocorrect_vocab_count_file_path, 'rb'))
# gl_probabilities = pickle.load(open(autocorrect_probabilities_file_path, 'rb'))
# gl_vocab = search_results(es_connection,)
# gl_vocabulary_soundex_codes = pickle.load(open(autocorrect_vocab_soundex_file_path, 'rb'))
#
#
# class AutoCorrectionVocab:
#     def __init__(self):
#         try:
#             self.vocab_counts = gl_vocab_counts
#             self.probabilities = gl_probabilities
#             self.vocab = gl_vocab
#             self.vocabulary_soundex_codes = gl_vocabulary_soundex_codes
#         except Exception as e:
#             logger.error(f'{e} pickle not loaded properly. Check for vocabularies')
