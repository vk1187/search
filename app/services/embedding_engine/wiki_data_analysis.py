from gensim.models.phrases import Phrases, ENGLISH_CONNECTOR_WORDS
from gensim.models.word2vec import Text8Corpus
from gensim.test.utils import datapath

sentences = Text8Corpus(datapath('..\..\..\..\models\wiki.en.text'))
phrases = Phrases(sentences, min_count=1, threshold=0.1, connector_words=ENGLISH_CONNECTOR_WORDS)
for phrase, score in phrases.find_phrases(sentences).items():
    print(phrase, score)
print(sentences)

# from gensim import utils
# import json
# # iterate over the plain text data we just created
# with utils.open('enwiki.json.gz', 'rb') as f:
#     for line in f:
#         article = json.loads(line)
#         print("Article title: %s" % article['title'])
#         print(f"Interlinks: {article['interlinks']}")
#         for section_title, section_text in zip(article['section_titles'], article['section_texts']):
#             print("Section title: %s" % section_title)
#             print("Section text: %s" % section_text)
