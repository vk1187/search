from spacy.lang.en import English
from spacy.language import Language
from spacy.vocab import Vocab
import spacy
# import en_core_web_sm
from app.services.ner_engine.ml_model.spacy.custom_components import custom_infix
from custom_logging import logger

# import en_core_web_lg
# from spacy.tokens import Token
english_model = English()
english_model_tokenizer = english_model.tokenizer


class EnglishSentenceModelSpacyInit:
    english_sentence_model = None

    # Load spacy model  for NER Extraction
    @classmethod
    def load_english_sentence_model(cls):
        """Load all the spacy models at startup"""
        try:
            # cls.english_sentence_model = Language(Vocab())
            cls.english_sentence_model = spacy.load('en_core_web_sm', disable=['tagger', 'parser', 'ner','tok2vec','attribute_ruler','lemmatizer'])
            # cls.english_sentence_model = en_core_web_sm.load()
            # cls.english_sentence_model = custom_infix(cls.english_sentence_model)
            # cls.english_sentence_model.disable_pipe("parser")
            cls.english_sentence_model.add_pipe('sentencizer')
            # cls.english_sentence_model.add_pipe("set_custom_sentence_end_points", after='sentencizer')
            cls.english_sentence_model.max_length = 135775100
            logger.debug('english_sentence_model Model Loaded')
        except Exception as e:
            logger.exception(f'{e} - Unable to load the english_sentence_model')

    @classmethod
    def get_english_sentence_model(cls):
        if cls.english_sentence_model is not None:
            return cls.english_sentence_model
        else:
            cls.load_english_sentence_model()
            return cls.english_sentence_model


# from Models.spacy.load_spacy import spacy_lg, spacy_sm, spacy_md, spacy_entities
# import SpacyModel

# from .load_spacy import SpacyInit
# # from app import SpacyInit
# from ...utils import output_converter
# from ...utils import output_format


class EnglishSentenceModelService:
    """Spacy singelton"""
    spacy_model = None

    def __init__(self):
        objspacy = EnglishSentenceModelSpacyInit()
        objspacy.load_english_sentence_model()
        # SpacyService.spacy_model == objspacy.get_spacy_model()

    @classmethod
    def model(cls):
        objspacy = EnglishSentenceModelSpacyInit()
        # cls.spacy_model = objspacy.get_spacy_model()
        return objspacy.get_english_sentence_model()


class EnglishModelInit:
    english_model = None

    # Load spacy model  for NER Extraction
    @classmethod
    def load_english_model(cls):
        """Load all the spacy models at startup"""
        try:
            cls.english_model = English()
            cls.english_model = custom_infix(cls.english_model)

            # cls.english_model.add_pipe("set_custom_sentence_end_points", after='sentencizer')
            # cls.english_model.max_length = 135775100
            logger.debug('english Model Loaded')
        except Exception as e:
            logger.exception(f'{e} - Unable to load the english_model')

    @classmethod
    def get_english_model(cls):
        if cls.english_model is not None:
            return cls.english_model
        else:
            cls.load_english_model()
            return cls.english_model

    @classmethod
    def get_english_model_tokenizer(cls):
        if cls.english_model is not None:
            return cls.english_model.tokenizer
        else:
            cls.load_english_model()
            return cls.english_model.tokenizer


class EnglishModelService:
    """Spacy singelton"""
    english_model = None

    def __init__(self):
        objspacy = EnglishModelInit()
        objspacy.load_english_model()

    @classmethod
    def model(cls):
        objspacy = EnglishModelInit()
        # cls.spacy_model = objspacy.get_spacy_model()
        return objspacy.get_english_model()

    @classmethod
    def tokenizer(cls):
        objspacy = EnglishModelInit()
        # cls.spacy_model = objspacy.get_spacy_model()
        return objspacy.get_english_model_tokenizer()

# english_sent_model = Language(Vocab())
# english_sent_model.add_pipe('sentencizer')
# english_sent_model.add_pipe("set_custom_sentence_end_points", after='sentencizer')
# english_sent_model.max_length=135775100
