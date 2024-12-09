import spacy_streamlit

models = ["en_core_web_sm", "en_core_web_md","en_core_web_lg"]
default_text = "Sundar Pichai is the CEO of Google."
spacy_streamlit.visualize(models, default_text)