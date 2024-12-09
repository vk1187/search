import numpy as np

from app.services.ner_engine.ml_model.spacy import SpacyService
from app.services.utils import flatten
from custom_logging import logger
from elastic_connection.elastic.helper import elastic_query_results


class Helper:
    def __init__(self, index_name=None, project_id=None, client_id=None):
        super().__init__()
        self.index_name = index_name
        self.project_id = project_id
        self.client_id = client_id
        # self.word = word
        # self.result = (self.word in self.vocab and self.word)
        # self.vocab_check = self.result if isinstance(self.result, bool) else [self.result]
        # logger.debug(f'self.word :{self.word}')
        # logger.debug(f'(self.word in self.vocab) : {(self.word in self.vocab)}')
        # logger.debug(f'len(self.word) < 3 : {len(self.word) < 3}')
        # logger.debug(f'get_has_number(self.word) : {get_has_number(self.word)}')
        # self.run_correction_check = (self.word in self.vocab) or len(self.word) < 3 or get_has_number(self.word)

    def check_entity_candidates(self, input_candidates):
        output = ''
        logger.debug(f'input_candidates:{input_candidates}')
        candidates = np.array(input_candidates)[:, 0]
        dic_candidates = {i[0]: i[1:] for i in input_candidates}
        logger.debug(f'dic_candidates: {dic_candidates}')

        if len(candidates) == 1:
            output = candidates
        elif len(candidates) > 1:
            logger.debug(f"In fn check_entity_candidates input is-->{', '.join(candidates)}")
            doc_entities = [SpacyService.extract_entities(i, self.client_id) for i in candidates]
            custom_ent = flatten([list(j["entities"].values())[0] for i, j in doc_entities])
            # doc, custom_entities = SpacyService.extract_entities(', '.join(candidates))
            logger.debug(f'custom_entities --> {custom_ent}')
            # entity_candidates = list(flatten(custom_entities["entities"].values()))
            entity_candidates = list(custom_ent)

            logger.debug(f'In fn check_entity_candidates --> Entities found are {entity_candidates}')
            if len(entity_candidates) == 0:
                return None
                # output = [np.random.choice(candidates)]
            elif len(entity_candidates) == 1:
                output = entity_candidates
            # elif len(entity_candidates) > 1:
            else:
                # logger.debug([(i, dic_candidates[i][2]) for i in entity_candidates])
                # logger.debug(list(sorted([(i, dic_candidates[i][2]) for i in entity_candidates],
                #                          key=lambda x: -x[1])))
                output = list(sorted([(i, dic_candidates[i][2]) for i in entity_candidates], key=lambda x: -x[1]))[0][0]
                # list(sorted(min_edit_matrix, key=lambda item: -item[1]))
                # output = [np.random.choice(entity_candidates)]
        # print(output)
        if isinstance(output, list):
            return {
                'candidate': output[0],
                'frequency': elastic_query_results(
                    index_name=self.index_name,
                    vocab_type='data_dictionary',
                    project_id=self.project_id,
                    candidate_key=output[0],
                    property_attribute='frequency')[output[0]],
                'edit_distance': dic_candidates[output[0]][1]

            }
        elif isinstance(output, str):
            return {'candidate': output,
                    'frequency': elastic_query_results(
                        index_name=self.index_name,
                        vocab_type='data_dictionary',
                        project_id=self.project_id,
                        candidate_key=output,
                        property_attribute='frequency')[output],
                    'edit_distance': dic_candidates[output][1]
                    }
