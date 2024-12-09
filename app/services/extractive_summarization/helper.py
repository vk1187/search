import re
import time

from bs4 import BeautifulSoup

from app.services.config_constants import appostophe_s_wordboundary,hyphen_space, number_identification, paranthesis_enclosed_tokens
# from utils import DataPreprocessor
from app.services.config_constants import auto_completion_min_shingle_length, auto_completion_max_shingle_length, page_regex
from app.services.config_constants import decimal1, decimal2, complete_number,complete_number_boundary, decimal3, decimal4, decimal5, decimal6, decimal7 ,\
    special_symbols, multiple_spaces,decimal8,decimal9
from app.services.config_constants import decimal_numbers, date5, date4, date3, date2, date1, hyphen_newline
from app.services.config_constants import double_hyphens, word_hyphen_word_regex, pure_alphanumeric_regex
from app.services.config_constants import email_id_pattern, document_splitter_regex, hyphenated_spaces, bullet_pattern, multi_fullstops, roman_num_check
from app.services.config_constants import http_url_regex, www_url_regex, not_allwed_punctuations_pattern, phone_number_pattern
from app.services.config_constants import square_paranthesis_enclosed_tokens, curely_paranthesis_enclosed_tokens
from app.services.model_engine.engelish_sentence_model import EnglishSentenceModelService
from app.services.utils import convert_unidecode, delete_custom_patterns,delete_custom_patterns_nospace, delete_custom_patterns_fullstop




def sentence_tokenizer(data):
    # new_data = {}
#     for keys in data:.
    
    data_transformed = []
    temp = []

    for some_data in data:

        
        split_data = some_data.encode("ascii", "ignore").decode('utf8').strip().splitlines()
        split_data = [i for i in split_data if (i != ' ') or (i != '')]
        data_transformed.extend(split_data)
    spacy_generator = EnglishSentenceModelService.model().pipe(data_transformed)
    temp.extend([sentences.text for i in spacy_generator for sentences in i.sents ])
    
    return temp 

def document_preprocessing(document_list:list,ExcludeAlphaNumericSuggestion=False,words_per_sentence_threshold=0):
    all_content = [i for i in document_list]

    # html_unique_tokens = ['&gt', '&lt']  # "workfiles=&gt;&gt"

    s1 = list(map(str.lower, all_content))
    s1 = list(map(convert_unidecode, s1))
    s1 = list(map(str.strip, s1))
    all_s1 = " ~ ".join(s1)
    s1 = convert_unidecode(BeautifulSoup(all_s1, "lxml").text)
#     print(s1)
    s1 = delete_custom_patterns(s1, hyphen_newline,replace_pattern='-')
    s1 = delete_custom_patterns(s1, hyphen_space,replace_pattern='-')
    s1 = delete_custom_patterns(s1, word_hyphen_word_regex)
    s1 = delete_custom_patterns(s1, http_url_regex)

    s1 = delete_custom_patterns(s1, www_url_regex)
    s1 = delete_custom_patterns(s1, email_id_pattern)
    s1 = delete_custom_patterns(s1, page_regex)
    # s1 = delete_custom_patterns(s1, appostophe_s_wordboundary)
    # s1 = delete_custom_patterns(s1, paranthesis_enclosed_tokens)
    # s1 = delete_custom_patterns(s1, square_paranthesis_enclosed_tokens)
    # s1 = delete_custom_patterns(s1, curely_paranthesis_enclosed_tokens)
    s1 = delete_custom_patterns_nospace(s1, phone_number_pattern)
    s1 = delete_custom_patterns(s1, decimal_numbers)
    # s1 = delete_custom_patterns(s1, date1)
    # s1 = delete_custom_patterns(s1, date2)
    # s1 = delete_custom_patterns(s1, date3)
    # s1 = delete_custom_patterns(s1, date4)
    # s1 = delete_custom_patterns(s1, date5)
    s1 = delete_custom_patterns(s1, decimal1)
    s1 = delete_custom_patterns(s1, decimal2)
    s1 = delete_custom_patterns(s1, decimal3)
    s1 = delete_custom_patterns(s1, decimal4)
    # s1 = delete_custom_patterns(s1, decimal5)
    s1 = delete_custom_patterns(s1, decimal6)
    s1 = delete_custom_patterns(s1, decimal7)
    s1 = delete_custom_patterns(s1, decimal8)
    s1 = delete_custom_patterns(s1, decimal9)
    # s1 = delete_custom_patterns(s1, decimal10)
    # s1 = delete_custom_patterns(s1, complete_number)
    # s1 = delete_custom_patterns(s1, complete_number_boundary)
    # s1 = delete_custom_patterns(s1, date4)
    s1 = delete_custom_patterns(s1, special_symbols)
    s1 = delete_custom_patterns(s1, hyphenated_spaces)
    s1 = delete_custom_patterns_nospace(s1, bullet_pattern)
    s1 = delete_custom_patterns_nospace(s1, roman_num_check)

    s1 = delete_custom_patterns(s1, not_allwed_punctuations_pattern)

    if ExcludeAlphaNumericSuggestion:
        s1 = delete_custom_patterns(s1, pure_alphanumeric_regex)
    s1 = delete_custom_patterns(s1, double_hyphens)
    s1 = delete_custom_patterns(s1, multiple_spaces)
    s1 = delete_custom_patterns_fullstop(s1, multi_fullstops)

    s1 = re.split(document_splitter_regex, s1)
    # s1 = [i.strip().replace('"',"") for i in s1 if i.strip() != '']
    s1 = [i.strip() for i in s1 if i.strip() != '']
    s1 = [i for i in s1 if len(i.split())>words_per_sentence_threshold]
    s1 = [sentence[1:].strip() if sentence.strip().startswith("-") else sentence for sentence in s1]
    s1 = [sentence[:-1].strip() if sentence.strip().endswith("-") else sentence for sentence in s1]

    return s1