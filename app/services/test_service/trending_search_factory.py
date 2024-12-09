import time

import numpy as np

from app.services.trending_search_engine.helper import z_score_calculation


def main(df_pivot, current_interval, topk,input_query_time, tic):
    """Returns trending query on the basis of z score calculation"""
    query_array = df_pivot.values
    _zscores = z_score_calculation(query_array, current_records=current_interval)
    if isinstance(_zscores, dict):
        return {'result': None,
                'eta': time.time() - tic,
                'status':False
                }
    else:
        query_timestamp = [input_query_time[i].timestamp() for i in df_pivot.index]
        combined_scores = np.array(list(zip(query_timestamp,-_zscores)))
        query_sorter = np.lexsort((combined_scores[:,0],combined_scores[:,1]))[:topk]
        _zscores[query_sorter]
        # query_sorter = np.argsort(-_zscores)[:topk]
        query_zscores = [{'query': i, 'score': j} for i, j in
                         list(zip(df_pivot.index.values[query_sorter], _zscores[query_sorter]))]
        return {'result': query_zscores,
                'eta': time.time() - tic,
                'status':False if (query_zscores is None) or len(query_zscores)==0 or any(x is None for x in query_zscores) else True
                }

    # today=datetime.now().date()
    # cross_join_dates_query = cross_join_data(df)
    # subset_df = filter_data(df)
    # subset_df.columns = ['date','query','counts']
    # query_dates_count = pd.merge(cross_join_dates_query, subset_df, how='outer').fillna(0)
    # query_dates_count = query_dates_count[query_dates_count['query']!='']
    # current_freq, current_delta = current_frequency(query_dates_count, today, 20)

    # weekly_counts = current_freq.groupby('query').mean().iloc[:, :1]
    # weekly_counts = weekly_counts['counts'].rename('weekly_counts')

    # historical_counts_from_start = historical_frequency(query_dates_count, today, current_delta,mode='quarterly').groupby('query')[
    #                                    'counts'].mean() 
    #                             # / \
    #                             #    historical_frequency(query_dates_count, today, current_delta,mode='quarterly').groupby('query')[
    #                             #        'query'].count()

    # historical_counts_from_start = historical_counts_from_start.rename("historical_counts_from_start")

    # historical_counts_on_usage_dates = historical_frequency(query_dates_count, today, current_delta,mode='quarterly').groupby('query')[
    #                                        'counts'].mean() 
    #                                 #        / \
    #                                 #    historical_frequency(query_dates_count, today, current_delta,mode='quarterly').groupby('query')[
    #                                 #        'counts'].count()
    # historical_counts_on_usage_dates.fillna(1, inplace=True)
    # historical_counts_on_usage_dates = historical_counts_on_usage_dates.rename('historical_counts_on_usage_dates')

    # age = query_dates_count.groupby('query')['counts'].count()
    # age = age.rename('age')

    # hist_counts = historical_frequency(query_dates_count, today, current_delta)
    # hist_counts['counts'].fillna(0, inplace=True)
    # std_dev = hist_counts.groupby('query')['counts'].agg(np.std, ddof=1)
    # std_dev.fillna(1, inplace=True)
    # std_dev = std_dev.rename('std_dev')

    # trend = pd.concat([
    #     weekly_counts,
    #     historical_counts_from_start,
    #     historical_counts_on_usage_dates,
    #     age,
    #     std_dev
    # ],
    #     axis=1)
    # trend.loc[trend.std_dev == 0, 'std_dev'] = 1

    # try:
    #     if (trend[['weekly_counts']].isnull().apply(lambda x: all(x), axis=0).values[0]) | (
    #             trend[['historical_counts_from_start']].isnull().apply(lambda x: all(x), axis=0).values[0]):
    #         return trend.sort_values('age', ascending=False)
    #     else:
    #         trend['z_score_start'] = ((trend.weekly_counts - trend.historical_counts_from_start) / trend.std_dev) * trend.age
    #         trend['z_score_usage_dates'] = ((trend.weekly_counts - trend.historical_counts_on_usage_dates) / trend.std_dev) * trend.age
    #         # print(trend.sort_values('z_score_start', ascending=False))
    #         trend = output(trend,'z_score_start')
    #         return {"result":trend.to_json(),"eta":time.time()-tic}
    # except Exception as e:
    #     logger.debug(f'[Trending Search]\n{e}')
    #     return {"result":output(trend).to_json(),"eta":time.time()-tic}
