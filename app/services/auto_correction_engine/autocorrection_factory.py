import time

from spacy.tokens.token import Token

# from app.services.auto_correction_engine import AutoCorrectionVocab
from app.services.auto_correction_engine.candidate_factory import SpellCheckEvaluator
from app.services.config_constants import ALL_ALGORITHM
from app.services.ner_engine.ml_model.spacy import SpacyService
from custom_logging import logger
from elastic_connection.elastic.helper import candidates_query
from elastic_connection.elastic.helper import search_results
from app.services.similarity_engine import acronym_expansion


class VocabularyEvaluator:
    """Check if the token is present in the vocabulary or not """

    def __init__(self, word: str, index_name: str, project_id: int):
        super().__init__()
        self.word = word.strip().lower()
        candidate = [self.word]
        # self.vocab = search_results(index_name, project_query('data_dictionary', project_id))
        self.vocab = search_results(
            index_name,
            candidates_query('data_dictionary', project_id, candidate))
        # logger.debug(self.word.lower() in self.vocab)
        # logger.debug(
        #     f"Count of vocabulary:{candidate} found are {self.vocab['hits']['total']['value']}"
        # )
        # self.result = (self.word in self.vocab and self.word)
        # self.vocab_check = self.result if isinstance(self.result, bool) else [self.result]

    def __call__(self):
        return self.vocab.get('hits', False).get('total',
                                                 False).get('value') > 0
        # return self.vocab['hits']['total']['value'] > 0
        # return self.word.lower() in self.vocab


class AcronymEvaluator:

    def __init__(self, word: str):
        super().__init__()
        self.word = word.strip().lower()
        # client = MongoConnection.getInstance()
        self.expanded_terms = acronym_expansion(self.word, None)

        # collection = client[search_analytics_database_name][Acronym_collection_name]
        # cursr_search_logs = collection.aggregate(
        #     search_analytics_count_pipeline(project_id, client_id, excludedDomains, delta_days))
        # # candidate = [self.word]
        # # self.vocab = search_results(index_name, project_query('data_dictionary', project_id))
        # self.vocab = search_results(index_name, candidates_query('data_dictionary', project_id, candidate))
        # # logger.debug(self.word.lower() in self.vocab)
        # logger.debug(f"Count of vocabulary:{candidate} found are {self.vocab['hits']['total']['value']}")
        # # self.result = (self.word in self.vocab and self.word)
        # # self.vocab_check = self.result if isinstance(self.result, bool) else [self.result]

    def __call__(self):
        if self.expanded_terms is None:
            return False
        else:
            return True
        # return self.vocab.get('hits', False).get('total', False).get('value') > 0
        # return self.vocab['hits']['total']['value'] > 0
        # return self.word.lower() in self.vocab


class LengthEvaluator:
    """check if the given input length is lower than 3 or not"""

    def __init__(self, word: str):
        super().__init__()
        self.word = word

    def __call__(self):
        return len(self.word) <= 3


class NonAlphabetEvaluator:
    """check if alphabet contains numeric or special charatcters as well """

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


class InputEngine:
    """Class to evaluate if autocorrection needs to run or not"""

    def __init__(self, word: str, index_name: str, project_id: int,
                 client_id: int):
        print('Start AutoCorrection Output')
        self.project_id = project_id
        self.client_id = client_id
        self.index_name = index_name
        self.quote_counter = 0
        self.word = word
        # self.query_operator_obj = QueryOperationHandler(word)
        # if self.query_operator_obj()[1]==True:
        #    self.Operator_query = self.query_operator_obj.raw_query

        self.doc = SpacyService.model_doc(word, self.client_id
                                          # original=True
                                          )
        # self.word_list = self.word.split()
        self.word_list = [i for i in self.doc]

    def word_(self, idx):
        if isinstance(idx, int):
            return (self.word_list[idx].text.strip())
        else:
            return idx

    def runnable(self, i):
        """operator compaitbility and mapping"""

        if self.word_(i) == 'NOT':
            return True
        if self.word_(i) == 'AND':
            return True
        if self.word_(i) == 'OR':
            return True
        if '"' in self.word_(i):
            self.quote_counter += 1

            return True
        if '-' in self.word_(i):
            return True
        if '!' in self.word_(i):
            return True
        if '-' in self.word_(i - 1) and len(self.word_(i - 1)) == 1:
            return True
        if '!' in self.word_(i - 1) and len(self.word_(i - 1)) == 1:
            return True
        if '+' in self.word_(i) and len(self.word_(i)) <= 3:
            return True
        if '&&' in self.word_(i) and len(self.word_(i)) <= 3:
            return True
        if '|' in self.word_(i) and len(self.word_(i)) <= 3:
            return True
        if '||' in self.word_(i) and len(self.word_(i)) <= 3:
            return True
        if '&' in self.word_(i) and len(self.word_(i)) <= 3:
            return True
        if '+' in self.word_(i) and len(self.word_(i)) > 3:
            return False
        if '&&' in self.word_(i) and len(self.word_(i)) > 3:
            return True
        if '|' in self.word_(i) and len(self.word_(i)) > 3:
            return True
        if '||' in self.word_(i) and len(self.word_(i)) > 3:
            return True
        if '&' in self.word_(i) and len(self.word_(i)) > 3:
            return True
        elif self.quote_counter % 2 != 0:

            return True
        else:
            self.quote_counter = 0
            return False

    def result(self, inp_time):
        tic = inp_time
        algo_output = {'soundex': "", 'levenshtein': "", 'All': ""}
        correct_token = ''
        check = []
        temp_token = ''
        overall_result = {'spellcorrection': [], 'corrected_spellings': []}
        logger.debug(f'algo_output : {overall_result}')
        for idx in range(len(self.word_list)):
            i = self.word_list[idx]
            # for i in self.doc:

            if (self.runnable(idx) or VocabularyEvaluator(
                    i.text, self.index_name, self.project_id)()
                    or LengthEvaluator(i.text)()
                    or non_alpha_evaluation('nonalphabeteval', i)()
                    or AcronymEvaluator(i.text)()):
                correct_token = ''
                overall_result['spellcorrection'].append(False)
                logger.debug(f'algo_output : {overall_result}')
                correct_token += i.text
                correct_token += i.whitespace_
                logger.debug(f'correct_token : {correct_token}')
                for key in algo_output.keys():
                    algo_output[key] += correct_token
                temp_token = correct_token
            else:
                # overall_result['corrected_spellings'].append(i.text)

                spellcheck_dictionary = SpellCheckEvaluator(
                    i.text, self.index_name, self.project_id,
                    self.client_id).output()
                logger.debug(
                    f'SpellCheckEvaluator(i.text).output : {spellcheck_dictionary}'
                )
                if temp_token != correct_token:
                    if len(spellcheck_dictionary.keys()) > 0:
                        for key in spellcheck_dictionary.keys():
                            algo_output[
                                key] = correct_token + spellcheck_dictionary[
                                    key] + i.whitespace_
                        temp_token = correct_token
                else:
                    if len(spellcheck_dictionary.keys()) > 0:
                        for key in spellcheck_dictionary.keys():
                            algo_output[key] += spellcheck_dictionary[
                                key] + i.whitespace_
                if spellcheck_dictionary[ALL_ALGORITHM] != i.text:
                    overall_result['corrected_spellings'].append(
                        spellcheck_dictionary[ALL_ALGORITHM])
                    overall_result['spellcorrection'].append(True)
                else:
                    overall_result['spellcorrection'].append(False)

        # cl = np.array(algo_output[ALL_ALGORITHM].strip().split(' '))
        output_split = [
            i.text + i.whitespace_ for i in SpacyService.model_doc(
                algo_output[ALL_ALGORITHM].strip(), self.client_id)
        ]
        #
        logger.debug(output_split)
        logger.debug(overall_result['spellcorrection'])
        overall_result['spellcheck_run'] = True if sum(
            overall_result['spellcorrection']) > 0 else False
        if algo_output[ALL_ALGORITHM] == self.word:
            overall_result['spellcheck_run'] = False

        # overall_result['corrected_spellings'] = list(
        #     np.array(cl)[overall_result['spellcorrection']]) if algo_output[
        #                                                             ALL_ALGORITHM] != '' else []
        
        overall_result.update(algo_output)
        overall_result['input_split'] = [
            i.text + i.whitespace_ for i in self.doc
        ]
        overall_result['output_split'] = output_split

        overall_result['time_elapsed'] = time.time() - tic
        # overall_result['output'] = algo_output

        return overall_result
