import os
import re
from mongodb_connection import configurations

cwd = os.getcwd()

remove_args_flag = "remove_args_flags"
flag_section_name = "flags"
search_query_section = "search_query_flags"
data_preprocessing_flag = 'ner_data_config_flag'
query_output_processing_flag = 'query_output_processing'
strip_punctuation_flag = 'strip_punctuation_flag'
phrase_extraction_flag = 'phrase_extraction_flag'
auto_completion_flag = "auto_completion_flags"
did_you_mean_flag = "did_you_mean_flags"
#enable_entities_synonyms = False
phrases_operator = '&'
blank_operator = ' '
special_operator = ' +'
#synonym_counter = 7
#synonym_threshold = 0.75
#sense2vec_model_path = os.path.join(cwd, "models", "s2v_old")
# sense2vec_model_path = os.path.join(cwd,"models","s2v_reddit_2019_lg")
#google_word2vec = 'word2vec-google-news-50'
# glove_wiki = 'glove-wiki-gigaword-300'
#glove_wiki = 'glove-wiki-gigaword-50'

api_url_prefix = "/cognitive"
api_similarity_endpoint = "/similarity"
api_extractive_summarization_endpoint = "/extractive_summarization"
api_ner_endpoint = "/ner"
api_related_search_endpoint = "/related_search"
api_related_entity_endpoint = "/related_entities"
api_autocorrect_endpoint = "/autocorrection"
api_autosuggestion_endpoint = "/autosuggestion"
api_datadictionary_endpoint = "/data_dictionaries"

api_SynonymExpansion_query = 'query'
api_SynonymExpansion_ner_expansion = 'ner_expansion_flag'
api_SynonymExpansion_industry_domain = 'industry_domain'
api_SynonymExpansion_enableSynonymExpansion = 'enableSynonymExpansion'
api_SynonymExpansion_client_id = 'client_id'

api_autocorrectexpansion_query = 'input_query'

#relevant_query_sense2vec_flag = False
#relevant_query_gensim_flag = True

token_end_punctuation = '!"#&\'()+,-./:;<=>?@[\\]^_`{|}~'
# $%* punctuation is removed - set(string.punctuation).difference(set('!"#&\'()+,-./:;<=>?@[\\]^_`{|}~'))
token_start_punctuation = '!"#&\'()*+,-./:;<=>?@[\\]^_`{|}~'

regex_latin_characters = '[^\x00-\x7F]+'

# MongoDB - add this to json
# database_name = 'ProdSLBConfig'
# acronym_collection = 'Acronym'
# query_col = 'Key'
# target_col = 'Options'
# filter_col = 'Category'
# mongodb_configuration_path = os.path.join(cwd, 'mongodb_connection', 'mongodb', 'config', 'constants.yaml')
mongodb_acronym_collection = 'Acronym'
mongodb_acronym_collection_key = 'Key'
mongodb_acronym_collection_Options = 'Options'
mongodb_acronym_collection_Category = 'Category'

# acronym_file_path = "../../models/mongo_db_data/Acronym_data.csv"

SynonymExpansionOutput_input_request = "input_request"
SynonymExpansionOutput_expanded_acronyms = "expanded_acronyms"
SynonymExpansionOutput_synonym_expansion = "synonym_expansion"
SynonymExpansionOutput_synonym_only_list = "synonym_only_list"
SynonymExpansionOutput_entities = "entities"
SynonymExpansionOutput_filter = "filter"
SynonymExpansionOutput_whitespace_tokens = "whitespace_tokens"
SynonymExpansionOutput_tokens = "tokens"
SynonymExpansionOutput_search_query_to_be_updated = "search_query_to_be_updated"
SynonymExpansionOutput_time = "time"
SynonymExpansionOutput_truecase_input = "truecase_input"

tokenanalysis_basic_split = "basic_split"
tokenanalysis_spacy_split = "spacy_split"
tokenanalysis_input_expansion_list = "input_expansion_list"
tokenanalysis_raw_data = "raw_data"
tokenanalysis_extracted_phrases = "extracted_phrases"
tokenanalysis_search_query_entities = "search_query_entities"
tokenanalysis_search_query_remaining_tokens = "search_query_remaining_tokens"

# s2v_model = Sense2Vec().from_disk(sense2vec_model_path)

min_edit_distance_letters = 'abcdefghijklmnopqrstuvwxyz'
#file_path = 'D:/wiki_training/wiki.en'
#autocorrect_probabilities_file_path = 'app/services/auto_correction_engine/vocab_probabilities.pickle'
#autocorrect_vocab_file_path = 'app/services/auto_correction_engine/vocab.pickle'
#autocorrect_vocab_soundex_file_path = 'app/services/auto_correction_engine/vocabulary_soundex_codes.pickle'
#autocorrect_vocab_count_file_path = 'app/services/auto_correction_engine/word_count_dict.pickle'
auto_correction_flag = 'auto_correction_flags'

auto_correction_soundex = 'soundex'
auto_correction_levenshtein = 'levenshtein'
# levenshtein_edit_threshold = 2
# prefix_edit_distance = 3
auto_correction_none_output = {None: []}

auto_completion_flag = "auto_completion_flags"
auto_completion_phraser_flag = "auto_completion_phraser_flags"
auto_completion_min_shingle_length = 1
auto_completion_max_shingle_length = 5
ExcludeAlphaNumericSuggestionFlag = False
# page_regex = re.compile('[Pp]age \d')
# http_url_regex = re.compile(r'http\S+')
# www_url_regex = re.compile(r'www\S+')
http_url_regex = re.compile(r'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?')
www_url_regex = re.compile(r'www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?')
email_id_pattern = re.compile(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
page_regex = re.compile(r'\b[Pp]age \d+\b')
# not_allwed_punctuations_pattern = re.compile(
#     r'''[!#\$%\(\)\*\+,„\./:;<=>\?@\[\\\]\^_`´”“’‘{\|}©]''', flags=0)
not_allwed_punctuations_pattern = re.compile(
    r'''[!#\*\+„;<=>\?@\[\\\]\^_{\|}©]''', flags=0)

phone_number_pattern = re.compile(
    r"""
    (?<!\w)
    (
        (\+?\d{1,3}[\s-]?)?
        (\(?\d{2,4}\)?[\s-]?)?
        \d{3,4}
        ([\s-]?\d{3,4}){1,2}
    )
    (?!\w)
    """,
    re.VERBOSE               # Allows this verbose regex syntax for better readability
)

number_identification = re.compile(
    r'^^[\(\{\[]?-?\+?\$?\d*={0,1}\,{0,1}\.{0,1}\/{0,1}\\{0,1}\d+\$?%?[.\/,]?\s?$',
    flags=0)
paranthesis_enclosed_tokens = re.compile(
    r'\([A-Za-z0-9_\-!@#\$%\^&\*,\.\?\'\"\;\:\\\/\s\+\~]+\)', flags=0)
square_paranthesis_enclosed_tokens = re.compile(
    r'\[[A-Za-z0-9_\-!@#\$%\^&\*,\.\?\'\"\;\:\\\/\s\+\~]+\]', flags=0)
curely_paranthesis_enclosed_tokens = re.compile(
    r'\{[A-Za-z0-9_\-!@#\$%\^&\*,\.\?\'\"\;\:\\\/\s\+\~]+\}', flags=0)
# decimal_numbers = re.compile(r'\d*\.\d*e{1}\^{0,1}-?\d*\.?\d*', flags=0)
# appostophe_s_wordboundary = re.compile(r'''[‘’"”“´'" ]s\b''', flags=0)
decimal_numbers = re.compile(r'(?<!\$)\b(\d+\.\d+(?:e\^-?\d+|e-?\d+)?|\d*\.\d+e\^-?\d+)\b', re.IGNORECASE)
appostophe_s_wordboundary = re.compile(r'''[''"""`´'" ]s\b''', flags=0)
appostophe_removal = re.compile(r'''[‘’"”“´'" ]''', flags=0)
remove_quotes = re.compile(r'''[‘’"“”´']''', flags=0)
# clean_punctuations_start_stop_special_char = "‘’”“`–——–—‑—‒–—‘’”“`"
clean_punctuations_start_stop_special_char = '`‑”‘—’‒“–'
hyphen_newline = re.compile('\-\\n')
hyphen_space = re.compile(
    '\-\s+')
word_hyphen_word_regex = re.compile(
    '\s\w+\-\s\w+|\w+\‑\s\w+|\w+\—\s\w+|\w+\–\s\w+')

# bullet_pattern = re.compile(
# r"(?mi)\b(?:[0-9]+(?!\.\d)|[b-hj-zB-HJ-Z]|i{1,3}|iv|v|vi{0,3}|i?x|[I]{1,3}|[IVX])\.(?!\d)"
# )

# bullet_pattern = re.compile(
# r"(?mi)^(?:[0-9]+(?!\.\d)|[b-hj-zB-HJ-Z]|i{1,3}|iv|v|vi{0,3}|i?x|[I]{1,3}|[IVX])\.(?!\d)"
# )

bullet_pattern = re.compile(
r"(?:(?<=^)|(?<=\s))(?![A-Za-z]{3,}\s\d{1,2},\s\d{4})(?!\$\d)(?!(\([0-9a-zA-Zivxlcdm]+\)))(?!a\s)(?:[0-9]{1,2}(?!\.\d)|[a-zA-Z]|i{1,3}|iv|v|vi{0,3}|i?x|[I]{1,3}|[IVX])(?:\.)?(?=\s|$)"
)

roman_num_check = re.compile(
    r"\b(M{0,3})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})\b", re.IGNORECASE
)

date1 = re.compile(r'[0-9]{1,2}\-[0-9]{1,2}\-[0-9]{1,4}')
date2 = re.compile(r'[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{1,4}')
date4 = re.compile(r'[0-9]{1,2}\\[0-9]{1,2}\\[0-9]{1,4}')
date3 = re.compile(r'[0-9]{1,2}\|[0-9]{1,2}\|[0-9]{1,4}')
date5 = re.compile(
    r'(?:\d{1,2}\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
    re.IGNORECASE  # Make the pattern case-insensitive
)

# email_id_pattern = re.compile(r'[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+')
# decimal1 = re.compile(r'\d+\.\d+')
decimal1 = re.compile(r'(?<![\$\€\£])\b\d+\.\d+')
decimal2 = re.compile(r'\s\d+\.\s')
decimal3 = re.compile(r'\s\.\d+')
decimal4 = re.compile(r'\s\d+\,\d+')
decimal5 = re.compile(r'\s\d+\,\s')
decimal6 = re.compile(r'\s\,\d+')
decimal7 = re.compile(r'\s\d+\-\d+')
decimal8 = re.compile(r'\s\d+\'\d+')
decimal9 = re.compile(r'\s\d+\-\w+')
complete_number = re.compile(r'\s\d+\s')
complete_number_boundary = re.compile(r"\b\d+\s|\s\d+\b|\b\d+\b")

# special_symbols = re.compile(r'[â€¢ºÂÃ‘’¼”˜ª€â°“™œ©£§¹¦ž\x9d]+')
# special_symbols = re.compile(
#     r'[•ﬁﬂ«»ʼ€¢øº…¨‘’”˜ª€°“™œ©®£§¹ı²³¼¾½¦\x9d\uf0d2\xad\x92\u200b�]')
special_symbols = re.compile(
    r"(?<![\$\d])[•ﬁﬂ«»øº…¨˜ª€°™œ©®£§¹ı²³¼¾½¦\x9d\uf0d2\xad\x92\u200b�](?![\d'])"
)
# documentation
multiple_spaces = re.compile(r'\s+')
# relatedsearch_lasttoken_patterns = re.compile(r' and$| to$')
multi_fullstops = re.compile(r'\.{2,}')
relatedsearch_lasttoken_list = ['and', 'to', 'us', 'the']
hyphenated_spaces = re.compile(r'\s[\-\–\‒\‑]+\s+')
document_splitter_regex = re.compile(r'~+|\s+•\s+|•')
double_hyphens = re.compile(r'\-{2,}')
# operator_symbols=re.compile(r'\+|\s\-|\-\s|!|(OR)|(NOT)|(AND)')
operator_symbols = re.compile(
    r'\+|\s\-|\-\s|\s\–|\s‒\|\s\‑|!|(OR)|(NOT)|(AND)')

pure_alphanumeric_regex = re.compile(r'(?!\d+\b)(?![a-zA-Z]+\b)[a-zA-Z\d]+')

data_dictionary_key = 'key'
data_dictionary_type = 'type'
data_dictionary_projectid = 'projectid'
data_dictionary_attributes = 'attributes'
data_dictionary_frequency = 'frequency'
data_dictionary_probabilities = 'probabilities'
data_dictionary_values = 'values'

api_synonym_expansion_similarity = {"ner_expansion_flag": 'ner_expansion_flag'}

# config_settings_path = os.path.join("app", "services", "configSetting.json")

ALL_ALGORITHM = 'All'

# main_database_name = configurations["mongodb_database_name"]
entity_ruler_collection_name = 'NEREntityRuler'
# Acronym_collection_name = "Acronym"
search_analytics_collections_name = 'SearchAnalytics'
# search_analytics_db_name = configurations["mongodb_database_name"]
#  "SLB_Log_Db"

search_analytics_current_period = 20
search_analytics_backlog_days = 'bimonthly'
search_analytics_topk = 2
# default_current_frequency_threshold = 5
force_runzscore = True
#trending_search_cache_seconds = 100
#excludedDomains_defaultvalue = "evalueserve.com"
excludedDomains_examplevalue = "accenture.com, ibm.com"

# widget_top_counter = 5
# relatedsearch_similarity_threshold_default_percent = 80
# relatedentity_similarity_threshold_default_percent = 80
# pasf_entities = ['Organization', 'Location']

# punctuation_splitter_for_sentence_segmentation = ['!', ':', '.', '?', ';']

#related_search_embedding_path = os.path.join('models', 'embeddings', )
#related_search_query_pickle_path = os.path.join('models', 'query_pickles')
#related_entity_pickle_path = os.path.join("entity_files", "entity_pickles")
#related_entity_embedding_path = os.path.join("entity_files", "entity_embeddings")

relatedsearch_configuration_flags = {
    "totalRecords": {
        "$gte": 1
    },
    "query": {
        "$ne": ""
    },
    "isForcedClicked": False,
    "manual": True
}

# job_config_database_name = configurations["mongodb_database_name"]  # 'SLBConfig_Cognitive'

job_config_collections_name = 'ModelConfiguration'
relatedsearch_job_critetrion_configuration = {
    "jobName": "RelatedSearch",
    "isLatest": True,
    "status": True
}
relatedentity_job_critetrion_configuration = {
    "jobName": "PeopleAlsoSearch",
    "isLatest": True,
    "status": True
}
job_projection_configuration = {
    "pickle_name": 1,
    "vector_index_name": 1,
    "pickle_location": 1,
    "vector_index_location": 1,
    "_id": 0
}

top_limit_entities = 5
# batch_size_to_process_related_entities = 1000

# Mongo Column Names
add_manual_entities_pattern_id = "pattern_Id"
add_manual_entities_client_id = "clientId"
add_manual_entities_project_id = "projectId"
add_manual_entities_pattern = "pattern"
add_manual_entities_entity = "entity"
add_manual_entities_text = "searchTerm"

NER_OUTPUT_FORMATTER = {
    "Location": ["LOC", "GPE", "Location"],
    "Organization": ["ORG", "Organization", "Organisation"]
}

NER_VALID_OUTPUT_ENTITIES = [
    "Location",
    "Person",
    "Organization",
    "Percentage",
    "Date",
    "Cardinal",
]

MAP_SPACY_ENTITIES = {
    "LOC": "Location",
    "GPE": "Location",
    "Location": "Location",
    "ORG": "Organization",
    "Organization": "Organization",
    "Organisation": "Organization"
}

entities_in_scope = list(MAP_SPACY_ENTITIES.keys())
#entities_in_scope = ["LOC", "GPE", "ORG", "Location", "Organization"]
