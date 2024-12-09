import datetime

from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.char_classes import CONCAT_QUOTES, LIST_ELLIPSES, LIST_ICONS
from spacy.language import Language
from spacy.tokens import Token
from spacy.util import compile_infix_regex
from load_parameters import get_parameters



# from app.services.config_constants import punctuation_splitter_for_sentence_segmentation


def custom_infix(spacy_model):
    """removed hyphen tokenization process from spacy by creating custom tokenizer"""
    tokenizer_infix = (
        LIST_ELLIPSES + LIST_ICONS + [
            r"(?<=[0-9])[+\-\*^](?=[0-9-])",
            r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
                al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES),
            r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
            #         r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
            r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
        ])
    infix_re = compile_infix_regex(tokenizer_infix)
    spacy_model.tokenizer.infix_finditer = infix_re.finditer
    return spacy_model


# ADD A NEW RULE TO THE PIPELINE
@Language.component("set_custom_sentence_end_points")
def set_custom_sentence_end_points(doc):
    parameters = get_parameters()
    punctuation_splitter_for_sentence_segmentation = parameters.get("DEFAULT","punctuation_splitter_for_sentence_segmentation")
    for token in doc[:-1]:
        if token.text in punctuation_splitter_for_sentence_segmentation:
            doc[token.i + 1].is_sent_start = True
        if token.text[-1] in punctuation_splitter_for_sentence_segmentation:
            doc[token.i].is_sent_start = None
    return doc


def validate_dmy(date_text):
    for sep in ['.', '/', '-']:
        try:
            datetime.datetime.strptime(date_text,
                                       '%d' + sep + '%m' + sep + '%Y')
            return True
        except ValueError:
            continue
    return False


def validate_ymd(date_text):
    for sep in ['.', '/', '-']:
        try:
            sepreated_data = date_text.split(sep)
            if len(sepreated_data) > 1:
                sepreated_data[1] = sepreated_data[1].rjust(2, '0')
            final_data = sep.join(sepreated_data)
            datetime.datetime.strptime(final_data,
                                       '%Y' + sep + '%m' + sep + '%d')
            return True
        except ValueError:
            continue
    return validate_dmy(date_text)


# Define the getter function
def get_has_number(token):
    """returns True if there is date or some specified special properties in tokens as mentioned in last else
    condition """
    if token.ent_type_ == 'DATE':
        return True
    elif validate_ymd(token.text):
        return True
    else:
        # Return if any of the tokens in the doc return True for token.like_num
        return token.like_num | token.like_email | token.is_currency | token.is_digit | token.like_url | token.is_stop | token.is_punct

    # Register the Doc property extension "has_number" with the getter get_has_number


Token.set_extension("has_number", getter=get_has_number)

# # Process the text and check the custom has_number attribute
# doc = nlp("The museum closed for five years in . I am going to Chennai!! what i your number 50%")
# for i in doc:
#     print("has_number:", i.text, ':', i._.has_number)
