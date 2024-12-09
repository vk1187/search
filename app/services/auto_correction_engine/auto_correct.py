# import numpy as np
# from fastDamerauLevenshtein import damerauLevenshtein
#
# # from app.services.auto_correction_engine import AutoCorrectionVocab
# # from app.services.auto_correction_engine.helpers import check_entity_candidates
# from app.services.auto_correction_engine.helpers import Helper
# # from app.services.auto_correction_engine.helpers import vocab_counts
# from app.services.auto_correction_engine.levenstien import Levenshtein
# from app.services.auto_correction_engine.soundex import Soundex
# from app.services.config_constants import auto_correction_flag
# from app.services.config_constants import auto_correction_levenshtein
# from app.services.config_constants import auto_correction_soundex
# from app.services.config_constants import levenshtein_edit_threshold
# from app.services.config_constants import prefix_edit_distance
# from app.services.ner_engine.ml_model.spacy import SpacyService
# from app.services.slb_configuration import SLBConfiguration
# from custom_logging import logger
#
# config = SLBConfiguration.get_config(auto_correction_flag)
#
#
# # class Output:
# #     Helper.run_correction_check
#
# class AutoCorrect:
#     def __init__(self, word: str):
#         super().__init__()
#         self.word = word
#         self.doc, self.custom_entities = SpacyService.extract_entities(
#             word
#             # original=True
#         )
#         # self.word_list = self.word.split()
#         self.word_list = [i for i in self.doc]
#         logger.debug(self.word_list)
#         self.first_letter_match = False
#         if config.get('first_letter_heuristic', None):
#             self.first_letter_match = True
#
#         self.did_you_mean = self.search_query_unigram_correction()
#         self.auto_correction_levenshtein_v = self.search_query_unigram_correction(
#             method=auto_correction_levenshtein) if len(
#             self.word) > prefix_edit_distance else {"candidate": self.word, "frequency": 0}
#         self.auto_correction_soundex_v = self.search_query_unigram_correction(method=auto_correction_soundex)
#
#     # def word_check(self, word):
#     #     return word in self.vocab or len(word) < 3 or get_has_number(word)
#
#     def search_query_unigram_correction(self, method=None):
#         logger.info(f'In fn -> {self.search_query_unigram_correction.__qualname__}')
#         print(self.word_list)
#         a = []
#         # print(len(self.word_list) == 1 and len(self.word) > 2, len(self.word_list), len(self.word),
#         #       len(self.word_list) == 1, len(self.word) > 2, self.word)
#
#         # if len(self.word_list) > 1:
#         #     print('In loop')
#         # for i in self.word_list:
#
#         # print(i,not self.word_check(word=i) , i.isalpha(),i in self.vocab , len(i) < 3 ,i.isnumeric(),i.isalnum())
#         # return [self.did_you_mean_suggestions(token=i)['candidate'] for i in self.word_list]
#
#         correct_token = ''
#         for i in self.word_list:
#             logger.info(f'Iterating over {i}')
#             logger.debug(f'Helper(i).run_correction_check -> {Helper(i).run_correction_check}')
#             logger.debug(f'str(i.text).isalpha() -> {str(i.text).isalpha()}')
#             logger.debug(f"i.ent_type_ not in ['PERSON'] -> {i.ent_type_} -> {i.ent_type_ not in ['PERSON']}")
#             # Issue -  removing Person check as of now since due to bad ner model results are not good
#             if not Helper(i).run_correction_check and str(i.text).isalpha():
#                 logger.info('Checking if word is present in vocab and is completely alphabetical')
#                 # counter += 1
#                 # if counter > 1:
#                 #     correct_token += ' '
#                 output = self.did_you_mean_suggestions(token=i.text, method=method)['candidate']
#                 correct_token += output if output else i.text
#             else:
#                 correct_token += i.text
#             correct_token += i.whitespace_
#         return correct_token
#
#         # output_txt
#
#         # return ' '.join(
#         #     self.did_you_mean_suggestions(token=i.text)['candidate'] if (
#         #             not self.word_check(word=i) and str(i.text).isalpha()) else i.text for i in
#         #     self.word_list)
#         # elif len(self.word_list) == 1 and len(self.word) > 2:
#         #     print(' In this loop for single unigram')
#         #     # return ' '.join(self.did_you_mean_suggestions(token=i)['candidate'] for i in self.word_list)
#         #     return ' '.join(
#         #         self.did_you_mean_suggestions(token=i)['candidate'] if not self.bool_vocab_check(i)
#         #         else i for i in
#         #         self.word_list)
#         # elif len(self.word) < 3:
#         #     return self.word
#         # else:
#         #     return self.word
#
#     def rectified_token(self):
#         return \
#             {
#                 auto_correction_levenshtein: self.auto_correction_levenshtein_v,
#                 auto_correction_soundex: self.auto_correction_soundex_v,
#                 'All': self.did_you_mean,
#                 'Both': self.did_you_mean_suggestions_both()
#             }
#
#     # def rectified_token(self):
#     #     return \
#     #         {
#     #             auto_correction_levenshtein: self.did_you_mean_suggestions(method=auto_correction_levenshtein) if len(
#     #                 self.word) > prefix_edit_distance else {"candidate": self.word, "frequency": 0},
#     #             auto_correction_soundex: self.did_you_mean_suggestions(method=auto_correction_soundex),
#     #             'All': self.did_you_mean_suggestions(),
#     #             'Both': self.did_you_mean_suggestions_both()
#     #         }
#
#     def input_word(self, token=None):
#         if token is None:
#             word = self.word
#         else:
#             word = token
#         return word
#
#     def suggestion_probabilities(self, suggestion_words: list):
#         return {token: self.probabilities.get(token, 0) for token in suggestion_words}
#
#     # def min_edit_distance(self, source=None, target=None, ins_cost=1, del_cost=1, rep_cost=2):
#     #     """
#     #     Input:
#     #         source: a string corresponding to the string you are starting with
#     #         target: a string corresponding to the string you want to end with
#     #         ins_cost: an integer setting the insert cost
#     #         del_cost: an integer setting the delete cost
#     #         rep_cost: an integer setting the replace cost
#     #     Output:
#     #         D: a matrix of len(source)+1 by len(target)+1 containing minimum edit distances
#     #         med: the minimum edit distance (med) required to convert the source string to the target
#     #     """
#     #     if source is None and target is None:
#     #         return None, None
#     #
#     #     source = self.input_word(source)
#     #     m = len(source)
#     #     n = len(target)
#     #     D = np.zeros((m + 1, n + 1), dtype=int)
#     #     for row in range(1, m + 1):
#     #         D[row, 0] = D[row - 1, 0] + del_cost
#     #     for col in range(1, n + 1):
#     #         D[0, col] = D[0, col - 1] + ins_cost
#     #     for row in range(1, m + 1):
#     #         for col in range(1, n + 1):
#     #             r_cost = rep_cost
#     #             if source[row - 1] == target[col - 1]:
#     #                 r_cost = 0
#     #             D[row, col] = min(D[row - 1, col] + del_cost, D[row, col - 1] + ins_cost, D[row - 1, col - 1] + r_cost)
#     #     med = D[m, n]
#     #     return med
#
#     # def delete_letter(self, token=None):
#     #     word = self.input_word(token)
#     #     split_l = [(word[:i], word[i:]) for i in range(len(word) + 1) if word[i:]]
#     #     delete_l = [L + R[1:] for L, R in split_l if R]
#     #     # logger.debug(f"input word {word}, \nsplit_l = {split_l}, \ndelete_l = {delete_l}")
#     #     return delete_l
#     #
#     # def switch_letter(self, token=None):
#     #     word = self.input_word(token)
#     #     split_l = [(word[:i], word[i:]) for i in range(len(word) + 1) if word[i:]]
#     #     switch_l = [L + R[1] + R[0] + R[2:] for L, R in split_l if len(R) > 1]
#     #     # logger.debug(f"Input word = {word} \nsplit_l = {split_l} \nswitch_l = {switch_l}")
#     #     return switch_l
#     #
#     # def replace_letter(self, token=None):
#     #     word = self.input_word(token)
#     #     split_l = [(word[:i], word[i:]) for i in range(len(word) + 1) if word[i:]]
#     #     replace_l = [l + c + r[1:] for l, r in split_l if r for c in min_edit_distance_letters]
#     #     replace_set = set([i for i in replace_l if i != word])
#     #     replace_l = sorted(list(replace_set))
#     #     # logger.debug(f"Input word = {word} \nsplit_l = {split_l} \nreplace_l {replace_l}")
#     #     return replace_l
#     #
#     # def insert_letter(self, token=None):
#     #     word = self.input_word(token)
#     #     split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
#     #     insert_l = [l + c + r for l, r in split_l for c in min_edit_distance_letters]
#     #     # logger.debug(f"Input word {word} \nsplit_l = {split_l} \ninsert_l = {insert_l}")
#     #     return insert_l
#     #
#     # def edit_one_letter(self, token=None, allow_switches=True):
#     #     """
#     #     Input:
#     #         word: the string/word for which we will generate all possible wordsthat are one edit away.
#     #     Output:
#     #         edit_one_set: a set of words with one possible edit. Please return a set. and not a list.
#     #     """
#     #     word = self.input_word(token)
#     #     edit_one_set = set()
#     #     edit_one_set.update(self.insert_letter(word))
#     #     edit_one_set.update(self.replace_letter(word))
#     #     edit_one_set.update(self.delete_letter(word))
#     #     if allow_switches:
#     #         edit_one_set.update(self.switch_letter(word))
#     #     # logger.debug(f'{edit_one_set}')
#     #     return edit_one_set
#     #
#     # def edit_two_letters(self, token):
#     #     """
#     #     Input:
#     #         word: the input string/word
#     #     Output:
#     #         edit_two_set: a set of strings with all possible two edits
#     #     """
#     #     word = self.input_word(token)
#     #     edit_two_set = set()
#     #     for token in self.edit_one_letter(word):
#     #         edit_two_set.update(self.edit_one_letter(token))
#     #     return edit_two_set
#     #
#     # def edit_three_letters(self, token):
#     #     """
#     #     Input:
#     #         word: the input string/word
#     #     Output:
#     #         edit_two_set: a set of strings with all possible three edits
#     #     """
#     #     word = self.input_word(token)
#     #     edit_three_set = set()
#     #     for token in self.edit_two_letters(word):
#     #         edit_three_set.update(self.edit_one_letter(token))
#     #     return edit_three_set
#     #
#     # def bool_vocab_check(self, token=None):
#     #     word = self.input_word(token)
#     #     result = word in self.vocab
#     #     return result
#     #
#     # def vocab_check(self, token=None):
#     #     word = self.input_word(token)
#     #     result = (word in self.vocab and word)
#     #     if isinstance(result, bool):
#     #         return result
#     #     else:
#     #         return [result]
#     #
#     # def edit_one_letter_suggestions(self, token=None):
#     #     word = self.input_word(token)
#     #     outputs = self.edit_one_letter(word).intersection(self.vocab)
#     #     # logger.debug(f'{outputs}')
#     #     return outputs
#     #
#     # def edit_two_letter_suggestions(self, token=None):
#     #     word = self.input_word(token)
#     #     return self.edit_two_letters(word).intersection(self.vocab)
#     #
#     # def edit_three_letter_suggestions(self, token=None):
#     #     word = self.input_word(token)
#     #     return self.edit_three_letters(word).intersection(self.vocab)
#     #
#     # def get_suggestions(self, token=None):
#     #     word = self.input_word(token)
#     #     logger.debug(f'Input token for suggestions token->{token};word->{word}')
#     #     if len(word) >= 5:
#     #         logger.debug('Length greater than 5')
#     #         return list(
#     #             self.vocab_check(word)
#     #             or
#     #             set(list(self.edit_one_letter_suggestions(word)) + list(self.edit_two_letter_suggestions(word)))
#     #             # self.edit_one_letter_suggestions(word)
#     #             # or
#     #             # self.edit_two_letter_suggestions(word)
#     #         )
#     #     elif 3 < len(word) < 5:
#     #         logger.debug('Length greater than 3 to 5')
#     #         return list(
#     #             self.vocab_check(word)
#     #             or
#     #             self.edit_one_letter_suggestions(word)
#     #         )
#     #     else:
#     #         logger.debug('As is')
#     #         return word.split()
#     #         # or
#     #         # self.edit_three_letter_suggestions())
#     #
#     # def get_levenshtein_corrections(self, token=None):
#     #
#     #     logger.info(f'In function --> {self.get_levenshtein_corrections.__qualname__}')
#     #     word = self.input_word(token)
#     #     suggestions = self.get_suggestions(token=word)
#     #     logger.debug(f'{self.get_levenshtein_corrections.__qualname__} any 10->{suggestions[:10]}')
#     #     return suggestions
#
#     # def get_soundex_corrections(self, token=None):
#     #     # Soundex(self.word).soundex_hash
#     #     word = self.input_word(token)
#     #     # logger.info(f'In function --> {self.get_soundex_corrections.__qualname__}')
#     #     suggestions = self.vocabulary_soundex_codes.get(Soundex(word).soundex_hash, None)
#     #     # candidate_probability = self.suggestion_probabilities(suggestion_words=suggestions)
#     #
#     #     logger.debug(f"{self.get_soundex_corrections.__qualname__}--> any 10 suggestions = {suggestions[:10]}")
#     #     # self.autocorrect_metrics(suggestions)
#     #     return suggestions
#
#     def autocorrect_metrics(self, token=None, suggestions=None):
#         logger.debug(f'In fn -> {self.autocorrect_metrics.__qualname__}')
#         word = self.input_word(token)
#         # logger.debug(f'{self.autocorrect_metrics.__qualname__} word-> {word} , token->{token}')
#         candidate_probability = self.suggestion_probabilities(suggestion_words=suggestions)
#         # pickle.dump(candidate_probability, open("candidate_probability.pickle", "wb"))
#         # logger.debug(f'{self.autocorrect_metrics.__qualname__}
#         # candidate_probability for {suggestions}->{candidate_probability}')
#         # candidate_edit_distance = {suggest: self.min_edit_distance(source=word, target=suggest) for suggest in
#         #                            suggestions}
#         candidate_edit_distance = {suggest: damerauLevenshtein(word, suggest, similarity=False) for suggest in
#                                    suggestions}
#         # candidate_edit_distance_score = {suggest: np.log(
#         #     damerauLevenshtein(word, suggest, similarity=False) * damerauLevenshtein(word, suggest, similarity=True))
#         #     for suggest in
#         #     suggestions}
#         candidate_edit_distance_score = {suggest: damerauLevenshtein(word, suggest, similarity=False) for suggest in
#                                          suggestions}
#
#         # pickle.dump(candidate_edit_distance, open("candidate_edit_distance.pickle", "wb"))
#         # logger.debug(
#         #     f'{self.autocorrect_metrics.__qualname__} candidate_edit_distance for {word} ->{token}->{candidate_edit_distance}')
#
#         metrics = np.array([[i, candidate_probability.get(i, 0), candidate_edit_distance.get(i, -1),
#                              candidate_edit_distance_score.get(i, -1)]
#                             for i in suggestions], dtype=object)
#         # pickle.dump(metrics, open("metrics.pickle", "wb"))
#         # logger.debug(metrics)
#         if len(metrics) > 0:
#             # logger.debug(levenshtein_edit_threshold,min(metrics[:, 2]) + 1,idx_dist)
#             if config.get('minimum_threshold_check', None):
#                 idx_dist = np.where(metrics[:, 2] <= levenshtein_edit_threshold, True, False)
#             else:
#                 idx_dist = np.where(metrics[:, 2] <= min(metrics[:, 2]) + 1, True, False)
#             # logger.debug(idx_dist)
#             min_edit_matrix = metrics[idx_dist]
#             # logger.debug(min_edit_matrix)
#             # logger.debug(f'Minimum Distance - {self.autocorrect_metrics.__qualname__} --> {min_edit_matrix}')
#             # idx_prob = np.where(min_edit_matrix[:, 1] == max(min_edit_matrix[:, 1]), True, False)
#             min_edit_matrix_10 = list(sorted(min_edit_matrix, key=lambda item: -item[1]))
#             # logger.debug(
#             #     f'Maximum Probability - {self.autocorrect_metrics.__qualname__} --> {min_edit_matrix[idx_prob][:-40]}')
#             # distance_probability_candidates = list(min_edit_matrix[idx_prob][:, 0])
#             distance_probability_candidates = min_edit_matrix_10
#
#             return distance_probability_candidates
#         else:
#             return None
#
#     def first_letter_heuristic(self, candidates, token=None):
#         word = self.input_word(token)
#         return [candidate for candidate in candidates if candidate[0] == word[0]]
#
#     def did_you_mean_suggestions(self, token=None, method=None):
#         logger.info(f'----------------------------Starting Point -> method={method}----------------------')
#         logger.info(f'In fn -> {self.did_you_mean_suggestions.__qualname__}')
#         word = self.input_word(token)
#         logger.debug(f'Input word->{word}')
#         candidates = []
#         if method == auto_correction_soundex:
#             candidates = Soundex(word).get_soundex_corrections()
#         elif method == auto_correction_levenshtein:
#             # candidates = self.get_levenshtein_corrections(token=word)
#             candidates = Levenshtein(word).levenshtein_autocorrection
#         elif method is None:
#             logger.info('Best candidate from both of levenstien and soundex')
#             candidates = Levenshtein(word).levenshtein_autocorrection
#             # candidates = levenshtein_candidates if isinstance(levenshtein_candidates,
#             #                                                   list) else levenshtein_candidates.split()
#             # logger.debug(f'{self.did_you_mean_suggestions.__qualname__} - Levenstien candidates {candidates}')
#             candidates.extend(list(Soundex(word).get_soundex_corrections()))
#             # logger.debug(f'{self.did_you_mean_suggestions.__qualname__} - soundex candidates are '
#             #              f'{list(self.get_soundex_corrections(token=word))}')
#             candidates = list(set(candidates))
#
#         if self.first_letter_match:
#             candidates = self.first_letter_heuristic(candidates, token=word)
#
#         top_candidates = self.autocorrect_metrics(token=word, suggestions=candidates)
#         if top_candidates is not None:
#             logger.debug(f'top_candidates -> {top_candidates}')
#             # logger.debug(f'{method} --> {len(candidates)}')
#             entity_found = check_entity_candidates(np.array(top_candidates))
#             return entity_found if entity_found else {'candidate': np.array(top_candidates)[:, 0][0],
#                                                       'frequency': vocab_counts[np.array(top_candidates)[:, 0][0]]}
#             # return check_entity_candidates(top_candidates)
#         else:
#             return {'candidate': '',
#                     'frequency': 0}
#
#     def did_you_mean_suggestions_both(self):
#         # auto_correction_levenshtein: self.auto_correction_levenshtein_v,
#         # soundex_ : self.auto_correction_soundex_v,
#         # soundex_ = self.search_query_unigram_correction(method=auto_correction_soundex)
#         # levenshtein_ = self.search_query_unigram_correction(method=auto_correction_levenshtein)
#         # soundex_ = self.did_you_mean_suggestions(method=auto_correction_soundex)
#         # levenshtein_ = self.did_you_mean_suggestions(method=auto_correction_levenshtein)
#         result = [self.auto_correction_soundex_v, self.auto_correction_levenshtein_v]
#         return result
