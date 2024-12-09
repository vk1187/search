from app.services.config_constants import *


class SynonymExpansionOutput:
    def __init__(self, input_request=None, expanded_acronyms=None, synonym_expansion=None, entities=None,
                 filter_entities=None, search_query_tokens=None, time=None):
        if input_request is None:
            self.input_request = ''
        elif len(input_request) >= 1 and input_request[-1] == '+':
            self.input_request = input_request[:-1]
        else:
            self.input_request = input_request

        # self.input_request = '' if input_request is None else input_request
        # if self.input_request != '' and self.input_request[-1] == '+':
        #     self.input_request = self.input_request[:-1]
        self.expanded_acronyms = '' if expanded_acronyms is None else expanded_acronyms
        self.synonym_expansion = '' if synonym_expansion is None else synonym_expansion
        self.entities = '' if entities is None else entities
        self.filter = {"Location": [], "Person": [], "Organization": [], "Percentage": [], "Date": [],
            "Cardinal": []} if filter_entities is None else filter_entities
        self.time = time

        self.whitespace_tokens = search_query_tokens[0]
        self.tokens = search_query_tokens[1]
        self.synonym_only_list = search_query_tokens[2]
        self.search_query_to_be_updated = search_query_tokens[3]
        self.truecase_input = search_query_tokens[4]

    def return_output(self):
        """output format"""
        return {SynonymExpansionOutput_truecase_input: self.truecase_input,
                SynonymExpansionOutput_input_request: self.input_request,
                SynonymExpansionOutput_expanded_acronyms: self.expanded_acronyms,
                SynonymExpansionOutput_synonym_expansion: self.synonym_expansion,
                SynonymExpansionOutput_synonym_only_list: self.synonym_only_list,
                SynonymExpansionOutput_entities: self.entities, SynonymExpansionOutput_filter: self.filter,
                SynonymExpansionOutput_whitespace_tokens: self.whitespace_tokens,
                SynonymExpansionOutput_tokens: self.tokens,
                SynonymExpansionOutput_search_query_to_be_updated: self.search_query_to_be_updated,
                SynonymExpansionOutput_time: self.time}

# print(SynonymExpansionOutput(1, 2, 3, 4,None,).return_output())
