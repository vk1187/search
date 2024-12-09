import time
from collections import Counter

from gensim.models.phrases import ENGLISH_CONNECTOR_WORDS
from gensim.models.phrases import Phrases
from nltk import ngrams

from app.services import DataPreprocessor
from app.services import auto_completion_flag
from app.services import auto_completion_max_shingle_length
from app.services import auto_completion_min_shingle_length
from app.services import auto_completion_phraser_flag


class AutoComplete:
    """returns autcompleted words"""

    def __init__(self, vocab_dict):
        self.vocab_dict = vocab_dict

    def __call__(self):
        return self.output_suggestions()

    def output_suggestions(self):
        sorted_tuples = sorted(self.vocab_dict.items(),
                               key=lambda item: -item[1])
        sorted_dict = {k: v for k, v in sorted_tuples}
        return [{'key': i, 'count': j} for i, j in sorted_dict.items()]

    @classmethod
    def extract_autocomplete_suggestions_ngram(cls, text):
        tic = time.time()
        text = DataPreprocessor(text, auto_completion_flag)()
        grams = [
            list((ngrams(text, i))) for i in range(
                auto_completion_min_shingle_length, auto_completion_max_shingle_length)
        ]
        clean_grams = [' '.join(i) for j in grams for i in j]
        clean_gram_dict = Counter(clean_grams)
        return cls(clean_gram_dict)()

    @classmethod
    def extract_autocomplete_suggestions_phrases(cls, text):
        tic = time.time()
        text = DataPreprocessor(text, auto_completion_phraser_flag)()
        bigram = Phrases(text,
                         min_count=1,
                         connector_words=ENGLISH_CONNECTOR_WORDS,
                         delimiter=' ')
        vocab_bigram = dict(bigram.vocab)
        for i in range(auto_completion_max_shingle - 1):
            bigram = Phrases(bigram[text],
                             min_count=1,
                             connector_words=ENGLISH_CONNECTOR_WORDS,
                             delimiter=' ')
            new_bigram = bigram.vocab
            vocab_bigram.update(new_bigram)
            print(len(vocab_bigram))
        return cls(vocab_bigram)()
