# # from flask import Flask, request
# # # from flask_cors import CORS
# # from functools import lru_cache
# # import tensorflow_hub as hub
# # from typing import Optional
# import spacy
# import uvicorn
# from fastapi import FastAPI
# from pydantic import BaseModel
# import numpy as np
# import config
#
# from elastic import connect_elastic, semantic_search, keyword_search
#
# # Define the app
# # app = Flask(__name__)
# app = FastAPI(debug=True)
#
#
# # Load configs
# # app.config.from_object('config')
# # Set CORS policies
# # CORS(app)
#
# class InputQuery(BaseModel):
#     """Base Class to take input"""
#     query: str
#
#
# # @lru_cache()
# # def get_settings():
# #     return config.Settings()
# #
# # settings: config.Settings = Depends(get_settings)
#
# # Load the universal-sentence-encoder
# # model = hub.load(config.settings.MODEL_URL)
# nlp = spacy.load(config.settings.SPACY_MODEL)
# # Connect to es node
# connect_elastic(config.settings.ELASTIC_IP, config.settings.ELASTIC_PORT)
#
#
# @app.post("/query/")
# def qa(input: InputQuery):
#     if input.query != '':
#         # Generate embeddings for the input query
#         query_vec = np.asarray(nlp(input.query).vector).tolist()
#         # Retrieve the semantically similar records for the query
#         records = semantic_search(query_vec, thresh = config.settings.SEARCH_THRESH)
#
#         # Retrieve records using keyword search (TF-IDF score)
#         # records = keyword_search(request.args.get("query"), app.config['SEARCH_THRESH'])
#     else:
#         return {"error": "Couldn't process your request"}, 422
#     return {"data": records}
#
#
# # @app.route("/query", methods=["GET"])
# # def qa():
# #     # API to return top_n matched records for a given query
# #     if request.args.get("query"):
# #         # Generate embeddings for the input query
# #         query_vec = np.asarray(model([request.args.get("query")])[0]).tolist()
# #         # Retrieve the semantically similar records for the query
# #         records = semantic_search(query_vec, app.config['SEARCH_THRESH'])
# #
# #         # Retrieve records using keyword search (TF-IDF score)
# #         # records = keyword_search(request.args.get("query"), app.config['SEARCH_THRESH'])
# #     else:
# #         return {"error": "Couldn't process your request"}, 422
# #     return {"data": records}
#
#
# if __name__ == '__main__':
#     uvicorn.run(app, host="0.0.0.0", port=8000)
