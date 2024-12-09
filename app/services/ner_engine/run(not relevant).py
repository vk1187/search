# import uvicorn
# from fastapi import FastAPI
# from ..SearchLego.Cognitive.Entities.Queries.getEntitiesNERQuery import NERProcessingQuery
# from Integration.model_integrator import spacy_hf_en

# app = FastAPI(debug=True)

# @app.post("/getEntities/")
# def getEntities(query : NERProcessingQuery):
#     """Reads input and outputs the entities based on the model called."""
#     if query is not None:
#       return spacy_hf_en(query.text, query.library_name, query.model_name)
#     else:
#      return "please specify input in the correct format"


# @app.get("/")
# def homepage():
#     """Home Page"""
#     return {"Entities": "Labels"}

# #
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
