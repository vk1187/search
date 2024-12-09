from pydantic import BaseSettings


class Settings(BaseSettings):
    # config = open("configSetting.json").read()
    # objConfig=json.load(config)
    # if ex objConfig)
    # # Universal Sentence Encoder Tf Hub url
    MODEL_URL: str = "https://tfhub.dev/google/universal-sentence-encoder/4"

    # spaCy Model
    SPACY_MODEL: str = 'en_core_web_sm'

    # Elasticsearch ip and port
    ELASTIC_IP: str = "localhost"
    ELASTIC_PORT: int = 9200

    # Min score for the match
    SEARCH_THRESH: float = 1.2

    # Reindexing Flag
    REINDEX_FLAG: bool = True

    # Index Name
    INDEX_NAME: str = "covid-qa"


settings = Settings()
