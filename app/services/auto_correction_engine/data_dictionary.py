import json
from collections import defaultdict

from app.services.auto_correction_engine.soundex import Soundex
from app.services.config_constants import *
from custom_logging import logger
import time
from unidecode import unidecode

# import en_core_web_sm

# nlp = en_core_web_sm.load()

# data_dic = {}
# for i in sorted(vocab):
#     data_dic[i] = {'frequency': word_count_dict[i],
#                    'probabilities': probabilities[i]}
#
# return {
#     "data_dictionary": data_dic,
#     "vocabulary_soundex_codes": vocabulary_soundex_codes
# }


class DidYouMean:

    def __init__(self, pid):
        self.file_path = ''
        self.input = ''
        self.pid = pid

    def fetch_data(self, input_: str):
        """
       returns a list containing all the words in the corpus 
        """
        self.input = input_
        if isinstance(self.input, str) and os.path.isfile(self.input):
            with open(self.input, 'r', encoding='utf-8-sig') as f:
                document = json.load(f)
                f.close()
                # document = json.load(open(self.input, 'r', encoding='utf-8-sig'))
        elif isinstance(self.input, list) and sum(
            [isinstance(i, dict) for i in self.input]) == len(self.input):
            document = self.input
        else:
            return None
        return document

    def preprocess_data(self, input_):
        document = self.fetch_data(input_)

        doc = '. '.join([
            '. '.join(list(document[idx].values()))
            for idx in range(len(document))
        ])
        doc = doc.lower()
        words = re.findall('\w+', doc)
        return words

    #         keys = document.keys()
    # #         for key in keys:
    # #             if document[key] in ['', ' ', None]:
    # #                 continue
    # #             else:

    #         # if api.payload['document'] in ['', ' ', None]:
    #         #     logger.warning('Document passed should be containing strings rather than blanks')
    #         # document = DataPreprocessor(api.payload['document'], data_preprocessing_flag)()
    #         document = DataPreprocessor('. '.join(list(api.payload.values())), data_preprocessing_flag)()

    #         list(document.values())
    #         doc = nlp(document)
    #         print(doc)

    def get_count(self, word_l):
        """
        Input:
            word_l: a set of words representing the corpus.
        Output:
            word_count_dict: The wordcount dictionary where key is the word and value is its frequency.
        """

        word_count_dict = {}  # fill this with word counts
        for token in word_l:
            word_count_dict[token] = word_count_dict.get(token, 0) + 1

        return word_count_dict

    def get_probability(self, word_count_dictionary):
        """return probability for the input vocabulary"""
        total_word_count = sum(word_count_dictionary.values())
        vocab_probabilities = {
            i: (j / total_word_count)
            for i, j in word_count_dictionary.items()
        }
        return vocab_probabilities

    def vocabulary_soundex_codes_fn(self, vocab):
        """return soundex codes for the input vocabulary"""
        vocab_codes = defaultdict(list)
        for i in vocab:
            try:
                sound_code = Soundex(word=unidecode(i),
                                     index_name=None,
                                     project_id=self.pid).soundex_code()
                # logger.debug(f'sound_code:{sound_code}')
                if sound_code is not None:
                    vocab_codes[sound_code].append(i)
                else:
                    logger.info(f'Soundex code not found for please validate: {i}')
                    continue
            except Exception as e:
                logger.error(f'Invalid vocab found: {i}')
                logger.exception(e)
                continue

        return vocab_codes

    def output(self, input_):
        """Returns output after computing word count, probabilities and respectvie soundex codes"""
        tic = time.time()
        # word_l = self.preprocess_data(input)
        if input_ is None:
            return self.output_template()
        vocab = list(set(input_))
        word_count_dict = self.get_count(input_)
        probabilities = self.get_probability(word_count_dict)
        # print(probabilities)
        vocabulary_soundex_codes = self.vocabulary_soundex_codes_fn(vocab)
        return self.output_template(vocab, word_count_dict, probabilities,
                                    vocabulary_soundex_codes)

    def output_template(self,
                        vocab=None,
                        word_count_dict=None,
                        probabilities=None,
                        vocabulary_soundex_codes=None):
        """Output Format for Did You Mean Endpoint"""

        output_result = []
        if vocab is None and word_count_dict is None and probabilities is None and vocabulary_soundex_codes is None:
            return \
                {data_dictionary_key: None,
                 data_dictionary_type: None,
                 data_dictionary_projectid: self.pid,
                 data_dictionary_attributes:
                     {data_dictionary_frequency: 0,
                      data_dictionary_probabilities: 0,
                      data_dictionary_values: []}}
        else:
            for i in sorted(vocab):
                output_dict = {
                    data_dictionary_key: i,
                    data_dictionary_type: 'data_dictionary',
                    data_dictionary_projectid: self.pid,
                    data_dictionary_attributes: {}
                }
                output_dict[data_dictionary_attributes][
                    data_dictionary_frequency] = word_count_dict[i]
                output_dict[data_dictionary_attributes][
                    data_dictionary_probabilities] = probabilities[i]
                output_dict[data_dictionary_attributes][
                    data_dictionary_values] = []
                output_result.append(output_dict)
            for i in vocabulary_soundex_codes:
                output_dict = {
                    data_dictionary_key: i,
                    data_dictionary_type: 'soundex',
                    data_dictionary_projectid: self.pid,
                    data_dictionary_attributes: {}
                }
                output_dict[data_dictionary_attributes][
                    data_dictionary_frequency] = 0
                output_dict[data_dictionary_attributes][
                    data_dictionary_probabilities] = 0
                output_dict[data_dictionary_attributes][
                    data_dictionary_values] = vocabulary_soundex_codes[i]
                output_result.append(output_dict)
            return output_result
