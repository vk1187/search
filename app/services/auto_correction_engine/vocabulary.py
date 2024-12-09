from spacy.tokens.token import Token

# from app.services.auto_correction_engine import AutoCorrectionVocab
from custom_logging import logger
from elastic_connection.elastic.helper import candidates_query
from elastic_connection.elastic.helper import search_results


class VocabularyEvaluator:

    def __init__(self, word: str, index_name: str, project_id: int):
        super().__init__()
        self.word = word.strip().lower()
        candidate = [self.word]
        # self.vocab = search_results(index_name, project_query('data_dictionary', project_id))
        self.vocab = search_results(index_name, candidates_query('data_dictionary', project_id, candidate))
        # logger.debug(self.word.lower() in self.vocab)
        logger.debug(f"Count of vocabulary:{candidate} found are {self.vocab['hits']['total']['value']}")
        # self.result = (self.word in self.vocab and self.word)
        # self.vocab_check = self.result if isinstance(self.result, bool) else [self.result]

    def __call__(self):
        return self.vocab['hits']['total']['value'] > 0
        # return self.word.lower() in self.vocab


class LengthEvaluator:
    def __init__(self, word: str):
        super().__init__()
        self.word = word

    def __call__(self):
        return len(self.word) <= 3


class NonAlphabetEvaluator:
    # if True then dont run SpellCorrection Approaches
    def __init__(self, word: Token):
        super().__init__()
        self.word = word

    def __call__(self):
        try:
            if isinstance(self.word, Token):
                return self.word._.has_number
        except ValueError:
            raise ValueError("spacy Token is not passed")


# def input_evaluation(obj='', word=None, index_name=None, project_id=None):
#     objs = dict(vocabeval=VocabularyEvaluator(word, index_name, project_id), lengtheval=LengthEvaluator(word))
#     return objs[obj]


def non_alpha_evaluation(obj='', word=None):
    objs = dict(nonalphabeteval=NonAlphabetEvaluator(word))
    return objs[obj]

# class InputEngine:
#     def __init__(self, word: str, index_name: str, project_id: int):
#         self.project_id = project_id
#         self.index_name = index_name
#         self.word = word
#         self.doc = SpacyService.model_doc(
#             word
#             # original=True
#         )
#         # self.word_list = self.word.split()
#         self.word_list = [i for i in self.doc]

#     def result(self):
#         tic = time.time()
#         algo_output = {'soundex': "",
#                        'levenshtein': "",
#                        'All': ""}
#         correct_token = ''
#         check = []
#         temp_token = ''
#         overall_result = {'spellcorrection': [], 'corrected_spellings': []}
#         logger.debug(f'algo_output : {overall_result}')
#         for i in self.doc:

#             if (VocabularyEvaluator(i.text, self.index_name, self.project_id)() or
#                     LengthEvaluator(i.text)() or
#                     non_alpha_evaluation('nonalphabeteval', i)()):
#                 correct_token = ''
#                 overall_result['spellcorrection'].append(False)
#                 logger.debug(f'algo_output : {overall_result}')
#                 correct_token += i.text
#                 correct_token += i.whitespace_
#                 logger.debug(f'correct_token : {correct_token}')
#                 for key in algo_output.keys():
#                     algo_output[key] += correct_token
#                 temp_token = correct_token
#             else:
#                 overall_result['corrected_spellings'].append(i.text)
#                 overall_result['spellcorrection'].append(True)
#                 dic1 = SpellCheckEvaluator(i.text,
#                                            self.index_name,
#                                            self.project_id).output()
#                 logger.debug(f'SpellCheckEvaluator(i.text).output : {dic1}')
#                 if temp_token != correct_token:
#                     for key in dic1.keys():
#                         algo_output[key] = correct_token + dic1[key] + i.whitespace_
#                     temp_token = correct_token
#                 else:
#                     for key in dic1.keys():
#                         algo_output[key] += dic1[key] + i.whitespace_

#         # cl = np.array(algo_output[ALL_ALGORITHM].strip().split(' '))
#         cl = [i.text for i in SpacyService.model_doc(algo_output[ALL_ALGORITHM].strip())]
#         #
#         logger.debug(cl)
#         logger.debug(overall_result['spellcorrection'])
#         overall_result['spellcheck_run'] = True if sum(overall_result['spellcorrection']) > 0 else False
#         if algo_output[ALL_ALGORITHM] == self.word:
#             overall_result['spellcheck_run'] = False

#         # overall_result['corrected_spellings'] = list(
#         #     np.array(cl)[overall_result['spellcorrection']]) if algo_output[
#         #                                                             ALL_ALGORITHM] != '' else []

#         overall_result['time_elapsed'] = time.time() - tic
#         # overall_result['output'] = algo_output
#         overall_result.update(algo_output)

#         return overall_result
