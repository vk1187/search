# from pandas.core.common import flatten

# from utils import _lowercase, spacy_model

# with open(config_settings_path) as file:
#     config = json.load(file)
from app.services import config


class DataHandler:
    def __init__(self, document: str):
        self.document = document
        self.doc_tokens = document.split()
        self.document_nested = []

    def document_splitter(self):
        if len(self.doc_tokens) > config['Spacy']['TOKEN_THRESH']:
            for i in range(0, len(self.doc_tokens), config['Spacy']['TOKEN_THRESH']):
                # print(i)
                self.document_nested.append(' '.join(self.doc_tokens[i:i + config['Spacy']['TOKEN_THRESH']]))
        else:
            self.document_nested.append(self.document)

        return self.document_nested

    def show_document(self):
        return {"Splitted Documents": self.document_splitter(), "length": self.__len__()}

    def __call__(self):
        return self.show_document()

    def __len__(self):
        return len(self.document_nested)

# if __name__ == '__main__':
#     ner_tags = {'wow': ['RSAKHI'],
#                 'ohoo': ['fdfd']}
#     print(_lowercase(list(ner_tags.values())))
#     print(type(ner_tags.values()))
#     # print(isinstance(ner_tags.values(), dict.values))
#     qh = QueryHandler('I am goint to Rsakhi', ner_tags)
#     print(qh())
#     qh = DataHandler('I am goint to Rsakhi')
#     print(qh())
