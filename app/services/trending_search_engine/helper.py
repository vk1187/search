import datetime
from datetime import timedelta

import numpy as np
import pandas as pd

from app.services.config_constants import search_analytics_collections_name
from app.services.utils import trendingsearch_relatedsearch_widget_cleaner
from app_cache import cache
from mongodb_connection.mongodb.helper import MongoConnection, search_analytics_count_pipeline

from load_parameters import get_parameters
parameters = get_parameters()

trending_search_cache_seconds = parameters.getint("trending_search",
                                                  "cache_seconds")


def filter_data(df, client_id=None, project_id=None, project_name=None):
    if client_id is not None:
        df = df[df["clientId"] == client_id]
    if project_id is not None:
        df = df[df["projectId"] == project_id]
    # if project_name is not None:
    #     df = df[df["projectName"] == project_name]
    return df.groupby(['date', 'query']).count().iloc[:, :1].reset_index()


def current_frequency(df, today_date, current_freq_delta=0):
    days = today_date - timedelta(days=current_freq_delta)
    return df[df.date >= days].reset_index(drop=True), current_freq_delta


def current_days_present_in_logs(df_pivot, current_period=7):
    current_records = len([
        i for i in df_pivot.columns
        if datetime.datetime.strptime(i, '%Y-%m-%d').date() >= (
            datetime.datetime.now() - timedelta(days=current_period)).date()
    ])
    return current_records


def z_score_calculation(query_array, current_records=10):
    custom_weights = np.array(list(range(1, query_array.shape[1] + 1)))
    current_values = np.average(query_array[:, -current_records:],
                                weights=custom_weights[-current_records:],
                                axis=1)
    historical_values = np.average(query_array, weights=custom_weights, axis=1)
    # current_values = query_array[:, -current_records:].mean(axis=1)
    # historical_values = query_array.mean(axis=1)
    std_dev = query_array.std(axis=1, ddof=0)
    age = (query_array > 0).astype(int).sum(axis=1)
    #     print(current_values.sum())
    if current_values.sum() == 0 or historical_values.sum(
    ) == 0 or std_dev.sum() == 0:
        return {'result': None}
    else:
        return np.round(
            ((current_values - historical_values) / (std_dev+1)), 4) * 100


@cache.memoize(trending_search_cache_seconds)
def historical_frequency(mode=None):
    historical_frequency_dict = {
        "monthly": 30,
        "quarterly": 90,
        "yearly": 365,
        "bimonthly": 60
    }
    return historical_frequency_dict.get(mode, 60)


def output(df, column=None):
    if column is None:
        return df[['age']].sort_values('age', ascending=False).head(10)
    elif isinstance(column, str) and column in df.columns:
        return df[[column]].sort_values(column, ascending=False).head(10)
    elif isinstance(column, list):
        columns_available = []
        columns_available.extend(column)
        return df[[i for i in columns_available if i in df.columns]]


def cross_join_data(df):
    unique_queries = df[['query']].drop_duplicates().reset_index(drop=True)
    unique_dates = df[['date']].drop_duplicates().reset_index(drop=True)
    unique_queries['key'] = 1
    unique_dates['key'] = 1
    cross_join_dates_query = pd.merge(unique_dates, unique_queries,
                                      on='key').drop(labels="key", axis=1)
    return cross_join_dates_query


@cache.memoize(trending_search_cache_seconds)
def preprocessing_trending_search_dataframe(project_id, client_id, delta_days,
                                            current_frequency_threshold,
                                            current_period, excludedDomains=None,user_id=None):
    client = MongoConnection.getInstance(is_log_connection=True)
    parameters = get_parameters()
    search_analytics_db_name = parameters.get("DEFAULT",
                                              "search_analytics_db_name")

    
    collection = client[search_analytics_db_name][search_analytics_collections_name]
    if excludedDomains is None:
            
        cursr_search_logs = collection.aggregate(
            search_analytics_count_pipeline(project_id=project_id, client_id=client_id, user_id=user_id,
                                            historial_delta=delta_days))
    else:
        cursr_search_logs = collection.aggregate(
            search_analytics_count_pipeline(project_id=project_id, client_id=client_id, excludedDomains=excludedDomains,
                                            historial_delta=delta_days))

    df = pd.DataFrame(list(cursr_search_logs))
    if df.shape[0] == 0:
        raise Exception(
            "[Trending Search] No data is avaialble through query in the database"
        )
    else:
        df['query'] = df['query'].apply(
            lambda x: trendingsearch_relatedsearch_widget_cleaner(x).strip(
            ).lower())
        input_query_time = df.groupby(
            ['query'])['original_timestamp'].max().to_dict()
        df = df.groupby(['timestamp', 'query'])['count'].sum().reset_index()
        df = df[df['query'] != ''].reset_index()
        df_pivot = df.pivot(index='query', columns='timestamp', values='count')
        df_pivot = df_pivot[df_pivot.columns.sort_values(
            ascending=True)].fillna(0)
        df_pivot = df_pivot[df_pivot.sum(axis=1) > current_frequency_threshold]
        current_interval = current_days_present_in_logs(
            df_pivot, current_period=current_period)
        return df_pivot, current_interval, input_query_time
