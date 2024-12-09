import time
import re
import truecase
from app.services.config_constants import NER_VALID_OUTPUT_ENTITIES, MAP_SPACY_ENTITIES


def ner_output_format(entities, tic):
    """ Added Time value to tell the time of producing output and does not
    account time for loading of model as default models was loaded at the startup """
    final_ = {'entities': entities, 'time': time.time() - tic}
    return final_


def ner_output_converter(entity_op):
    """Converts output from spacy and transformer models to unified format"""

    output_f = {entity_label: [] for entity_label in NER_VALID_OUTPUT_ENTITIES}
    # output_f = {
    #     "Location": [],
    #     "Person": [],
    #     "Organization": [],
    #     "Percentage": [],
    #     "Date": [],
    #     "Cardinal": [],
    # }
    # {
    #     "LOC": "Location",
    #     "GPE": "Location",
    #     "Location": "Location",
    #     "ORG": "Organization",
    #     "Organization": "Organization"
    # }
    for i in entity_op:
        if MAP_SPACY_ENTITIES.get(i, -1) != -1:
            output_f[MAP_SPACY_ENTITIES[i]].extend(entity_op[i])
        # if i in ['LOC', 'GPE', "Location"]:  # , 'NORP'
        #     output_f['Location'].extend(entity_op[i])
        # # if i in ['PER', 'Person', 'PERSON']:
        # #     output_f['Person'].extend(entity_op[i])
        # # if i in ['PERCENT']:
        # #     output_f['Percentage'].extend(entity_op[i])
        # # if i in ['DATE']:
        # #     output_f['Date'].extend(entity_op[i])
        # if i in ['ORG', "Organization", "Organisation"]:
        #     output_f['Organization'].extend(
        #         entity_op[i]
        #     )  # if i in ['Cardinal', 'CARDINAL']:  #     output_f['Cardinal'].extend(entity_op[i])

    return output_f


def reformatting_input(data,data_attributes,truecase_flag):
    """Reformatting the input"""
    for i in data:
        for j in i:
            if j != 'id':
                # if i[j]!="" and not english_language_present(i[j]):
                #     i[j]=""



                if truecase_flag and (j in data_attributes):

                    cased_text = truecase.get_true_case(
                        "," +
                        i[j])[1:].strip() if "&" not in i[j] else i[j]
                    cased_text = re.sub("(\-*\d*\.\d+\%*)|\d{4}\,*|\d+%|(ERROR:#N/A)|\-+\d+|(\.\d+E\-)"," ", cased_text)
                    cased_text = re.sub("(•)"," ", cased_text)
                    
                    i[j] = [cased_text, {'id': i['id']}]
                else:
                    i[j] = [i[j], {'id': i['id']}]
        i.pop('id')
    
    combined_data = []
    for doc in data:
        combined_doc_data = []
        for key, value in doc.items():
            if key == 'DocumentPage':
                for page in value[0]:
                    combined_doc_data.append([page['text'], {'id': doc['SUMMARY'][1]['id']}])
            else:
                combined_doc_data.append([value[0], value[1]])
        combined_data.append(combined_doc_data)

    # combined_data = [
    #             list(i.values()[0])
    #             if isinstance(i.values(), list) else list(i.values())
    #             for i in data
    #         ]

    return combined_data
