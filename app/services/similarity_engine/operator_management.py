import re
from collections import defaultdict

# Added & to support AT&T type vocabs
# token_split_regex = '[a-zA-Z0-9*_?$%=:;,\"&.]+[-][a-zA-Z0-9*_?$&%=:;,\".]+|[a-zA-Z0-9*_?&$%=:;,\".]+'
token_split_regex='[a-zA-Z0-9*_?$%=:;,\"\'&.]+([-][a-zA-Z0-9*_?$&%=:;,\"\'.]+)+|[a-zA-Z0-9*_?&$%=:;,\"\'.]+'
operator_split_regex = '\s+[^a-zA-Z0-9*_?&$%=:;,\"\'.]+|\s+'

recurring_negative_pattern_regex = r'(\-)+\1'
recurring_positive_pattern_regex = r'(\+)+\1'
same_word_replacement_pattern = r'\1'
paranthesis_pattern_regex = r'[(){}\[\]]'


def unifying_query_operators(input_query):
    """replaces opertor tokens for the operator symbols"""
    all_operators = {'\sAND\s+': '+', '\s&&\s*': '+', '\s\|\|\s*': '| ', "\sOR\s+": "| ", "\sNOT\s+": "+-", "\!\s*": "+-",
                     "\s\-\s*": " +-", "\+\s*": "+"}

    for i in all_operators:
        input_query = re.sub(i, all_operators[i], input_query)
    return input_query


def token_group(pattern, query):
    """returns matching tokens, along with their index number based on the pattern specified in input"""
    return [(m.group(), (m.start(0), m.end(0) - 1)) for m in re.finditer(pattern, query)]


# old='[a-zA-Z0-9*_"]+'
# old_op = '[^a-zA-Z0-9*_"]+'
def token_operator_split(query):
    """spilts the query considering operators"""
    token_operator_split_list = token_group(token_split_regex, query) + token_group(operator_split_regex, query)
    token_operator_split_list.sort(key=lambda x: x[1][0])
    return token_operator_split_list


class QueryOperationHandler:
    def __init__(self, input_query):
        input_query = input_query.strip()
        self.operator_contains_flag = False
        self.operators = None
        self.positive_tokens = []
        self.negative_tokens = []
        self.raw_query = unifying_query_operators(input_query)
        # self.raw_query_copy = self.raw_query
        self.raw_query = re.sub(recurring_negative_pattern_regex, same_word_replacement_pattern, self.raw_query)
        self.raw_query = re.sub(recurring_positive_pattern_regex, same_word_replacement_pattern, self.raw_query)
        # self.raw_query_copy = re.sub(recurring_negative_pattern_regex,
        #  same_word_replacement_pattern, self.raw_query_copy)
        # self.raw_query_copy = re.sub(recurring_positive_pattern_regex,
        #  same_word_replacement_pattern, self.raw_query_copy)
        double_quotes = '"'
        self.input_query = re.sub(paranthesis_pattern_regex, double_quotes, self.raw_query)
        self.input_query_copy = self.input_query

        # double_quotes = '"'
        double_quote_replacement_pattern = r'\"(.+?)\"'
        parentheses_replacements_pattern = r"\((.+?)\)"
        double_quote_replacements = self.pattern_substitution(double_quote_replacement_pattern)
        pranthesis_replacemnet = self.pattern_substitution(parentheses_replacements_pattern)
        # double_quotes = '"'
        # self.pattern_removal(double_quotes,double_quote_replacements)    
        token_operator_list = token_operator_split(self.input_query_copy)
        self.idx_to_token = None
        self.token_to_idx = None
        self.sort_tokens(self.input_query_copy)
        #         print(token_operator_list)
        #         self.operator_tokens = self.sorted_operator_tokens_dictionary(token_operator_list)
        
        self.synonym_expansion_tokens = self.tokens_for_synonym_expansion_fn(token_operator_list) # Does not handle duplicates well

    def __call__(self):
        return self.synonym_expansion_tokens, self.operator_contains_flag, self.operators, self.input_query

    def pattern_substitution(self, pattern):
        return [(i.group()[1:-1].replace(' ', '_'), i.start(), i.end()) for i in re.finditer(pattern, self.input_query)]

    def pattern_removal(self, pattern, replaced_tokens):
        for i, j, k in replaced_tokens:
            self.input_query_copy = self.input_query_copy[:j + 1] + i + self.input_query_copy[k - 1:]
        self.input_query_copy = self.input_query_copy.replace(pattern, '')

    def sort_tokens(self, query):
        self.idx_to_token = {i: j[0] for i, j in reversed(list(enumerate(token_group(token_split_regex, query))))}
        self.token_to_idx = {i[1]: i[0] for i in self.idx_to_token.items()}

    def operator_tokens_dictionary(self, token_operator_list):
        # old_del = '^[a-zA-Z0-9_*\"]*$'
        operator = [' ']
        words = []
        for i in [i[0] for i in token_operator_list]:
            try:
                words.append(re.match(token_split_regex, i).group())
            except Exception as e:
                operator.append(i)
        if len(list(set(operator))) > 1:
            self.operator_contains_flag = True
            self.operators = list(set(operator))
        operator_dict = defaultdict(list)
        for i in range(len(operator[::-1])):
            if words[-i] not in operator_dict[operator[-i]]:
                operator_dict[operator[-i]].append(words[-i])

        return operator_dict

    def sorted_operator_tokens_dictionary(self, token_operator_list):
        operator_dict = self.operator_tokens_dictionary(token_operator_list)
        if operator_dict.get(' '):
            indexed_list = [self.token_to_idx[i] for i in operator_dict.get(' ')]
            indexed_list.sort()
            operator_dict[' '] = [self.idx_to_token[i] for i in indexed_list]
        return operator_dict

    def remove_negative_operator(self, token_operator_list):
        """this nested list of tokens to be used for synonym expansion API"""

        self.operator_dict = self.sorted_operator_tokens_dictionary(token_operator_list)
        for key in self.operator_dict.keys():
            if key.find('-') == -1:
                self.positive_tokens.append(self.operator_dict[key])
            else:
                self.negative_tokens.append(self.operator_dict[key])
        return self.positive_tokens  # return [operator_dict[key] for key in operator_dict if key.find('-')==-1]

    def tokens_for_synonym_expansion_fn(self, token_operator_list):
        result = []
        list_of_tokens_for_synonym_expansion = self.remove_negative_operator(token_operator_list)
        for list_of_tokens in list_of_tokens_for_synonym_expansion:
            for tokens in list_of_tokens:
                if tokens.find('_') > 0:
                    result.append('"' + tokens.replace("_", " ") + '"')
                else:
                    result.append(tokens)
        return ' '.join(result)

# print(QueryOperationHandler('I am going to AND America + USA? Are you going to -India ! Japan && facebook AND Union OR '
#                             'Pakistan "Farishte". What is this man? " raskhit sakhuja " ').raw_query)
