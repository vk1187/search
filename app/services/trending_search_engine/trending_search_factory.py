import math

import numpy as np

from app.services.config_constants import force_runzscore
from app.services.trending_search_engine.helper import z_score_calculation
from app.services.utils import min_max_normalization
from app_cache import cache

from load_parameters import get_parameters
parameters = get_parameters()
trending_search_cache_seconds = parameters.getint("trending_search", "cache_seconds")

# def min_max_normalization(x):
#     """Min_Max Normalization"""
#     return np.round(((x-np.min(x))/(np.max(x)-np.min(x)))*100,2)

def z_score_result(df_pivot, current_interval, topk, input_query_time):
    query_array = df_pivot.values
    _zscores = z_score_calculation(query_array, current_records=current_interval)

    if isinstance(_zscores, dict):
        return None
        # return {'result': None,
        #         'eta': time.time() - tic,
        #         'status':False
        #         }
    else:
        _zscores = min_max_normalization(_zscores)
        query_timestamp = [input_query_time[i].timestamp() for i in df_pivot.index]
        combined_scores = np.array(list(zip(query_timestamp, -_zscores)))
        query_sorter = np.lexsort((combined_scores[:, 0], combined_scores[:, 1]))[:topk]
        # _zscores[query_sorter]
        # query_sorter = np.argsort(-_zscores)[:topk]
        query_zscores = [{'query': i, 'score': j} for i, j in
                         list(zip(df_pivot.index.values[query_sorter], _zscores[query_sorter]))]
        return query_zscores
        # return {'result': query_zscores,
        #         'eta': time.time() - tic,
        #         'status':False if (query_zscores is None) or len(query_zscores)==0 or any(x is None for x in query_zscores) else True
        #         }


@cache.memoize(trending_search_cache_seconds)
def main(df_pivot, current_interval, topk, input_query_time):
    """Returns trending query on the basis of z score calculation"""
    # query_array = df_pivot.values
    # current_interval=search_analytics_current_period if current_interval==0 else current_interval
    if current_interval <= 0.1 * df_pivot.values.shape[1] and current_interval > 0:
        return z_score_result(df_pivot, current_interval, topk, input_query_time)
    elif force_runzscore == True:
        current_interval = math.ceil(0.1 * df_pivot.values.shape[1])
        return z_score_result(df_pivot, current_interval, topk, input_query_time)
    # else:
    #     return {'result': None,
    #             'eta': time.time() - tic,
    #             'status':False
    #     }
