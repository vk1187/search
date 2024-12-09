import itertools
import re
import time
import copy
from collections import defaultdict

import truecase

from app.services.config_constants import SynonymExpansionOutput_entities
# import gensim_models
from app.services.config_constants import blank_operator, special_operator
from app.services.config_constants import phrase_extraction_flag
from app.services.config_constants import remove_args_flag
from app.services.config_constants import search_query_section
from app.services.config_constants import strip_punctuation_flag
from app.services.config_constants import entities_in_scope
from app.services.embedding_models import GensimLoader
# from ..ner_engine.ml_model.spacy.spacy_service import SpacyService
from app.services.ner_engine.ml_model.spacy import SpacyService
from app.services.similarity_engine import ExpansionHelper
# from app.services.similarity_engine import Sense2VecEmbeddings
from app.services.similarity_engine import SynonymExpansionOutput
from app.services.similarity_engine import TokenAnalysis
from app.services.similarity_engine import acronym_expansion
from app.services.similarity_engine.operator_management import QueryOperationHandler
from app.services.utils import DataPreprocessor
from app.services.utils import flatten
from custom_logging import logger

from load_parameters import get_parameters

# from utils import _lowercase
gensim_models = GensimLoader()

# s2v = Sense2VecEmbeddings()
# s2v = Sense2vec_Loader.getInstance()
s2v = None
import json


def post_processing(embedding_similarity_list, label=None, text=None):
    """

    :param embedding_similarity_list: list of tokens for which similar entities has to be found
    :param label: criteria on the basis of similar entities has to be found, if none
    then genric similarity has to be calculated
    :param text: check for original strings to be not found in similarity results
    :return: list of similar elements
    """
    unique_embedding_similarity_list = []
    if label is not None:
        embedding_similarity_list = s2v.resultant_entity(
            embedding_similarity_list, label)
    else:
        embedding_similarity_list = s2v.resultant_entity(
            embedding_similarity_list)
    logger.debug(f'post processing-----{embedding_similarity_list}')
    unique_embedding_similarity_list = ExpansionHelper.case_insensitive_unique_list(
        embedding_similarity_list)
    if text is not None:
        for text_iter in [text, text.replace(' ', '_')]:
            unique_embedding_similarity_list = s2v.check_original_search_string(
                unique_embedding_similarity_list, text_iter)
    return unique_embedding_similarity_list


def query_representation(tokens):
    """

    :param list of tokens or string which needs to be enclosed in brackets:
    :return: bracket enclosed string
    """
    if isinstance(tokens, list):
        # blank_operator
        action = special_operator.join('"' + item + '"' for item in tokens)
    elif isinstance(tokens, str):
        action = tokens

    action = '(' + action + ')'
    return action


class QueryHandler:

    def __init__(self,
                 search_query: str,
                 ner_expansion_flag: bool = True,
                 industry_domain: str = 'All',
                 enable_synonym_expansion: bool = True,
                 client_id: int = None):
        self.enable_synonym_expansion = enable_synonym_expansion
        self.industry_domain = industry_domain
        self.original_input_query = search_query
        self.parameters = get_parameters()
        # _, self.custom_entities = SpacyService.extract_entities(
        #     search_query
        #     # original=True
        # )

        # all_entities = flatten(self.custom_entities['entities'])
        self.query_operator_obj = QueryOperationHandler(search_query)
        updated_search_query, operator_flag, query_operators, self.updated_operator_original_query = self.query_operator_obj()
        self.search_query =  self.updated_operator_original_query.replace("+","").replace(" -"," ").replace("- "," ").replace("  "," ")
        #earlier it was self.search_query = updated_search_query, but causing lot of bugs
        logger.debug(f'Input Search query {self.search_query}')
        self.query_tokens = self.search_query.split()
        # self.doc = SpacyService.model_doc(self.search_query)
        self.doc, self.custom_entities = SpacyService.extract_entities(
            text=truecase.get_true_case("," + self.search_query)
            if "&" not in self.search_query else self.search_query,
            # Made this change to support & in true_case
            client_id=client_id,
            apply_rules_flag=True,
            # truecase.get_true_case(","+self.search_query)
            # original=True
        )
        self.truecase_input = self.doc.text
        self.doc = self.doc[1:] if "&" not in self.search_query else self.doc
        self.model_name = 'glove'
        # self.model_name='word2vec'
        self.ner_expansion_flag = ner_expansion_flag
        self.entity_token_syns = defaultdict(list)
        self.copy_q = self.doc.text
        self.double_quote_flag = False
        self.synonymization_flag, self.synonymization_flag_value = self.check_synonyms(
        )

        # self.ner_tag_values = list(flatten(self.ner_tags.values()))
        self.syn_exp = []
        # self.search_query_token_expansion = {}
        self.acronym_present = [token.text for token in self.doc if acronym_expansion(token.text, self.industry_domain)]
            
        self.init_original_entities = copy.deepcopy(self.custom_entities)
        self.init_entities = self.entities_query()
        self.init_tokens = self.non_entity_query()
        z = re.match("(?i)\d+g", self.doc.text)
        if z:
            self.whitespace_text_tokens = [
                i + " " for i in self.doc.text.split()
            ]
            self.text_tokens = [i for i in self.doc.text.split()]
        else:

            self.whitespace_text_tokens = [
                i.text + i.whitespace_ for i in self.doc
            ]
            self.text_tokens = [i.text for i in self.doc]

    def no_syn(self):
        return self.doc.like_num or self.doc.like_email or self.doc.is_currency or self.doc.is_stop

    def double_quote_phrase_extraction(self):
        """
        :return: Phrases enclosed within double quotes
        """
        try:
            extracted_phrases = DataPreprocessor(self.search_query,
                                                 phrase_extraction_flag)()
            if extracted_phrases != ['']:
                self.double_quote_flag = True
        except Exception as e:
            logger.error(f'{e}')
            logger.exception(e)
            extracted_phrases = ['']
        return extracted_phrases

    def entityless_raw_data(self, plane_query):
        """
        :param plane_query: input query ->str
        :return: String without entity tokens/double quote enclosed phrases/punctuations->str
        """
        try:
            # input_expansion_list = ExpansionHelper.case_insensitive_unique_list(
            #     self.query_tokens + [i.text for i in self.doc])
            raw_data = DataPreprocessor(plane_query, strip_punctuation_flag)()
            logger.info(
                f'{self.entityless_raw_data.__qualname__}.raw data --> {raw_data}'
            )
        except Exception as e:
            logger.error(f'{e}')
            logger.exception(e)
            raw_data = ''
        return raw_data

    def token_analysis(self):
        """

        :return: return various ways input query to be tokenized
        """

        ta_obj = TokenAnalysis(search_query=self.search_query,
                               query_tokens=self.query_tokens,
                               doc=self.doc,
                               init_entities=self.init_entities,
                               init_tokens=self.init_tokens)

        return ta_obj.tokens()

    def acronym_addition(self, list_name):
        """

        :param list_name: input the acronym/tokens to be expanded from mongodb_collection and add them to the same list
        :return:
        """
        logger.debug(f'In function {self.acronym_addition.__qualname__}')
        logger.debug(
            f'tokens for which acronym need to be found - {list_name}')
        acronym_names, acronym_dict = self.acronym_expansion_help(list_name)
        logger.debug(f'Acronyms - {acronym_names}')
        if acronym_names:
            list_name.extend(acronym_names)
        return list_name, acronym_dict

    def location_org_entity_values(self):
        """

        :return: returns organisation expanded acronyms, location expanded acronyms and combined organisation and location entities
        """
        logger.debug(
            f'In function {self.location_org_entity_values.__qualname__}')
        orgs = self.custom_entities['entities']['Organization']
        if len(orgs) > 0:
            orgs_acr, acronyms_dict = self.acronym_addition(orgs)
        else:
            orgs_acr = []
        logger.debug(
            f'{self.location_org_entity_values.__qualname__}.Organisation Names --> {orgs_acr} '
        )
        locs = self.custom_entities['entities']['Location']

        if len(locs) > 0:
            locs_acr, acronyms_dict = self.acronym_addition(locs)
        else:
            locs_acr = []

        logger.debug(
            f'{self.location_org_entity_values.__qualname__}.Location Names --> {locs_acr} '
        )
        # org_locs = orgs + locs
        logger.debug(
            f'{self.location_org_entity_values.__qualname__}.orgs + locs --> {orgs + locs}'
        )
        if len(orgs) >= 1 and len(locs) >= 1:
            org_locs = ' '.join('"' + item + '"' for item in orgs + locs)
        elif len(locs) >= 1:
            org_locs = ' '.join('"' + item + '"' for item in locs)
        elif len(orgs) >= 1:
            org_locs = ' '.join('"' + item + '"' for item in orgs)
        else:
            org_locs = ''
        logger.debug(
            f'{self.location_org_entity_values.__qualname__}.orgs + locs --> {org_locs}'
        )
        return orgs_acr, locs_acr, org_locs

    def query_intent(self):
        """

        :return: returns all the entities combined with '+' along with non entity tokens
        """
        logger.debug(f'In function {self.query_intent.__qualname__}')
        # intent = '|'
        tokens = []
        result_intent = ''
        # if isinstance(self.init_entities, str):
        if self.double_quote_flag:
            user_phrases = self.init_entities
            user_phrases = ' '.join('"' + item + '"' for item in user_phrases)
            result_intent += query_representation(user_phrases)
            result_intent += '+'
        else:
            orgs, locs, org_locs = self.location_org_entity_values()
            logger.debug(
                f'{self.query_intent.__qualname__} org: {orgs} locs: {locs} org+locs : {org_locs} '
            )
            if len(orgs) >= 1:
                orgs_repr = query_representation(orgs)
                result_intent += orgs_repr
                result_intent += '+'
            if len(locs) >= 1:
                locs_repr = query_representation(locs)
                logger.debug(locs_repr)
                result_intent += locs_repr
                result_intent += '+'
            other_entities = [
                i for i in self.init_entities if not (i in orgs or i in locs)
            ]
            logger.debug(
                f'{self.query_intent.__qualname__}.other_entities --> {other_entities}'
            )
            if isinstance(other_entities, list):
                tokens.extend(other_entities)
            else:
                tokens.append(other_entities)

        other_tokens = self.remove_verb_non_entity_query()
        logger.debug(
            f'{self.query_intent.__qualname__}.other_tokens after removing verbs -->  {other_tokens}'
        )
        if isinstance(other_tokens, list):
            tokens.extend(other_tokens)
        else:
            tokens.append(other_tokens)
        tokens = ExpansionHelper.case_insensitive_unique_list(tokens)
        tokens, acronyms_dict = self.acronym_addition(tokens)
        logger.debug(f'{self.query_intent.__qualname__}.tokens --> {tokens}')
        if len(acronyms_dict) >= 1:
            tokens = [i for i in tokens if i not in acronyms_dict.keys()]
            tokens = [
                i for i in tokens for j in acronyms_dict.values() if i not in j
            ]
            # Acronym Representation

            try:

                acr_repr = ''
                acr_list = []
                for i in list(acronyms_dict.items()):
                    temp = i[1]
                    temp.append(i[0])
                    acr_list.append(temp)
                for i in acr_list:
                    x = ('("' + '" "'.join(i) + '")+')
                    acr_repr += x
            except Exception as e:
                logger.error(e)
                logger.exception(e)

        # acr_repr[:-1]

        year_regex = re.compile("(19|20)[0-9]{2}")
        if len(tokens) >= 1:
            dates = [k.group() for i in tokens for k in year_regex.finditer(i)]
            if len(dates) > 0:
                result_intent += query_representation(dates).replace(
                    '" "', '" +"')
                result_intent += '+'
                try:
                    [tokens.remove(str(i)) for i in dates]
                except Exception as exc:
                    pass
                    logger.error(exc)
            if len(acronyms_dict) >= 1:
                result_intent += acr_repr[:-1]
                result_intent += '+'
            if len(tokens) >= 1:
                token_repr = query_representation(tokens)
                result_intent += token_repr

        # if isinstance(self.init_entities, str):
        if self.double_quote_flag:
            entity_intent = user_phrases

        else:
            entity_intent = org_locs
        return result_intent, entity_intent

    def pos_tags(self):
        """

        :return: returns verbs(pos_tag) peresent in search query
        """
        logger.debug(f'In function {self.pos_tags.__qualname__}')
        pos_text = []
        for i in self.doc:
            # Added logic to exclude acronyms from Verb inclusion
            if i.pos_ in ['VERB'] and i.text not in self.acronym_present:
                pos_text.append(i.text)
        return pos_text

    def entities_query(self):
        """

        :return: return entity using spacy model or tokens mentioned in double quote
        """
        logger.debug(f'In function {self.entities_query.__qualname__}')
        user_phrases = self.double_quote_phrase_extraction()
        logger.debug(
            f'{self.entities_query.__qualname__}.user_phrases --> {user_phrases}'
        )
        if user_phrases != ['']:
            entity_values = user_phrases
        else:
            for i in self.custom_entities['entities']: 
                for j in self.custom_entities['entities'][i]:
                    if j in self.acronym_present:
                        self.custom_entities['entities'][i].remove(j)

            entity_values = list(
                flatten(list(self.custom_entities['entities'].values())))
            # logger.debug(f'Entities from query from .ent attribute --> {self.doc.ents}')
            entity_values=[i for i in  entity_values if i not in self.acronym_present]

        logger.debug(
            f'1. {self.entities_query.__qualname__}.Entities from query - {entity_values}'
        )
        return entity_values

    def non_entity_query(self, clean_query=True):
        """

        :param clean_query: flag to enable removing the stop words
        :return: returns tokens which does not contain any entity or double quoted phrases
        """

        logger.debug(f'In function {self.non_entity_query.__qualname__}')
        # parameters = get_parameters()
        # entities_in_scope = json.loads(self.parameters.get("ner", "entities_in_scope"))
        # ent_val = self.init_entities
        # plane_query = self.search_query

        # if isinstance(ent_val, list):
        # plane_query = re.sub('\s+', ' ',
        #                      re.sub('|'.join([i + '\\b' for i in self.init_entities]), '', self.search_query))
        # This does not work because in case of repeating words below code is replace words from other entity as well
        # plane_query = re.sub('\s+', ' ',
        #                      re.sub('|'.join([i + '\\b' for i in self.init_entities]), '', self.search_query))
        plane_query = ''.join([
            i.text + i.whitespace_ for i in self.doc
            if i.ent_type_ not in entities_in_scope
        ])

        logger.debug(
            f'2. {self.non_entity_query.__qualname__}.plane_query --> {str(plane_query)} '
        )
        plane_query = blank_operator.join(
            ExpansionHelper.case_insensitive_unique_list(plane_query.split()))
        # elif isinstance(ent_val, str):
        plane_query = self.entityless_raw_data(plane_query)

        logger.debug(
            f'{self.non_entity_query.__qualname__}.plane_query variable --> {str(plane_query)}'
        )

        if clean_query:
            # logger.debug(f'plane_query {str(plane_query)} ,- verbs list{str(verbs)}')
            plane_query = DataPreprocessor(plane_query,
                                           search_query_section)().split()
        logger.debug(
            f'3. {self.non_entity_query.__qualname__}.EntityLess query - {str(plane_query)} '
        )
        # if boost:
        #     return ent_val, plane_query
        
        for i in  self.acronym_present:
            if i not in plane_query:
                plane_query.append(i)


        return plane_query

    def remove_verb_non_entity_query(self):
        """

        :return: returns original query without any verbs
        """
        logger.debug(
            f'In function {self.remove_verb_non_entity_query.__qualname__}')

        verbs = self.pos_tags()
        
        plane_query = self.init_tokens
        if len(verbs):
            logger.debug(
                f'plane_query before removing verbs --> {plane_query}')
            plane_query = DataPreprocessor([plane_query, verbs],
                                           remove_args_flag)().split()
            logger.debug(f'plane_query after removing verbs --> {plane_query}')
        return plane_query

    # def gensim_post_processing(self, text):
    #     unique_embedding_similarity_list = []
    #     try:
    #         for text_iter in [text, text.replace(' ', '_')]:
    #             try:
    #                 standard_embedding_op = gensim_models.model_similarity(text, self.model_name)
    #             except ValueError as ve:
    #                 logger.exception(f'{text_iter} not present in {self.model_name}')
    #                 continue
    #         embedding_similarity_list = [i[0] for i in standard_embedding_op]
    #         unique_embedding_similarity_list = ExpansionHelper.case_insensitive_unique_list(embedding_similarity_list)
    #     except Exception as e:
    #         logger.error(f'{e} -  Key not found in {self.model_name}')
    #     return unique_embedding_similarity_list

    # def entities_query_expansion(self, enforce_entity=False):
    #     # assert (len(self.entities_query()) > 0)
    #     syn_list = []
    #     for ent in self.doc.ents:
    #         syn_list.append(ent.text)
    #         if ent.label_ in ['ORG', 'GPE', 'LOC', 'NORP']:
    #             if enforce_entity:
    #                 embedding_similarity_list = s2v.top_similar_terms(ent.text, ent.label_)
    #
    #                 unique_embedding_similarity_list = post_processing(embedding_similarity_list, ent.label_)
    #             else:
    #                 embedding_similarity_list = s2v.top_similar_terms(ent.text)
    #                 unique_embedding_similarity_list = post_processing(embedding_similarity_list)
    #         if unique_embedding_similarity_list:
    #             unique_embedding_similarity_list = self.gensim_post_processing(ent.text)
    #         syn_list.extend(unique_embedding_similarity_list)
    #         self.entity_token_syns[ent.text].extend(unique_embedding_similarity_list)
    #     return syn_list

    def s2v_entities_query_expansion(self, enforce_entity=False):
        """
        :param enforce_entity: this flag enables to search for similar tokens for the same entity type
        :return: return expansion of entities suing Sense2vec
        """
        logger.debug(
            f'In function {self.s2v_entities_query_expansion.__qualname__}')
        enable_entities_synonyms = self.parameters.getboolean(
            "similarity", "enable_entities_synonyms")
        # assert (len(self.entities_query()) > 0)
        syn_list = []
        for ent in self.doc.ents:
            # if ent.label_ in ['LOC', 'GPE', 'NORP', 'PER', 'ORG']:
            if ent.label_ in entities_in_scope:
                syn_list.append(ent.text)
            # if ent.label_ in ['ORG', 'GPE', 'LOC', 'NORP'] and enable_entities_synonyms == True:
            if ent.label_ in entities_in_scope and enable_entities_synonyms == True:
                if enforce_entity:
                    embedding_similarity_list = s2v.top_similar_terms(
                        ent.text, ent.label_)

                    unique_embedding_similarity_list = post_processing(
                        embedding_similarity_list, ent.label_, ent.text)
                else:
                    embedding_similarity_list = s2v.top_similar_terms(ent.text)
                    unique_embedding_similarity_list = post_processing(
                        embedding_similarity_list, ent.text)
                logger.debug(
                    f'{self.s2v_entities_query_expansion.__qualname__}(entities + sense2vec similar tokens) --> {ent.text} - {unique_embedding_similarity_list} '
                )
                syn_list.extend(unique_embedding_similarity_list)
                self.entity_token_syns[ent.text].extend(
                    unique_embedding_similarity_list)
        return syn_list

    def gensim_entities_query_expansion(self):
        """

        :return: return expansion of entities suing Gensim models(word2vec/glove)
        """
        logger.debug(
            f'In function {self.gensim_entities_query_expansion.__qualname__}')
        enable_entities_synonyms = self.parameters.getboolean(
            "similarity", "enable_entities_synonyms")
        # assert (len(self.entities_query()) > 0)
        syn_list = []
        for ent in self.doc.ents:
            # if ent.label_ in ['LOC', 'GPE',  'ORG']: #'NORP', 'PERSON',
            if ent.label_ in entities_in_scope:
                syn_list.append(ent.text)
                # for word in ent.text.split():
                #     if word not in syn_list:
                #         syn_list.append(word)
                # syn_list.extend(ent.text.split())

            logger.debug(
                f'Finding Similarity for  {ent.text}  through {self.model_name} -->syn_list {syn_list}'
            )

            # Disabling Synonyms for entities

            if enable_entities_synonyms == True:
                # if ent.label_ in ['ORG', 'GPE', 'LOC']:
                if ent.label_ in entities_in_scope:
                    unique_embedding_similarity_list = gensim_models.post_processing(
                        ent.text, self.model_name)
                    logger.debug(
                        f'7. {self.gensim_entities_query_expansion.__qualname__} Gensim synonyms are : {unique_embedding_similarity_list}'
                    )
                    syn_list.extend(unique_embedding_similarity_list)
                    self.entity_token_syns[ent.text].extend(
                        unique_embedding_similarity_list)
            logger.debug(
                f'8. {self.gensim_entities_query_expansion.__qualname__} entity_token_syns: {self.entity_token_syns}'
            )
        return syn_list

    # def ner_relevant_query_tokens(self):
    #
    #     for ent in self.doc.ents:
    #         if ent.label_ in ['ORG', 'GPE', 'LOC', 'NORP']:
    #             embedding_similarity_list = s2v.top_similar_terms(ent.text,
    #                                                               ent.label_)
    #
    #             # self.entity_token_syns['ent.label_']
    #             if len(embedding_similarity_list) > 1:
    #                 logger.debug(f'{embedding_similarity_list} -synonym list for ner query-tokens')
    #                 possible_synonyms_list_with_entity = s2v.resultant_entity(embedding_similarity_list, ent.label_)
    #                 possible_synonyms_list_with_entity = ExpansionHelper.case_insensitive_unique_list(
    #                     possible_synonyms_list_with_entity)
    #                 possible_synonyms_list_wo_entity = s2v.resultant_entity(embedding_similarity_list)
    #                 possible_synonyms_list_wo_entity = ExpansionHelper.case_insensitive_unique_list(
    #                     possible_synonyms_list_wo_entity)
    #
    #                 logger.debug(f'{possible_synonyms_list_with_entity} -possible_synonyms_list_with_entity')
    #                 logger.debug(f'{possible_synonyms_list_wo_entity} -possible_synonyms_list_wo_entity')
    #                 possible_synonyms_list_with_entity = ExpansionHelper.sorted_entities(
    #                     possible_synonyms_list_with_entity,
    #                     ent.text.strip().replace(' ', '_'),
    #                     ent.label_)
    #
    #                 possible_synonyms_list_wo_entity = ExpansionHelper.sorted_entities(
    #                     possible_synonyms_list_wo_entity,
    #                     ent.text.strip().replace(' ', '_'),
    #                     ent.label_)
    #
    #                 # logger.debug(f'{possible_synonyms_list_with_entity} -Sorted possible_synonyms_list_with_entity')
    #                 # logger.debug(f'{possible_synonyms_list_wo_entity} -Sorted possible_synonyms_list_wo_entity')
    #                 resultant_synonyms_with_entity = s2v.check_original_search_string(
    #                     possible_synonyms_list_with_entity,
    #                     ent.text.replace(' ', '_'))
    #                 resultant_synonyms_wo_entity = s2v.check_original_search_string(possible_synonyms_list_wo_entity,
    #                                                                                 ent.text.replace(' ', '_'))
    #                 logger.debug(f'{resultant_synonyms_with_entity} -resultant_synonyms list')
    #                 logger.debug(f'{resultant_synonyms_wo_entity} -resultant_synonyms list')
    #
    #                 self.syn_exp.extend(resultant_synonyms_wo_entity)
    #                 self.entity_token_syns[ent.text].extend(resultant_synonyms_with_entity)
    #
    #         self.copy_q = self.copy_q.replace(ent.text, '').strip()
    # return self.syn_exp
    # return {"synonym_expansion": syn_exp, "time": time.time() - tic}

    # def non_ner_relevant_query_tokens(self):
    #     syn_exp = []
    #     # self.copy_q = DataPreprocessor(self.copy_q.lower(), search_query_section)().split()
    #     # logger.info(f'{search_query_section} flag from configsetting is used')
    #     # logger.info(f'{self.copy_q} - New Query')
    #     self.copy_q = self.non_entity_query()
    #     for term in self.copy_q:
    #         syn_exp.append(term)
    #         term_sense = s2v.s2v_model.get_best_sense(term)
    #         if term_sense is not None:
    #             final_lists = s2v.resultant_entity(s2v.s2v_model.most_similar(term_sense, synonym_counter))
    #             syn_exp.extend(s2v.check_original_search_string(final_lists, term))
    #         else:
    #             unique_embedding_similarity_list = self.gensim_post_processing(term)
    #             syn_exp.extend(unique_embedding_similarity_list)
    #
    #     return syn_exp

    def s2v_non_ner_relevant_query_tokens(self):
        """

        :return: return expansion of non-entity tokens using Sense2vec
        """
        synonym_counter = self.parameters.getint("similarity",
                                                 "synonym_counter")
        logger.debug(
            f'In function {self.s2v_non_ner_relevant_query_tokens.__qualname__}'
        )
        syn_exp = []
        self.copy_q = self.non_entity_query()
        verbs = self.pos_tags()
        for term in self.copy_q:
            syn_exp.append(term)
            # if term not in verbs and not self.synonymization_flag.get(term, True) and self.enable_synonym_expansion:
            try:
                synonym_run_flag = self.synonymization_flag_value[
                    self.synonymization_flag.index(term)]
            except Exception as e:
                synonym_run_flag = True
            if term not in verbs and not synonym_run_flag and self.enable_synonym_expansion:

                term_sense = s2v.s2v_model.get_best_sense(term)
                if term_sense is not None:
                    final_lists = s2v.resultant_entity(
                        s2v.s2v_model.most_similar(term_sense,
                                                   synonym_counter))
                    syn_exp.extend(
                        s2v.check_original_search_string(final_lists, term))
        return syn_exp

    def gensim_non_ner_relevant_query_tokens(self):
        """

        :return: return expansion of non-entity tokens using Sense2vec
        """
        # logger.debug(f'In function {self.gensim_non_ner_relevant_query_tokens.__qualname__}')
        syn_exp = []
        self.copy_q = self.init_tokens
        # self.non_entity_query()  ##[CEO,Nokia,going]
        # self.check_synonyms()
        logger.debug(
            f'4. {self.gensim_non_ner_relevant_query_tokens.__qualname__} - Non NER token --> {self.copy_q} '
        )
        verbs = self.pos_tags()
        if len(self.copy_q) >= 1 and isinstance(self.copy_q, list):
            for term in self.copy_q:
                syn_exp.append(term)
                try:
                    synonym_run_flag = self.synonymization_flag_value[
                        self.synonymization_flag.index(term)]
                except Exception as exc:
                    synonym_run_flag = True
                # if term not in verbs and not self.synonymization_flag.get(term, True) and self.enable_synonym_expansion:
                if term not in verbs and not synonym_run_flag and self.enable_synonym_expansion:
                    unique_embedding_similarity_list = gensim_models.post_processing(
                        term, self.model_name)
                    unique_embedding_similarity_list = [word.replace('_', ' ').lower() for word in unique_embedding_similarity_list]
                    syn_exp.extend(unique_embedding_similarity_list)
        logger.debug(
            f'5. {self.gensim_non_ner_relevant_query_tokens.__qualname__}.syn_exp --> {syn_exp} '
        )
        return syn_exp

    def check_synonyms(self):
        # if self.doc
        z = re.match("(?i)\d+g", self.doc.text)
        if z:
            return [token for token in self.doc.text.split()
                    ], [True for token in self.doc.text.split()]
        else:
            return [token.text for token in self.doc
                    ], [token._.not_synonymous for token in self.doc]

    # def relevant_query_tokens(self):
    #     tic = time.time()
    #     self.entities_query()
    #     self.non_entity_query()
    #     if len(self.entities_query()) > 0:
    #         self.entities_query_expansion()
    #     # syn_exp = []
    #     self.ner_relevant_query_tokens()
    #     self.non_ner_relevant_query_tokens()
    #     tokenized_query = list(i.text for i in self.doc.ents)
    #     tokenized_query.extend(self.copy_q)
    #     self.syn_exp.extend(tokenized_query)
    #     if self.ner_expansion_flag:
    #         self.entity_synonym_expansion()
    #     # return self.custom_entities
    #     return {"synonym_expansion": ' '.join('"' + item + '"' for item in self.syn_exp),
    #             "Filter": self.custom_entities['entities'],
    #             "time": time.time() - tic}

    def s2v_relevant_query_tokens(self):
        """

        :return: returns input_request along with acronyms , entities and synonyms to be searched using s2v model
        """
        tic = time.time()

        plane_syns = self.s2v_non_ner_relevant_query_tokens()
        if plane_syns is None:
            plane_syns = []

        if isinstance(self.entities_query(),
                      list) and len(self.entities_query()) >= 1:
            all_ner_syns = self.s2v_entities_query_expansion(
                enforce_entity=True)

            if len(all_ner_syns) > 1:
                plane_syns = ExpansionHelper.expansion_helper_postprocessing_output(
                    plane_syns)
                plane_syns.extend(all_ner_syns)
        elif isinstance(self.entities_query(), str):
            fixed_phrases = self.entities_query()

        logger.debug(f' plane_syns-->{plane_syns} ')
        if self.ner_expansion_flag and isinstance(self.entities_query(), list):
            self.entity_synonym_expansion()
        # return self.custom_entities
        synonym_expansion, input_request, expanded_acronyms = self.result_acronymcheck(
            plane_syns)
        # i for i in synonym_expansion.split() if i.find
        synonym_expansion = self.positive_synonyms_only(synonym_expansion)
        synonyms_only_list = synonym_expansion[1:-1].split('" "')
        ignorance_list = self.search_query.split(" ")
        ignorance_list.extend([i.text for i in self.doc.ents])
        # synonyms_only_list = [i for i in synonyms_only_list if i not in ignorance_list]
        synonyms_only_list = [
            i for i in synonyms_only_list
            if i.lower() not in [k.lower() for k in ignorance_list]
        ]
        # synonym_expansion += ' ' + self.search_query
        # synonym_expansion += ' ' + self.updated_operator_original_query
        result_intent, entity_intent = self.query_intent()
        only_relevant_tokens = input_request
        # only_relevant_tokens = result_intent.replace('"',' ').replace("("," ").replace(")"," ").replace(" + "," ").replace("  "," ").strip()

        entity_text = " +".join(self.entities_query())
        for i in expanded_acronyms[1:-1].split('" "'):
            entity_text = entity_text.replace("+" + i, " " + i)
        modified_query = self.search_query_with_entity_intent(
            self.updated_operator_original_query, self.entities_query())
        # modified_query = self.updated_operator_original_query.replace(" "," +")
        if entity_intent is None or entity_intent == "":
            updated_synonym_expansion = '"' + self.updated_operator_original_query + '"' + ' (' + modified_query + ') ' + '( ' + only_relevant_tokens + " " + synonym_expansion + ' )'
        else:
            updated_synonym_expansion = '"' + self.updated_operator_original_query + '"' + ' (' + modified_query + ') ' + "((" + entity_intent + ") +" + '( ' + only_relevant_tokens + " " + synonym_expansion + ' ))'

        # updated_synonym_expansion = '"'+self.updated_operator_original_query+'"' + ' (' + self.updated_operator_original_query.replace(" "," +") + ') '+ "(("+" +".join(self.entities_query())+") +"+'( '+only_relevant_tokens+" "+ synonym_expansion+' ))'
        #

        # updated_synonym_expansion = '"'+self.updated_operator_original_query+'"' + ' (' + self.updated_operator_original_query.replace(" "," +") + ') '+ '( '+synonym_expansion+' )'
        if isinstance(self.entities_query(), str):
            updated_synonym_expansion = updated_synonym_expansion + ' ' + modified_query + ' ' + ''.join(
                '"' + item + '"' for item in fixed_phrases)
            # result_intent, entity_intent = self.query_intent()
        # ' (' + self.updated_operator_original_query.replace(" "," +") + ') '+
        seo_obj = SynonymExpansionOutput(
            '"' + self.original_input_query + '" ' + ' (' + modified_query +
            ') ' + result_intent.strip(), expanded_acronyms.strip(),
            updated_synonym_expansion.strip(), entity_intent.strip(),
            self.init_original_entities.get(SynonymExpansionOutput_entities, None),
            (self.whitespace_text_tokens, self.text_tokens, synonyms_only_list,
             self.updated_operator_original_query, self.truecase_input),
            time.time() - tic)

        # seo_obj = SynonymExpansionOutput('"' + self.original_input_query + '" '+ result_intent.strip(),
        #                                  expanded_acronyms.strip(),
        #                                   updated_synonym_expansion.strip(),
        #                                    entity_intent.strip(),
        #                                  self.custom_entities.get(SynonymExpansionOutput_entities, None),
        #                                  (self.whitespace_text_tokens,
        #                                   self.text_tokens,
        #                                   synonyms_only_list,
        #                                   self.updated_operator_original_query,
        #                                   self.truecase_input),
        #                                  time.time() - tic
        #                                  )

    def positive_synonyms_only(self, synonym_expansion):
        negative_tokens = list(
            itertools.chain(*self.query_operator_obj.negative_tokens))
        return ' '.join([
            i for i in synonym_expansion.split() if i not in [
                i for i in synonym_expansion.split() for d in negative_tokens
                if d.lower() in i.lower()
            ]
        ])

    def search_query_with_entity_intent(self, text, entities):
        for i in entities:
            text = re.sub(i.lower(), '"' + i.replace(" ", "_").lower() + '"',
                          text.lower())
        return text.replace(" ", " +").replace("_", " ")

    def gensim_relevant_query_tokens(self):
        """

        :return: returns input_request along with acronyms , entities and synonyms to be searched using
        """
        tic = time.time()
        plane_syns = self.gensim_non_ner_relevant_query_tokens()
        logger.info(
            f'6. {self.gensim_non_ner_relevant_query_tokens.__qualname__} EntityLess tokens and their Synonyms  -->  {plane_syns}'
        )
        # if plane_syns is None:
        #     plane_syns = []

        if self.double_quote_flag:
            fixed_phrases = self.entities_query()
        else:
            all_ner_syns = self.gensim_entities_query_expansion()
            logger.debug(
                f'{self.gensim_non_ner_relevant_query_tokens.__qualname__} Final NER Synonyms List --> {all_ner_syns}'
            )
            if len(all_ner_syns):
                logger.debug(f'All tokens + Synonyms : {plane_syns}')
                plane_syns = ExpansionHelper.expansion_helper_postprocessing_output(
                    plane_syns)
                plane_syns.extend(all_ner_syns)

        logger.debug(f'Cleaning Output : {plane_syns}')
        # if self.ner_expansion_flag and isinstance(self.entities_query(), list):
        if self.ner_expansion_flag and not self.double_quote_flag:
            self.entity_synonym_expansion()

        synonym_expansion, input_request, expanded_acronyms = self.result_acronymcheck(
            plane_syns)
        synonym_expansion = self.positive_synonyms_only(synonym_expansion)

        synonyms_only_list = synonym_expansion[1:-1].split('" "')
        ignorance_list = self.search_query.split(" ")
        ignorance_list.extend([i.text for i in self.doc.ents])
        # synonyms_only_list = [i for i in synonyms_only_list if i not in ignorance_list]
        synonyms_only_list = [
            i for i in synonyms_only_list
            if i.lower() not in [k.lower() for k in ignorance_list]
        ]

        # synonym_expansion += ' ' + self.search_query
        # synonym_expansion += ' ' + self.updated_operator_original_query
        # updated_synonym_expansion = self.updated_operator_original_query + ' ' + synonym_expansion
        result_intent, entity_intent = self.query_intent()
        only_relevant_tokens = input_request
        # only_relevant_tokens = result_intent.replace('"',' ').replace("("," ").replace(")"," ").replace(" + "," ").replace("  "," ").strip()

        entity_text = " +".join(self.entities_query())
        for i in expanded_acronyms[1:-1].split('" "'):
            entity_text = entity_text.replace("+" + i, " " + i)
        modified_query = self.search_query_with_entity_intent(
            self.updated_operator_original_query, self.entities_query())
        # modified_query = self.updated_operator_original_query.replace(" "," +")


        if entity_intent is None or entity_intent == "":
            updated_synonym_expansion = '"' + self.updated_operator_original_query + '"' + ' (' + modified_query + ') ' + '( ' + only_relevant_tokens + " " + synonym_expansion + ' )'
        else:
            updated_synonym_expansion = '"' + self.updated_operator_original_query + '"' + ' (' + modified_query + ') ' + "((" + entity_intent + ") +" + '( ' + only_relevant_tokens + " " + synonym_expansion + ' ))'
        # if isinstance(self.entities_query(), str):
        if self.double_quote_flag:
            updated_synonym_expansion = updated_synonym_expansion + ' ' + modified_query + ' ' + ''.join(
                '"' + item + '"' for item in fixed_phrases)
        # ' (' + self.updated_operator_original_query.replace(" "," +") + ') '+
        seo_obj = SynonymExpansionOutput(
            '"' + self.original_input_query + '" ' + ' (' + modified_query +
            ') ' + result_intent.strip(), expanded_acronyms.strip(),
            updated_synonym_expansion.strip(), entity_intent.strip(),
            self.init_original_entities.get(SynonymExpansionOutput_entities, None),
            (self.whitespace_text_tokens, self.text_tokens, synonyms_only_list,
             self.updated_operator_original_query, self.truecase_input),
            time.time() - tic)
        return seo_obj.return_output()

    def acronym_expansion_help(self, tokens: list):
        result = []
        acronym_dict = {}
        logger.debug(f'input tokens of acronym_expansion_help - {tokens}')
        for token in tokens:
            expanded_terms = acronym_expansion(token, self.industry_domain)
            logger.debug(f'expanded_terms_result - {expanded_terms}')
            if expanded_terms is not None:
                result.extend(expanded_terms)
                acronym_dict[token] = expanded_terms
        logger.debug(f'result - {result}')
        return ExpansionHelper.unique_ordered_list(result), acronym_dict

    def result_acronymcheck(self, plane_syns):
        logger.debug(f'{self.result_acronymcheck.__qualname__}')
        # if isinstance(self.init_entities, str):
        if self.double_quote_flag:
            ent_val, plane_query = self.init_entities, self.remove_verb_non_entity_query(
            )
            acronyms, _ = self.acronym_expansion_help(plane_query)
        # elif isinstance(self.init_entities, list):
        else:
            ent_val, plane_query = self.init_entities.copy(
            ), self.remove_verb_non_entity_query()
            logger.debug(f'{ent_val}  --- {plane_query}')
            ent_val.extend(plane_query)
            ent_val = ExpansionHelper.case_insensitive_unique_list(ent_val)
            logger.debug(f'{ent_val} --  Entity+Tokens Inputs')
            acronyms, _ = self.acronym_expansion_help(ent_val)
            logger.debug(f'{acronyms} -- acronyms')
        logger.debug(f'{ent_val}')
        plane_syns.extend(acronyms)
        plane_syns = plane_syns[::-1]

        # logger.debug(f'{[i for i in plane_syns if i not in query_tokens]}')
        # result = ' '.join('"' + item + '"' for item in [i for i in plane_syns if i not in ent_val])
        result = ' '.join('"' + item + '"' for item in plane_syns)
        # result = ' '.join('"' + item + '"^2.0' for item in ent_val) + " " + ' '.join(
        #     '"' + item + '"' for item in [i for i git in plane_syns if i not in ent_val])
        logger.debug(
            f"{self.result_acronymcheck.__qualname__}.All Acronyms for plane syns-->{result}"
        )
        # logger.debug(self.query_intent())
        return result, \
               ' '.join('"' + item + '"' for item in ent_val), \
               ' '.join('"' + item + '"' for item in acronyms)

    def relevant_query_tokens(self, sense2vec_flag=False, gensim_flag=True):
        try:

            if sense2vec_flag:
                output = self.s2v_relevant_query_tokens()
            if gensim_flag:
                output = self.gensim_relevant_query_tokens()
            return output

        except Exception as e:
            logger.error(f'{e}')
            logger.exception(e)

    def token_split_synonyms(self):
        pass

    def entity_synonym_expansion(self):
        for i in self.custom_entities['entities']:
            for j in self.custom_entities['entities'][i]:
                self.custom_entities['entities'][i].extend(
                    self.entity_token_syns[j])
        logger.debug(
            f'{self.entity_synonym_expansion.__qualname__} --->{self.custom_entities}'
        )

    def __call__(self):
        return self.relevant_query_tokens()


# if __name__ == '__main__':
#     # ner_tags = {'wow': ['RSAKHI'],
#     #             'ohoo': ['fdfd']}
#     # print(_lowercase(list(ner_tags.values())))
#     # print(type(ner_tags.values()))
#     # # print(isinstance(ner_tags.values(), dict.values))
#     qh = QueryHandler('I am going to Japan')
#     print(qh.ner_tags)
#     # qh = DataHandler('I am goint to Rsakhi')
#     # print(qh())
