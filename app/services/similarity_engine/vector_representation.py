# from ..utils import spacy_model, _lowercase
import time

from app.services.ner_engine.ml_model.spacy import SpacyService
from .. import config


# with open("app/services/configSetting.json") as file:
#     config = json.load(file)


class TextEmbeddings:
    """Loading English Model and converting it to spacy format"""

    def __init__(self, text):
        self.tic = time.time()
        self.nlp = SpacyService.model()
        self.text = text
        self.doc = self.nlp(self.text, disable=config['Spacy']['DISABLE_COMPONENTS'])

    def embeddings(self):
        """Return text embeddings of the input"""
        return self.doc.vector

    def show_vector(self):
        return {"text": self.text,
                "vector": self.embeddings().tolist(),
                "length": self.__len__(),
                "time_elapsed": round(time.time() - self.tic, 3)
                }

    def __len__(self):
        return len(self.doc.vector)

# if __name__ == '__main__':
#     te = TextEmbeddings('I am going to Rajasthan')
#     print(te.embeddings())
#     print(len(te))
#
#     import os
#
#     print(os.getcwd())
#     print(config['Spacy']['DISABLE_COMPONENTS'])
