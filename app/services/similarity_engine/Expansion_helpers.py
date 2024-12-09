from app.services.config_constants import query_output_processing_flag
from app.services.utils import DataPreprocessor
from custom_logging import logger


class ExpansionHelper:
    # @classmethod
    # def sorted_entities(cls, similar_terms, term, entity=None):
    #     similar_entities = similar_terms
    #     # if entity in ['ORG', 'GPE', 'LOC', 'NORP']:
    #     #     similar_entities = [i for i in similar_terms if i[0].lower() == term[0].lower()]
    #     #     similar_entities.extend([i for i in similar_terms if i[0].lower() != term[0].lower()])
    #     # else:
    #     #     similar_entities = similar_terms
    #     return similar_entities

    @classmethod
    def unique_ordered_list(cls, seq):
        """reutrns unique list in the original order as sent in input"""
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]

    @classmethod
    def case_insensitive_unique_list(cls, data):
        """reutrns unique list in the original order as sent in input irrespective of case"""
        seen, result = set(), []
        for item in data:
            if item.lower() not in seen:
                seen.add(item.lower())
                result.append(item)
        return result

    @classmethod
    def expansion_helper_postprocessing_output(cls, similar_terms):
        logger.debug('expansion_helper_postprocessing_output')
        return list(set([DataPreprocessor(i, query_output_processing_flag)().strip() for i in similar_terms if
                         DataPreprocessor(i, query_output_processing_flag)().strip() != '']))
