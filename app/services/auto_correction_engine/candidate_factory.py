import numpy as np
from fastDamerauLevenshtein import damerauLevenshtein
import time
# from app.services.auto_correction_engine import AutoCorrectionVocab
from app.services.auto_correction_engine.helpers import Helper
# from app.services.auto_correction_engine.helpers import check_entity_candidates
from app.services.auto_correction_engine.levenstien import Levenshtein
from app.services.auto_correction_engine.soundex import Soundex
from app.services.config_constants import ALL_ALGORITHM
from app.services.config_constants import auto_correction_flag
# from app.services.config_constants import levenshtein_edit_threshold
from app.services.slb_configuration import SLBConfiguration
from custom_logging import logger
from elastic_connection.elastic.helper import elastic_query_results
from load_parameters import get_parameters


config = SLBConfiguration.get_config(auto_correction_flag)

# def spellcheck_candidate_evaluator(obj='', word=None):
#     objs = dict(soundex=Soundex(word), levenshtein=Levenshtein(word))
#     return objs[obj]


class SpellCheckEvaluator:

    def __init__(self, word, index_name: str, project_id: int, client_id: int):
        """ Initialization Constructor"""
        super().__init__()

        self.word = word
        self.parameters = get_parameters()
        self.index_name = index_name
        self.project_id = project_id
        self.client_id = client_id
        self.soundex_candidates = Soundex(self.word, self.index_name,
                                          self.project_id)()
        # spellcheck_candidate_evaluator('soundex', self.word)())
        # self.levenshtein_candidates =
        # self.first_letter_heuristic(Levenshtein(self.word, self.index_name, self.project_id)())
        self.levenshtein_candidates = Levenshtein(self.word, self.index_name,
                                                  self.project_id)()
        # spellcheck_candidate_evaluator('levenshtein', self.word)())
        # self.all_candidates = set(self.soundex_candidates + self.levenshtein_candidates)

    def first_letter_heuristic(self, candidates):
        """returns only those candidate whose first character is same as the inputs first character"""
        return [
            candidate for candidate in candidates
            if candidate[0] == self.word[0]
        ]

    def sort_candidates(self, candidates: list):
        """returns sorted top candidates after computation """
        top_candidates = self.autocorrect_metrics(suggestions=candidates)
        return top_candidates

    def results_autocorrect(self, algo):
        """return candidates with their frequency and edit distance for soundex/levenshtein candidates"""
        candidates = []
        if algo == 'soundex':
            candidates = self.soundex_candidates
            # logger.debug(f'soundex candidates : {candidates}')
        if algo == 'levenshtein':
            candidates = self.levenshtein_candidates
            logger.debug(f'levenshtein candidates : {candidates}')
        # logger.debug(f'algorithm candidates : {candidates}')
        if len(candidates) > 0:
            logger.debug(f'Running {algo}')
            top_candidate = self.sort_candidates(candidates)
            logger.debug(f'top_candidate after sorting func {top_candidate}')
            if len(top_candidate) > 0:
                return self.entity_evaluation(top_candidate)
            # else:
        return {'candidate': self.word, 'frequency': 0, 'edit_distance': 10000}

    def result_value_all(self):
        """return the best output from soundex and levenstein algorithm"""
        algo_outputs = {
            algo: self.results_autocorrect(algo)
            for algo in ['soundex', 'levenshtein']
        }
        all_values = [list(i[1].values()) for i in algo_outputs.items()]
        all_op = list(sorted(all_values, key=lambda x: -x[1]))[0][0]
        return all_op

    def output(self):
        """computes the output for soundex,levenstien and outputs the best one as well in 'all' key"""
        # algo_outputs = {algo: self.results_autocorrect(algo)['candidate'] for algo in ['soundex', 'levenshtein']}
        soundex_algo_output = self.results_autocorrect('soundex')
        logger.debug(f'soundex_algo_output:{soundex_algo_output}')
        levenshtein_algo_output = self.results_autocorrect('levenshtein')
        logger.debug(f'levenshtein_algo_output:{levenshtein_algo_output}')
        # algo_outputs = {algo: self.results_autocorrect(algo) for algo in ['soundex', 'levenshtein']}
        algo_outputs = {
            'soundex': soundex_algo_output,
            'levenshtein': levenshtein_algo_output
        }
        logger.debug(f'algo_outputs: {algo_outputs}')
        all_values = [list(i[1].values()) for i in algo_outputs.items()]
        logger.debug(f'all_values:{all_values}')
        all_op = list(sorted(all_values, key=lambda x: (x[2], -x[1])))[0][0]
        algo_op = {i[0]: i[1]['candidate'] for i in algo_outputs.items()}
        algo_op[ALL_ALGORITHM] = all_op

        logger.debug(f"outputs : {algo_op}")
        return algo_op

    def entity_evaluation(self, top_candidates: list):
        """returns the entities found in the top candidates along with their frequence and edit distance"""
        # logger.debug(f'top_candidates -> {top_candidates}')
        logger.debug(f'top_candidates: {top_candidates}')
        entity_found = Helper(self.index_name, self.project_id,
                              self.client_id).check_entity_candidates(
                                  np.array(top_candidates))
        return entity_found if entity_found else {
            'candidate':
            np.array(top_candidates)[:, 0][0],
            'frequency':
            elastic_query_results(index_name=self.index_name,
                                  vocab_type='data_dictionary',
                                  project_id=self.project_id,
                                  candidate_key=np.array(top_candidates)[:,
                                                                         0][0],
                                  property_attribute='frequency')[np.array(
                                      top_candidates)[:, 0][0]],
            'edit_distance':
            np.array(top_candidates)[0, :][2]
        }
        # self.vocab_counts.get(np.array(top_candidates)[:, 0][0])}

    def suggestion_probabilities(self, suggestion_words: list):
        """returns the probabilities of the suggestion words"""
        suggestions = elastic_query_results(index_name=self.index_name,
                                            vocab_type='data_dictionary',
                                            project_id=self.project_id,
                                            candidate_key=suggestion_words,
                                            property_attribute='probabilities')
        # return {token: self.probabilities.get(token, 0) for token in suggestion_words}
        return suggestions

    def autocorrect_metrics(self, suggestions=None):
        """computation of best candidates on the basis of  edit distance threshold using damerauLevenshtein"""
        inp = self.word.lower()
        # logger.debug(f'In fn -> {self.autocorrect_metrics.__qualname__}')
        # word = self.input_word(token)
        # logger.debug(f'{self.autocorrect_metrics.__qualname__} word-> {word} , token->{token}')
        candidate_probability = self.suggestion_probabilities(
            suggestion_words=suggestions)
        # pickle.dump(candidate_probability, open("candidate_probability.pickle", "wb"))
        # logger.debug(f'{self.autocorrect_metrics.__qualname__}
        # candidate_probability for {suggestions}->{candidate_probability}')
        # candidate_edit_distance = {suggest: self.min_edit_distance(source=word, target=suggest) for suggest in
        #                            suggestions}
        candidate_edit_distance = {
            suggest: damerauLevenshtein(inp, suggest, False)
            for suggest in suggestions
        }
        candidate_edit_distance_score = {
            suggest: np.log(
                damerauLevenshtein(inp, suggest, False) *
                damerauLevenshtein(inp, suggest, True))
            for suggest in suggestions
        }
        # candidate_edit_distance_score = {suggest: damerauLevenshtein(word, suggest, similarity=False) for suggest in
        #                                  suggestions}

        # pickle.dump(candidate_edit_distance, open("candidate_edit_distance.pickle", "wb"))
        # logger.debug(
        #     f'{self.autocorrect_metrics.__qualname__} candidate_edit_distance for {word} ->{token}->{candidate_edit_distance}')

        metrics = np.array([[
            i,
            candidate_probability.get(i, 0),
            candidate_edit_distance.get(i, -1),
            candidate_edit_distance_score.get(i, -1)
        ] for i in suggestions],
                           dtype=object)
        # pickle.dump(metrics, open("metrics.pickle", "wb"))
        # logger.debug(metrics)

        # logger.debug(levenshtein_edit_threshold,min(metrics[:, 2]) + 1,idx_dist)
        logger.debug(f'metrics : {metrics}')
        
        # if config.get('minimum_threshold_check', None):

        levenshtein_edit_threshold = self.parameters.getint("autocorrection","levenshtein_edit_threshold")

        idx_dist = np.where(metrics[:, 2] <= levenshtein_edit_threshold, True,
                            False)
        # else:
        if sum(idx_dist) == 0:
            idx_dist = np.where(metrics[:, 2] <= min(metrics[:, 2]) + 1, True,
                                False)
        # logger.debug(idx_dist)
        min_edit_matrix = metrics[idx_dist]
        # logger.debug(min_edit_matrix)
        # logger.debug(f'Minimum Distance - {self.autocorrect_metrics.__qualname__} --> {min_edit_matrix}')
        # idx_prob = np.where(min_edit_matrix[:, 1] == max(min_edit_matrix[:, 1]), True, False)
        min_edit_matrix_10 = list(
            sorted(min_edit_matrix, key=lambda item: -item[1]))[:10]
        # logger.debug(
        #     f'Maximum Probability - {self.autocorrect_metrics.__qualname__} --> {min_edit_matrix[idx_prob][:-40]}')
        # distance_probability_candidates = list(min_edit_matrix[idx_prob][:, 0])
        distance_probability_candidates = min_edit_matrix_10

        return distance_probability_candidates
