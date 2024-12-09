#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import time

start_time = time.time()

if sys.version[0] != "3":
    print("nThis script requires Python 3")
    print("Please run the script using the 'python3' command.n")
    quit()
try:
    # import the Elasticsearch low-level client library
    from elasticsearch import Elasticsearch
    # import Pandas, JSON, and the NumPy library
    import pandas, json
    import numpy as np
except ImportError as error:
    print("nImportError:", error)
    print("Please use 'pip3' to install the necessary packages.")
    quit()
# create a client instance of the library
print("ncreating client instance of Elasticsearch")
elastic_client = Elasticsearch()

"""
MAKE API CALL TO CLUSTER AND CONVERT
THE RESPONSE OBJECT TO A LIST OF
ELASTICSEARCH DOCUMENTS
"""
# total num of Elasticsearch documents to get with API call

print("nmaking API call to Elasticsearch for", "documents.")
response = elastic_client.search(
    index='cognitive_datadictionary_111194_25_5_20219_8',
    body={},
    size=60000
)
# grab list of docs from nested dictionary response
print("putting documents in a list")
elastic_docs = response["hits"]["hits"]

"""
GET ALL OF THE ELASTICSEARCH
INDEX'S FIELDS FROM _SOURCE
"""
#  create an empty Pandas DataFrame object for docs
docs = pandas.DataFrame()
# iterate each Elasticsearch doc in list
print("ncreating objects from Elasticsearch data.")
for num, doc in enumerate(elastic_docs):
    # get _source data dict from document
    source_data = doc["_source"]
    # get _id from document
    _id = doc["_id"]
    # create a Series object from doc dict object
    doc_data = pandas.Series(source_data, name=_id)
    # append the Series object to the DataFrame object
    docs = docs.append(doc_data)

"""
EXPORT THE ELASTICSEARCH DOCUMENTS PUT INTO
PANDAS OBJECTS
"""
print("nexporting Pandas objects to different file types.")

# export the Elasticsearch documents as a JSON file
docs.to_json("objectrocket.json")
# have Pandas return a JSON string of the documents
json_export = docs.to_json()  # return JSON data
# print ("nJSON data:", json_export)
# export Elasticsearch documents to a CSV file
docs.to_csv("objectrocket.csv", ",")  # CSV delimited by commas
# export Elasticsearch documents to CSV
csv_export = docs.to_csv(sep=",")  # CSV delimited by commas
# print ("nCSV data:", csv_export)
# create IO HTML string
import io

html_str = io.StringIO()
# export as HTML
docs.to_html(
    buf=html_str,
    classes='table table-striped'
)

# print out the HTML table
# print (html_str.getvalue())
# save the Elasticsearch documents as an HTML table
docs.to_html("objectrocket.html")

print("nntime elapsed:", time.time() - start_time)
