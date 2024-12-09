import csv

from pymongo import MongoClient

from app.services.config_constants import acronym_file_path
# from config_constants import database_name
from app.services.config_constants import mongodb_acronym_collection as acronym_collection
from load_parameters import get_parameters


def csv2dictlist(input_path=acronym_file_path, mode='r'):
    csvfile = open(input_path, mode=mode)
    reader = csv.DictReader(csvfile)
    csvfile.close()
    header = reader.fieldnames
    dict_list = []
    # header = ["ID",
    #           "Acronym",
    #           "FullForm",
    #           "Domain"]
    for each in reader:
        row = {}
        for field in header:
            if field == 'Options':
                row[field] = each[field].split(',')
            else:
                row[field] = each[field]
        dict_list.append(row)
    return dict_list


client = MongoClient(host='localhost', port=27017)

db = client[parameters["DEFAULT"]['main_database_name']]
# db[acronym_collection].drop()
all_records = csv2dictlist(input_path=acronym_file_path, mode='r')
db[acronym_collection].insert_many(all_records)
