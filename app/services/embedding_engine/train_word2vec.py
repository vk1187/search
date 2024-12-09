from gensim.models.phrases import Phrases
from gensim.models.word2vec import Text8Corpus

Text8Corpus('../../data/')
phrase_model = Phrases.load("phrase_model.pkl")
cores = multiprocessing.cpu_count()
phrased_sentences = phrase_model[sentences]

w2v_model = Word2Vec(min_count=10, window=5, vector_size=300, sample=1e-5, alpha=0.03, epochs=20, negative=5,
    workers=cores, compute_loss=True, batch_words=10000, sorted_vocab=0, )

w2v_model = Word2Vec.load("wiki.en.word2vec_09022021.model")
w2v_model.build_vocab(phrased_sentences, update=True)  # prepare the model vocabulary
w2v_model.train(phrased_sentences, total_examples=w2v_model.corpus_count, epochs=w2v_model.epochs)
w2v_model.save('wiki.en.word2vec_wiki_news_09022021.model')


class RetrainWord2vec:
    def __init__(self):
        self.w2v_model = Word2Vec.load("../../wiki.en.word2vec_09022021.model")
