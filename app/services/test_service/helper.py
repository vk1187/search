from random import randint
from app_cache import cache
import time
@cache.memoize(10)
def results_fixed(project_id,client_id,backlog_days,current_period,topk,current_frequency_threshold):
    print('cache is not used')
    return {
            "time": time.time(),
            "random_number": randint(1, 100),
            "project_id": project_id,
            "client_id": client_id, 
            "current_period": current_period,
            "backlog_days": backlog_days,
            "topk": topk,
            "current_frequency_threshold": current_frequency_threshold
            }