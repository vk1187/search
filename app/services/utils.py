import re
import string
# from spacy.lang.en import English
# english_model = English()
# english_model_tokenizer = english_model.tokenizer
import time
from collections import Counter
from functools import partial
from functools import reduce
from itertools import chain
from typing import Generator
from typing import List
from typing import Optional
from typing import Set

import numpy as np
import spacy
from bs4 import BeautifulSoup
from spacy.lang.en.stop_words import STOP_WORDS
from unidecode import unidecode

from app.services.config_constants import blank_operator
from app.services.config_constants import did_you_mean_flag
from app.services.config_constants import remove_quotes, multiple_spaces, relatedsearch_lasttoken_list
from app.services.config_constants import token_end_punctuation
from app.services.config_constants import token_start_punctuation, clean_punctuations_start_stop_special_char, \
    hyphen_newline, operator_symbols, appostophe_s_wordboundary
from app.services.model_engine.engelish_sentence_model import EnglishModelService
# from app.services.ner_engine.ml_model.spacy import SpacyService
from app.services.slb_configuration import SLBConfiguration
from custom_logging import logger

import time


def error_message(start_time, error_message: str):
    return {
        'status': False,
        'time': time.time() - start_time,
        'Error': error_message
    }


def ner_output_format(entities, tic):
    """ Added Time value to tell the time of producing output and does not
    account time for loading of model as default models was loaded at the startup """
    final_ = {'entities': entities, 'time': time.time() - tic}
    return final_


# def ner_output_converter(entity_op):
#     """Converts output from spacy and transformer models to unified format"""
#     output_f = {"Location": [], "Person": [], "Organization": [], "Percentage": [], "Date": [], "Cardinal": [], }

#     for i in entity_op:
#         if i in ['LOC', 'GPE']:  # , 'NORP'
#             output_f['Location'].extend(entity_op[i])
#         if i in ['PER', 'Person', 'PERSON']:
#             output_f['Person'].extend(entity_op[i])
#         if i in ['PERCENT']:
#             output_f['Percentage'].extend(entity_op[i])
#         if i in ['DATE']:
#             output_f['Date'].extend(entity_op[i])
#         if i in ['ORG']:
#             output_f['Organization'].extend(entity_op[i])
#         if i in ['Cardinal', 'CARDINAL']:
#             output_f['Cardinal'].extend(entity_op[i])

#     return output_f


def convert_unidecode(text, force_run=False):
    """Converts unicode to ascii"""
    if force_run:
        return unidecode(text)
    else:
        return text


def flatten(listOfLists):
    """retuns a list from nested list"""
    return chain.from_iterable(listOfLists)


class SpacyModel:

    def __init__(self):
        self.nlp = spacy.load(
            SLBConfiguration.get_config()['Spacy']['SPACY_MODEL'])

    def __call__(self):
        return self.nlp


# spacy_model = SpacyModel()
def delete_custom_patterns(document, compiled_regex,replace_pattern=None):
    if replace_pattern==None:
       replace_pattern =' '
    document = compiled_regex.sub(replace_pattern, document)
    return document


def delete_custom_patterns_nospace(document, compiled_regex):
    document = compiled_regex.sub('', document)
    return document

def delete_custom_patterns_fullstop(document, compiled_regex):
    document = compiled_regex.sub('.', document)
    return document

def _lowercase(obj):
    """ Make dictionary lowercase """
    if isinstance(obj, dict):
        return {k.lower(): _lowercase(v) for k, v in obj.items()}
    elif isinstance(obj, (list, set, tuple)):
        t = type(obj)
        return t(_lowercase(o) for o in obj)
    elif isinstance(obj, str):
        return obj.lower()
    else:
        return obj


def min_max_normalization(x):
    """Min_Max Normalization"""
    diff = np.max(x) - np.min(x)
    if diff == 0:
        return np.array([0.0] * x.shape[0])
    else:
        return np.round(((x - np.min(x)) / (diff)) * 100, 2)


def global_clean_punctuations_start_stop(document, ignore_dot=False):
    special_char = clean_punctuations_start_stop_special_char
    all_symbols = string.punctuation + special_char
    if ignore_dot:
        all_symbols = all_symbols.replace('.', '')
    try:
        if (document[0] == document[-1]) & (
                document[0] in all_symbols) & len(document) == 1:
            document = ''

        elif document[-1] in all_symbols:

            document = document[:-1]
            document = global_clean_punctuations_start_stop(document)
        elif document[0] in all_symbols:
            document = document[1:]
            document = global_clean_punctuations_start_stop(document)
        else:
            pass
        return document
    except Exception as e:
        #             print(f'{e}')
        return document


def trendingsearch_relatedsearch_widget_cleaner(text):
    # data_obj = DataPreprocessor(text)
    # data_obj.clean_punctuations_start_stop()
    # clean_term = data_obj.document
    clean_term = global_clean_punctuations_start_stop(text.strip())
    text = delete_custom_patterns(clean_term, operator_symbols)
    text = convert_unidecode(text).strip()

    for i in [appostophe_s_wordboundary, remove_quotes, multiple_spaces]:
        text = delete_custom_patterns(text, i).strip()
    while (text.split(' ')[-1] in relatedsearch_lasttoken_list):
        text = text.split(' ')[:-1]
        text = ' '.join(text)
    # text = delete_custom_patterns(text, relatedsearch_lasttoken_patterns)
    # text = delete_custom_patterns(text, remove_quotes)
    # text = delete_custom_patterns(text, multiple_spaces)
    return text

def fix_top_N(input_text, list_to_compare):
    input_query_processed = re.sub(r'\s', '', input_text.lower())
    pattern = re.compile(r'\b' + re.escape(input_query_processed) + r'\b', re.IGNORECASE)
    unique_queries = set()
    filtered_entities = []
    
    for entity in list_to_compare:
        query = re.sub(r'\s', '', entity['query'].lower())
        if query not in unique_queries and not pattern.search(re.sub(r'\s', '', query)):
            unique_queries.add(query)
            filtered_entities.append(entity)
    
    filtered_entities.sort(key=lambda x: x['score'], reverse=True)
    return filtered_entities[:5]


class DataPreprocessor:
    """Preprocess data"""

    def __init__(self, document, flag_section_name=None):
        self.irrelevant_search_text = ''
        self.document = None
        self.flag_section_name = flag_section_name
        self.parse_data(document)
        # if isinstance(document, list) and sum([isinstance(i, dict) for i in document]) == len(document):
        #     self.document = self.parse_json_values(document)
        # if isinstance(document, list):
        #     self.document = document[0]
        #     self.irrelevant_search_text = document[1]
        # else:
        #     self.document = document
        self.extracted_emails = ''
        self.urls = ''
        # [!#\$%\(\)\*\+,\./:;<=>\?@\[\\\]\^_`”{\|}©]
        self.valid_punctuations = ''.join(
            [i for i in string.punctuation if i not in "-#/:;<=>@[\]^_`{|}~"])

        self.punctuation_regex = re.compile('[%s]' %
                                            re.escape(self.valid_punctuations))
        self.double_quote_pattern = re.compile('\".*?\"')
        self.unknown_symbol_regex = re.compile('')

    def __call__(self):
        self.preprocessing()
        return self.document

    def convert_to_strings(self, data):
        if isinstance(data, list):
            converted_list = []
            for item in data:
                converted_list.append(self.convert_to_strings(item))
            return converted_list
        return str(data)

    def parse_data(self, document):
        """returns the dcoument which is parseable"""
        document = self.convert_to_strings(document)
        if self.flag_section_name == did_you_mean_flag:
            self.document = BeautifulSoup(
                convert_unidecode('. '.join(document)), "lxml").text
        elif isinstance(document, list):
            self.document = document[0]
            self.irrelevant_search_text = document[1]
        else:
            self.document = document

    def parse_json_values(self, document):
        """reurns documents in string format from json format"""
        doc = '. '.join([
            '. '.join(list(document[idx].values()))
            for idx in range(len(document))
        ])
        return doc

    def remove_words(self, list_of_tokens, words_to_be_removed):
        """removes the list of tokens mentioned"""
        return ' '.join(
            list(
                filter(lambda w: w.lower() not in words_to_be_removed,
                       list_of_tokens)))

    def preprocessing(self):
        """applies preprocessing on the documents based upon the configuration mentioned"""
        config = SLBConfiguration.get_config(self.flag_section_name)

        if config.get('clean_punctuations_start_stop', None):
            self.clean_punctuations_start_stop()
        if config.get('split_by_delim', None):
            self.document = re.sub('\n‹#›\n', '~~', self.document)
            self._find_and_remove_header_footer(100, 0, 1)
        if config.get('remove_non_utf8', None):
            self.remove_non_utf8()
        if config.get('remove_tn', None):
            self.remove_tn()
        if config.get('remove_newline_tab_characters', None):
            self.remove_newline_tab_characters()
        if config.get('stop_words', None):
            self.remove_stopwords()
        if config.get('freq_words', None):
            self.remove_freq_words()
        if config.get('rare_words', None):
            self.remove_rare_words()
        if config.get('lemmatization', None):
            self.lemmatize_words()
        if config.get('remove_html_tags', None):
            self.remove_html()
        if config.get('spell_check', None):
            self.correct_spellings()
        if config.get('remove_email', None):
            email_id = re.compile(r'[\w\.-]+@[\w\.-]+')
            self.extracted_emails = self.remove_patterns(email_id)
        if config.get('remove_websites', None):
            url_regex = re.compile(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            )
            self.urls = self.remove_patterns(url_regex)
        if config.get('remove_punctuation', None):
            self.remove_punctuation()
        if config.get('remove_unknown_symbols', None):
            self.remove_unknown_symols()
        if config.get('remove_numerics', None):
            numeric = re.compile(r'\b[0-9]+\b\s*')
            self.numbers_removed = self.remove_patterns(numeric)
        if config.get('show_abbreviations', None):
            all_caps_regex = re.compile(r'[A-Z]{2,}')
            self.show_pattern(all_caps_regex)
        if config.get('remove_single_char', None):
            # single_char_regex = re.compile(r'(?:^| )\w(?:$| )')
            single_char_regex = re.compile(r'\b[A-Za-z] +\b|\b +[A-Za-z]\b')
            self.chars_removed = self.remove_patterns(single_char_regex)
        if config.get('remove_double_spaces', None):
            self.remove_double_spaces()
        if config.get('remove_page_no', None):
            page_regex = re.compile('[Pp]age \d')
            self.page_no = self.remove_patterns(page_regex)
        if config.get('custom_patterns', None):
            self.document = hyphen_newline.sub('', self.document)
        if config.get('lower_case', None):
            self.lower_case()
        if config.get('tokenize', None):
            temp_list = []
            total_len = len(self.document)
            # batch_range = math.ceil(total_len/SpacyService.model().max_length)

            batched_data = EnglishModelService.tokenizer()(self.document)
            # for i in range(batch_range):
            # logger.debug(f'Processing Text in batches...In Progress: {i+1}/{batch_range}')
            # start_idx=i*SpacyService.model().max_length
            # end_index=(i+1)*SpacyService.model().max_length
            # batched_data = SpacyService.model().pipe(self.document[start_idx:end_index],n_process=-1,disable)
            # with SpacyService.model().select_pipes(enable="parser"):
            #     batched_data = SpacyService.model()(self.document,n_process=-1)
            # batched_data = SpacyService.model().pipe(self.document,n_process=-1,disable)
            cleaned_data = [
                i.text for i in batched_data
                if i.text not in string.punctuation
            ]
            temp_list.extend(cleaned_data)
            # temp_list.index("phisticated")
            # temp_list.index("ber")
            self.document = temp_list  # self.document = [i.text for i in SpacyService.model()(self.document) if i.text not in string.punctuation]
        if config.get('remove_word_containing_hash', None):
            self.remove_word_containing_hash()
        if config.get('replace_underscore_whitespace', None):
            self.replace_underscore_whitespace()
        if config.get('remove_alpha_numeric', None):
            self.remove_alpha_numeric()
        if config.get('remove_args_text', None):
            self.remove_args_text()
        if config.get('stripped_doc', None):
            self.stripped_doc()
        if config.get('non_transformable_phrases', None):
            self.non_transformable_phrases()
        if config.get('make_one_large_corpus', None):
            self.make_one_large_corpus()
        if config.get('make_one_gensim_phrase_large_corpus', None):
            self.make_one_gensim_phrase_large_corpus()

    def stripped_doc(self):
        """

        :return: removes punctuation from the start and stop position of any token
        """
        doc_re = re.sub(self.double_quote_pattern, "", self.document)
        logger.info(f'Replaced Double Quotes with  blank: {doc_re}')
        logger.info(f'{[i for i in doc_re.split()]}')
        logger.info(
            f'Removed punctuation from above input : {[self.strip_punctuation(i) for i in re.sub(self.double_quote_pattern, "", self.document).split() if len(i) > 1]}'
        )

        self.document = blank_operator.join(final_op for final_op in [
            self.strip_punctuation(i) for i in re.sub(
                self.double_quote_pattern, "", self.document).split()
            if len(i) > 1
        ] if len(final_op) > 1)

    def remove_tn(self):
        self.document = re.sub("[\\n|\\t]", " ", self.document)
        self.document = re.sub(" +", " ", self.document)

    def make_one_large_corpus(self):
        self.document = ' '.join([
            ' '.join(i.split()) for i in self.document.split('\n')
            if i.split()
        ]).split()
        logger.debug(f'make_one_large_corpus: {self.document}')

    def make_one_gensim_phrase_large_corpus(self):
        self.document = [
            i.split() for i in self.document.split('\n') if i.split()
        ]
        logger.debug(f'make_one_gensim_phrase_large_corpus: {self.document}')

    def non_transformable_phrases(self):

        self.document = '|'.join([
            i.group()[1:-1]
            for i in re.finditer(pattern=self.double_quote_pattern,
                                 string=self.document)
        ]).split('|')

    def remove_args_text(self):
        self.document = self.remove_words(self.document,
                                          self.irrelevant_search_text)

    def check_last_punctuation(self, text):
        """removes punctuaion from the end of input string"""
        try:
            if text[-1] in token_end_punctuation:

                return self.check_last_punctuation(text[:-1])
            else:
                return text
        except IndexError as e:
            return text
        except Exception as ee:
            logger.error(f'{ee}')

    def check_first_punctuation(self, text):
        """removes punctuaion from the start of input string"""
        try:
            if text[0] in token_start_punctuation:
                return self.check_first_punctuation(text[1:])
            else:
                return text
        except IndexError as e:
            return text
        except Exception as ee:
            logger.error(f'{ee}')

    def strip_punctuation(self, text):
        """removes start and end punctuation for given input string"""
        text = self.check_last_punctuation(text)
        text = self.check_first_punctuation(text)
        return text

    def replace_underscore_whitespace(self):
        """replace unserscores with whitespace for given input string"""
        # logger.debug(f'{self.document} - replacing words containing _')

        if '_' in self.document:
            logger.debug(f'{self.document} replacing underscore')
            self.document = self.document.replace('_', ' ')

    def remove_word_containing_hash(self):

        # logger.debug(f'{self.document}removing words containing hash')
        if '#' in self.document:
            logger.debug(f'{self.document} - removing # words')
            self.document = ""

    def clean_punctuations_start_stop(self):
        special_char = clean_punctuations_start_stop_special_char
        all_symbols = string.punctuation + special_char
        try:
            logger.debug(
                f'{self.document, self.document[-1], self.document[0]}')
            if (self.document[0] == self.document[-1]) & (
                    self.document[0] in all_symbols) & (len(self.document)
                                                        == 1):
                self.document = ''

            elif self.document[-1] in all_symbols:
                # logger.debug(f'Removing Punctuation - new doc is {self.document[:-1]}')
                self.document = self.document[:-1]
                self.clean_punctuations_start_stop()
            elif self.document[0] in all_symbols:
                # logger.debug(f'Removing Punctuation - new doc is {self.document[1:]}')
                self.document = self.document[1:]
                self.clean_punctuations_start_stop()
            else:
                pass
        except Exception as e:
            logger.error(f'{e}')

    def remove_newline_tab_characters(self):
        # self.document = re.sub('\n‹#›\n', '~~', self.document)
        self.document = re.sub('\n+', '\n', self.document)
        self.document = self.document.replace('\n\t', '. ').replace('\t', '. ')
        self.document = self.document.replace('\n',
                                              '. ').replace('..', '.').replace(
                                                  '. . ', '. ')

    def lower_case(self):
        self.document = ''.join([
            x.lower() for x in self.document
        ])  # logger.debug(f'lower_case : {self.document}')

    def remove_punctuation(self):
        """https://stackoverflow.com/questions/265960/best-way-to-strip-punctuation-from-a-string"""
        """To remove the punctuation"""
        # logger.debug(f'Original Document to remove punctuation {self.document}')
        self.document = self.punctuation_regex.sub(
            ' ', self.document)  # logger.debug(f'Cleaned doc {self.document}')
    
    def remove_unknown_symols(self):
    
        """To remove the unknown symbols"""
        self.document = self.unknown_symbol_regex.sub(
            ' ', self.document)  # logger.debug(f'Cleaned doc {self.document}')

    def remove_stopwords(self):
        self.document = self.remove_words(self.document.split(' '), STOP_WORDS)

    def remove_freq_words(self, n_words=10):
        text_counter = Counter(self.document.split(' '))
        frequent_words = [w for (w, wc) in text_counter.most_common(n_words)]
        print('removing ', frequent_words)
        self.document = self.remove_words(self.document.split(' '),
                                          frequent_words)

    def remove_rare_words(self, n_words=10):
        text_counter = Counter(self.document.split(' '))
        rare_words = set(
            [w for (w, wc) in text_counter.most_common()[:-n_words - 1:-1]])
        print('removing ', rare_words)
        self.document = self.remove_words(self.document.split(' '), rare_words)

    def remove_non_utf8(self):
        self.document = ''.join(
            [token for token in self.document if ord(token) < 128])

    def replace_non_utf8(self):
        self.document = ''.join([
            convert_unidecode(token, force_run=True) for token in self.document
        ])  # logger.debug(f'remove_non_utf8 : {self.document}')

    def remove_alpha_numeric(self):
        out = False
        regex = "^(?=.*[a-zA-Z])(?=.*[0-9])[A-Za-z0-9]+$"
        p = re.compile(regex)
        if self.document is None:
            out = False
        if re.search(p, self.document):
            out = True
        else:
            out = False

        if out:
            self.document = ''

    # if self.document.isalnum():
    #     self.document = ''

    def lemmatize_words(self):
        pass  # return ' '.join(token.lemma_ for token in self.text)

    def remove_html(self):
        html_pattern = re.compile('<.*?>')
        self.document = html_pattern.sub(r'', self.document)
        logger.debug(f'remove_html_flag: {self.document}')

    def remove_patterns(self, compiled_regex):
        match = compiled_regex.findall(self.document)
        match = list(set(match))

        if len(match) > 0:
            # logger.debug(f'{match} - patterns removed ')
            self.document = compiled_regex.sub(' ', self.document)
            # logger.debug(f'remove_patterns: {self.document, match}')

            return match
        else:
            pass

    def show_pattern(self, compiled_regex):
        match = compiled_regex.findall(self.document)
        match = list(set(match))
        if len(match) > 0:
            print(match)
        else:
            pass

    def remove_numerics(self):
        numeric = re.compile(r'\d')
        self.document = self.remove_patterns(numeric)

    def lemmatize_words(self):
        pass  # return ' '.join(token.lemma_ for token in self.text)

    def remove_html(self):
        html_pattern = re.compile('<.*?>')
        self.document = html_pattern.sub(r'', self.document)

    def remove_double_spaces(self):
        double_spaces_regex = re.compile(' +')
        self.document = double_spaces_regex.sub(
            r' ', self.document
        )  # logger.debug(f'remove_double_spaces: {self.document}')

    def _find_and_remove_header_footer(self, n_chars: int,
                                       n_first_pages_to_ignore: int,
                                       n_last_pages_to_ignore: int) -> str:
        pages = self.document.split("~~")

        # header
        start_of_pages = [
            p[:n_chars]
            for p in pages[n_first_pages_to_ignore:-n_last_pages_to_ignore]
        ]
        found_header = self._find_longest_common_ngram(start_of_pages)
        if found_header:
            pages = [page.replace(found_header, "") for page in pages]

        # footer
        end_of_pages = [
            p[-n_chars:]
            for p in pages[n_first_pages_to_ignore:-n_last_pages_to_ignore]
        ]
        found_footer = self._find_longest_common_ngram(end_of_pages)
        if found_footer:
            pages = [page.replace(found_footer, "") for page in pages]
        # logger.debug(f"Removed header '{found_header}' and footer '{found_footer}' in document")
        self.document = ".".join(pages)  # return text

    def _ngram(self, seq: str, n: int) -> Generator[str, None, None]:
        """
        Return ngram (of tokens - currently split by whitespace)
        :param seq: str, string from which the ngram shall be created
        :param n: int, n of ngram
        :return: str, ngram as string
        """

        # In order to maintain the original whitespace, but still consider \n and \t for n-gram tokenization,
        # we add a space here and remove it after creation of the ngrams again (see below)
        seq = seq.replace("\n", " \n")
        seq = seq.replace("\t", " \t")

        words = seq.split(" ")
        ngrams = (" ".join(words[i:i + n]).replace(" \n",
                                                   "\n").replace(" \t", "\t")
                  for i in range(0,
                                 len(words) - n + 1))

        return ngrams

    def _allngram(self, seq: str, min_ngram: int, max_ngram: int) -> Set[str]:
        lengths = range(min_ngram, max_ngram) if max_ngram else range(
            min_ngram, len(seq))
        ngrams = map(partial(self._ngram, seq), lengths)
        res = set(chain.from_iterable(ngrams))
        return res

    def _find_longest_common_ngram(self,
                                   sequences: List[str],
                                   max_ngram: int = 30,
                                   min_ngram: int = 3) -> Optional[str]:
        """
        Find the longest common ngram across different text sequences (e.g. start of pages).
        Considering all ngrams between the specified range. Helpful for finding footers, headers etc.
        :param sequences: list[str], list of strings that shall be searched for common n_grams
        :param max_ngram: int, maximum length of ngram to consider
        :param min_ngram: minimum length of ngram to consider
        :return: str, common string of all sections
        """
        sequences = [s for s in sequences if s]  # filter empty sequences
        if not sequences:
            return None
        seqs_ngrams = map(
            partial(self._allngram, min_ngram=min_ngram, max_ngram=max_ngram),
            sequences)
        intersection = reduce(set.intersection, seqs_ngrams)

        try:
            longest = max(intersection, key=len)
        except ValueError:
            # no common sequence found
            longest = ""
        return longest if longest.strip() else None


# def correct_spellings(self):
#     spell = SpellChecker()
#     corrected_text = []
#     misspelled_words = spell.unknown(self.document.split())
#     for word in self.document.split():
#         if word in misspelled_words:
#             corrected_text.append(spell.correction(word))
#         else:
#             corrected_text.append(word)
#     self.document = " ".join(corrected_text)

# f = open('d://SearchLego-1//SearchLego_CognitiveServices//app//text.json', encoding='utf8')

# data = json.load(f)
# # url_regex = re.compile(r'http[s].\S*')
# # match = url_regex.findall(data['Content'])
# # print(match)
# z = DataPreprocessor(data['Content'])
# ff = open('d://SearchLego-1//SearchLego_CognitiveServices//app//clean.text', mode='w+', encoding='utf8')
# ff.write(z())
# ff.close()
# print(z.page_no)
# # print(z.urls)
# print(DataPreprocessor('rakshit,sakhuja').remove_punctuation())
