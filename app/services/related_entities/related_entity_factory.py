import faiss
import numpy as np
import re
# from app.services.config_constants import batch_size_to_process_related_entities
from load_parameters import get_parameters
from app.services.ner_engine.ml_model.spacy.spacy_service import SpacyService
from app.services.related_entities.helper import write_query_index, write_entity_pickles,delete_old_files
from custom_logging import logger
from app.services.utils import fix_top_N


class RelatedEntity:
    # @classmethod
    # def query_encoder(cls, model, query):
    #     """Encoding queries through HuggingFace model"""
    #     return model.encode(query, convert_to_tensor=True)

    @classmethod
    def search(cls, query_index, entity_idx2tok, entity_idx2entities,
               query_vector, query_entity, input_query, top_counter,
               similarity_threshold_percent):
        """returns results using faiss indexing"""

        if not np.array_equal(np.zeros(query_vector.shape), query_vector):
            faiss.normalize_L2(query_vector)
            k = min(top_counter * 5, len(entity_idx2tok))
            top_k = query_index.search(query_vector, k)
            result = [{
                'query': entity_idx2tok[_id],
                'score': np.round(score * 100, 2)
            } for score, _id in zip(top_k[0].tolist()[0], top_k[1].tolist()[0])
                      if (entity_idx2entities[_id].lower() == query_entity[0].
                          lower()) and (input_query.lower().strip(
                          ) != entity_idx2tok[_id].lower().strip()) and (
                              input_query.lower().strip() != '')
                      and score >= similarity_threshold_percent]

            result = fix_top_N(input_query, result)
        else:
            result = None
        return result
    # This method will take entities list as a input and will generate the index file from those entities
    # The index file will have vector representation of all the entities generated from Spacy Large model.
    @classmethod
    def save_indexes(cls, entities, project_id, client_id):
        """returns results using faiss indexing"""
        try:
            parameters = get_parameters()
            batch_size_to_process_related_entities = parameters.getint(
                "related_entity", "batch_size")
            ev = []
            ent_values = list(entities.values())
            for i in ent_values:
                ev.extend(i)
            entity_values = sorted(
                np.unique(list(map(lambda x: x.lower().strip(), ev))).tolist())
            # entity_values = sorted(list())
            tok2idx = {j: i for i, j in enumerate(entity_values)}
            idx2tok = {j: i for i, j in tok2idx.items()}
            idx2entities = {
                tok2idx[j.lower().strip()]: i
                for i in entities for j in entities[i]
            }
            disable_clients = [
                str(i) for i in SpacyService.get_ruler_names()
                if i != client_id
            ]
            disable_components = ['tagger', 'attribute_ruler', 'lemmatizer'
                                  ] + disable_clients
            unique_ents_vecotrs = np.array([
                i.vector for i in SpacyService.model_lg().pipe(
                    entity_values,
                    batch_size=batch_size_to_process_related_entities,
                    disable=disable_components)
            ])

            delete_old_files(client_id, project_id,"PeopleAlsoSearch")
            entity_data = {"idx2tok": idx2tok, "idx2entities": idx2entities, "tok2idx": tok2idx}
            entity_pickle_name = write_entity_pickles(entity_data, project_id, client_id)
            entity_vector_repr_name = write_query_index(unique_ents_vecotrs, project_id, client_id)
            return entity_pickle_name, entity_vector_repr_name

        except Exception as e:
            logger.error(
                '[RelatedEntity.save_indexes] Unable to save entity indexes and entity tokens'
            )
            logger.error(e)
            logger.exception(e)
            return None, None
            # return {'status': False,
            # 'entity_pickle_name':None,
            # 'entity_vector_index_name':None,
            # 'time': time.time() - tic}

    # def topk_queries(cls,query_embedding):
    #     top_k = min(5, len(corpus))
    #     cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    #     top_results = torch.topk(cos_scores, k=top_k)
    #     return

