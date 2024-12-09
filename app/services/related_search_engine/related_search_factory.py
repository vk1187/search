import faiss
import numpy as np

from custom_logging import logger
from mongodb_connection.mongodb.helper import fetch_mannual_rules
from mongodb_connection.mongodb.helper import widget_post_processing_ignorance_rules
from app.services.utils import fix_top_N

expected_count = 5


class RelatedSearch:
    @classmethod
    def query_encoder(cls, model, query):
        """Encoding queries through HuggingFace model"""
        return model.encode(query, convert_to_tensor=True)

    @classmethod
    def search(cls, index, query, model, corpus, threshold_score, negative_tokens, widget_counter):
        """returns results using faiss indexing"""
        # query_vector = model.encode([query])
        old_query, updated_query = query
        try:

            query_vector = cls.query_encoder(model, [updated_query]).numpy()
            faiss.normalize_L2(query_vector)
            k = min(100, len(corpus))
            top_k = index.search(query_vector, k, )
            result = [{'query': corpus[_id], 'score': np.round(score * 100, 2)} for score, _id in
                      zip(top_k[0].tolist()[0], top_k[1].tolist()[0]) if
                      (corpus[_id].strip().lower() != old_query.strip().lower()) and score >= threshold_score]
            result = cls.post_processing_widget_cleaner(result)
            count = 0
            results = []
            for i in result:

                negative_tokens_counter = 0
                for k in negative_tokens:
                    if i['query'].lower().find(k.lower()) >= 0:
                        negative_tokens_counter += 1
                if negative_tokens_counter == 0:
                    count += 1
                    results.append(i)

                if count == widget_counter+25:
                    break
            
            results = fix_top_N(updated_query, results)
            return results
        except Exception as e:
            logger.error(f'{e}')
            logger.exception(e)

    @classmethod
    def post_processing_widget_cleaner(cls, input_list):
        temp = []
        relatedsearch_postprocessing_rules = fetch_mannual_rules(rule_type="relatedsearch_postprocessing")
        for i in input_list:
            result = widget_post_processing_ignorance_rules(i['query'], relatedsearch_postprocessing_rules)
            if not isinstance(result, bool):
                status, token = result
                i['query'] = token
            elif isinstance(result, bool):
                status = result
            if status:
                if len(temp) == 0:
                    temp.append(i)
                elif len(temp) > 0:
                    donot_append = 0
                    for temp_dict in temp:
                        if temp_dict['query'] == i['query']:
                            donot_append = 1
                            # break
                    if donot_append != 1:
                        temp.append(i)
                elif len(temp) == expected_count:
                    break
        return temp
        # return [i for i in result if widget_post_processing_ignorance_rules(i['query'],
        # relatedsearch_postprocessing_rules)==True]

    # def topk_queries(cls,query_embedding):
    #     top_k = min(5, len(corpus))
    #     cos_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]
    #     top_results = torch.topk(cos_scores, k=top_k)
    #     return
