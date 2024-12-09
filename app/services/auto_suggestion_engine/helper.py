import re
import time

from bs4 import BeautifulSoup

from app.services.config_constants import appostophe_s_wordboundary,appostophe_removal, number_identification, paranthesis_enclosed_tokens
# from utils import DataPreprocessor
from app.services.config_constants import auto_completion_min_shingle_length, auto_completion_max_shingle_length, page_regex
from app.services.config_constants import decimal1, decimal2, complete_number, decimal3, decimal4, decimal5, decimal6, decimal7 ,\
    special_symbols, multiple_spaces,decimal8,decimal9
from app.services.config_constants import decimal_numbers, date4, date3, date2, date1, hyphen_newline
from app.services.config_constants import double_hyphens, word_hyphen_word_regex, pure_alphanumeric_regex
from app.services.config_constants import email_id_pattern, document_splitter_regex, hyphenated_spaces
from app.services.config_constants import http_url_regex, www_url_regex, not_allwed_punctuations_pattern
from app.services.config_constants import square_paranthesis_enclosed_tokens, curely_paranthesis_enclosed_tokens
from app.services.model_engine.engelish_sentence_model import EnglishSentenceModelService
from app.services.utils import convert_unidecode, delete_custom_patterns
from app.services.utils import global_clean_punctuations_start_stop


def transform_data(data):
    data_transformed = {}
    for i in data:
        temp_ = []
        for key in i:
            if key not in ['id', 'projectId']:
                temp_.append(i[key])
        data_transformed[str(i['projectId']) + '_' + str(i['id'])] = temp_
    
    return data_transformed


def valida_ascii_data(data):
    return ''.join([i for i in data if ord(i) < 127])


import string

from nltk.util import ngrams
from nltk.corpus import stopwords

punctuations_to_remove = [i for i in string.punctuation if i not in '!"#$%&\',-@_~']


def remove_junk(list_of_tokens):
    """removes the punctiaion not needed in auto generations"""
    temp = [token for token in list_of_tokens if check_input_text(token)]
    temp.sort()
    return temp


def punctuation_removal(input_text):
    return not any(x in input_text for x in punctuations_to_remove)


def length_check(input_text):
    return len(input_text.strip()) > 3


def stop_word_removal(input_text):
    return input_text.lower().strip() not in stopwords.words('english')


def numeric_removal(input_text):
    return not input_text.strip().isnumeric()


def calculate_time(func):
    def inner1(*args, **kwargs):
        begin = time.time()
        func(*args, **kwargs)
        end = time.time()
        print("Total time taken in : ", func.__name__, end - begin)

    return inner1


def check_input_text(input_text):
    # return stop_word_removal(input_text) and length_check(input_text) and numeric_removal(input_text)
    return numeric_removal(input_text)
    # punctuation_removal(input_text) and 


def sentence_splitter(data):
    new_data = {}
    for keys in data:
        temp = []
        data_transformed = []
        for some_data in data[keys]:
            split_data = str(some_data).splitlines()
            split_data = [i for i in split_data if (i != ' ') or (i != '')]
            data_transformed.extend(split_data)

        # split_data = data[keys][0].splitlines()
        # split_data = [i for i in split_data if i!=' ']
        spacy_generator = EnglishSentenceModelService.model().pipe(data_transformed)
        # spacy_generator=SpacyService.model().pipe(data[keys],disable=["tok2vec", "tagger", "attribute_ruler", "lemmatizer","ner"])
        # for i in spacy_generator:
        #     temp.extend(se.text for se in list(i.sents))
        temp.extend([sentences.text for i in spacy_generator for sentences in i.sents ])

        new_data[keys] = temp
    del temp
    del data_transformed
    return new_data


def remove_not_allwed_punctuations_pattern(x):
    return re.sub(not_allwed_punctuations_pattern, ' ', x).strip()


# d['pages']

def document_preprocessing(document_list:list,ExcludeAlphaNumericSuggestion=False):
    all_content = [i for i in document_list if i != '']

    html_unique_tokens = ['&gt', '&lt']  # "workfiles=&gt;&gt"

    s1 = list(map(str.lower, all_content))
    s1 = list(map(convert_unidecode, s1))
    s1 = list(map(str.strip, s1))
    all_s1 = " ~ ".join(s1)
    s1 = convert_unidecode(BeautifulSoup(all_s1, "lxml").text)
#     print(s1)
    s1 = delete_custom_patterns(s1, hyphen_newline)
    s1 = delete_custom_patterns(s1, word_hyphen_word_regex)
    s1 = delete_custom_patterns(s1, http_url_regex)

    s1 = delete_custom_patterns(s1, www_url_regex)
    s1 = delete_custom_patterns(s1, email_id_pattern)
    s1 = delete_custom_patterns(s1, page_regex)
    s1 = delete_custom_patterns(s1, appostophe_s_wordboundary)
    s1 = delete_custom_patterns(s1, appostophe_removal)
    s1 = delete_custom_patterns(s1, paranthesis_enclosed_tokens)
    s1 = delete_custom_patterns(s1, square_paranthesis_enclosed_tokens)
    s1 = delete_custom_patterns(s1, curely_paranthesis_enclosed_tokens)
    s1 = delete_custom_patterns(s1, decimal_numbers)
    s1 = delete_custom_patterns(s1, date1)
    s1 = delete_custom_patterns(s1, date2)
    s1 = delete_custom_patterns(s1, date3)
    s1 = delete_custom_patterns(s1, date4)
    s1 = delete_custom_patterns(s1, decimal1)
    s1 = delete_custom_patterns(s1, decimal2)
    s1 = delete_custom_patterns(s1, decimal3)
    s1 = delete_custom_patterns(s1, decimal4)
    s1 = delete_custom_patterns(s1, decimal5)
    s1 = delete_custom_patterns(s1, decimal6)
    s1 = delete_custom_patterns(s1, decimal7)
    s1 = delete_custom_patterns(s1, decimal8)
    # s1 = delete_custom_patterns(s1, decimal9)
    # s1 = delete_custom_patterns(s1, decimal10)
    s1 = delete_custom_patterns(s1, complete_number)
    s1 = delete_custom_patterns(s1, date4)
    s1 = delete_custom_patterns(s1, special_symbols)
    s1 = delete_custom_patterns(s1, hyphenated_spaces)

    s1 = delete_custom_patterns(s1, not_allwed_punctuations_pattern)

    if ExcludeAlphaNumericSuggestion:
        s1 = delete_custom_patterns(s1, pure_alphanumeric_regex)
    s1 = delete_custom_patterns(s1, double_hyphens)
    s1 = delete_custom_patterns(s1, multiple_spaces)

    s1 = re.split(document_splitter_regex, s1)
    s1 = [i.strip() for i in s1 if i.strip() != '']
    return s1

def auto_suggestion_generation(data, max_shingle_length=auto_completion_max_shingle_length,
                               ExcludeAlphaNumericSuggestion=False):
    suggestions_ = {}
    count = 0
    for i in data:
        tic = time.time()
        count += 1
        print(f'processing for key {count} : {i}', end=': ')
        s1 = document_preprocessing(data[i],ExcludeAlphaNumericSuggestion)
        # all_content = [j for j in data[i] if j != '']

        # html_unique_tokens = ['&gt', '&lt']  # "workfiles=&gt;&gt"

        # s1 = list(map(str.lower, all_content))
        # s1 = list(map(convert_unidecode, s1))
        # s1 = list(map(str.strip, s1))
        # all_s1 = " ~ ".join(s1)
        # s1 = convert_unidecode(BeautifulSoup(all_s1, "lxml").text)

        # s1 = delete_custom_patterns(s1, hyphen_newline)
        # s1 = delete_custom_patterns(s1, word_hyphen_word_regex)
        # s1 = delete_custom_patterns(s1, http_url_regex)

        # s1 = delete_custom_patterns(s1, www_url_regex)
        # s1 = delete_custom_patterns(s1, email_id_pattern)
        # s1 = delete_custom_patterns(s1, page_regex)
        # s1 = delete_custom_patterns(s1, appostophe_s_wordboundary)
        # s1 = delete_custom_patterns(s1, paranthesis_enclosed_tokens)
        # s1 = delete_custom_patterns(s1, square_paranthesis_enclosed_tokens)
        # s1 = delete_custom_patterns(s1, curely_paranthesis_enclosed_tokens)
        # s1 = delete_custom_patterns(s1, decimal_numbers)
        # s1 = delete_custom_patterns(s1, date1)
        # s1 = delete_custom_patterns(s1, date2)
        # s1 = delete_custom_patterns(s1, date3)
        # s1 = delete_custom_patterns(s1, date4)
        # s1 = delete_custom_patterns(s1, decimal1)
        # s1 = delete_custom_patterns(s1, decimal2)
        # s1 = delete_custom_patterns(s1, decimal3)
        # s1 = delete_custom_patterns(s1, decimal4)
        # s1 = delete_custom_patterns(s1, decimal5)
        # s1 = delete_custom_patterns(s1, decimal6)
        # s1 = delete_custom_patterns(s1, decimal7)
        # s1 = delete_custom_patterns(s1, decimal8)
        # s1 = delete_custom_patterns(s1, decimal9)
        # s1 = delete_custom_patterns(s1, complete_number)
        # s1 = delete_custom_patterns(s1, date4)
        # s1 = delete_custom_patterns(s1, special_symbols)
        # s1 = delete_custom_patterns(s1, hyphenated_spaces)

        # s1 = delete_custom_patterns(s1, not_allwed_punctuations_pattern)

        # if ExcludeAlphaNumericSuggestion:
        #     s1 = delete_custom_patterns(s1, pure_alphanumeric_regex)
        # s1 = delete_custom_patterns(s1, double_hyphens)
        # s1 = delete_custom_patterns(s1, multiple_spaces)

        # s1 = re.split(document_splitter_regex, s1)
        # s1 = [i.strip() for i in s1 if i.strip() != '']
        temp = []
        uninitialized_grams = {idx - 1: [] for idx in range(auto_completion_min_shingle_length, max_shingle_length)}
        all_tokens = []
        for key in s1:
            new_tokens = ([tok.strip() for tok in key.split() if tok.strip() != ''])
            new_tokens = list(map(global_clean_punctuations_start_stop, new_tokens))
            new_tokens = [i.strip() for i in new_tokens if i.strip() != '']

            new_tokens = list(map(lambda x: re.sub(number_identification, ' ', x).strip(), new_tokens))
            new_tokens = [i.strip() for i in new_tokens if i.strip() != '']

            # try:
            #     index_val = new_tokens.index("trans formation")
            #     with open("trans_info.text", 'a+') as f:
            #         f.write(f"trans found in {i}")
            # except Exception as e:
            #     pass

            # new_tokens = list(map(remove_not_allwed_punctuations_pattern,new_tokens))

            # all_tokens = [i for i in all_tokens if len(i)>1]
            new_tokens = [tok.strip('❛❛').strip() for tok in new_tokens]
            all_tokens.extend([i for i in new_tokens if len(i) > 1])
        grams = {idx - 1: list(ngrams(all_tokens, idx)) for idx in
                    range(auto_completion_min_shingle_length, max_shingle_length)}

        del all_tokens
        # clean_grams = [' '.join(i).strip() for j in grams for i in j if i]
        [uninitialized_grams[j].append(' '.join(i).strip()) for j in grams for i in grams[j] if i]
        print(f'time {(time.time() - tic):.2f}')
        # temp.extend(clean_grams)

        clean_grams = {j: remove_junk(list(set(uninitialized_grams[j]))) for j in uninitialized_grams}
        suggestions_[i] = clean_grams
    return suggestions_


def output_format(result, result_name='results', tic=0):
    final_ = {result_name: result, 'time': time.time() - tic}
    return final_
