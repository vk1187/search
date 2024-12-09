import spacy
# import tensorflow_hub as hub
import numpy as np
from tqdm import tqdm
import pandas as pd

from elastic import connect_elastic, insert_qa,reindex_qa
import config_e as config


def process_qa():
    df = pd.read_csv("data/COVID-QA_v1.csv")
    df = df[~df.Answers.isna()]
    df = df[~df.Question.isna()]
    df.dropna(inplace=True, subset=["Answers", "Question"])

    print("\nIndexing QA's...")
    for _, row in tqdm(df.iterrows()):
        # Index each qa pair along with the question id and embedding
        if  sum(np.asarray(nlp(row['Answers']).vector).tolist())==0:
            answer_vec =  np.asarray(np.ones(300)).tolist()
        else:
            answer_vec = np.asarray(nlp(row['Answers']).vector).tolist()

        insert_qa({
            'q_id': row['Question ID'],
            'question': row['Question'],
            'answer': row['Answers'],
            'question_vec': np.asarray(nlp(row['Question']).vector).tolist(),
            'answer_vec': answer_vec

        })


if __name__ == '__main__':
    # Load the universal-sentence-encoder model
    # model = hub.load(config.settings.MODEL_URL)
    nlp = spacy.load(config.settings.SPACY_MODEL)
    print("Model loaded successfully...")
    # Connect to elasticsearch node
    connect_elastic(config.settings.ELASTIC_IP, config.settings.ELASTIC_PORT)
    # Index the dataset
    if config.settings.REINDEX_FLAG:
        reindex_qa()
    process_qa()

# nlp = spacy.load('en_core_web_lg')
#
# doc = nlp(document_string)
#
#
# for token in doc:
#     v = token.vector
#     v_str = ('%5.2f ' * 4) % tuple(v[:4])
#     print(row(token, '|', '(' + v_str + '...)'))