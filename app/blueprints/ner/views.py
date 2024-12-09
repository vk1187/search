import itertools
import time
from collections import defaultdict

import numpy as np
# from flask_restx import Api
from flask_restx import Resource
import os
from datetime import datetime
from app.services.config_constants import data_preprocessing_flag, entity_ruler_collection_name
from app.services.ner_engine.helper import ner_output_format,reformatting_input
from app.services.ner_engine.ml_model.spacy import SpacyService
from app.services.ner_engine.ml_model.spacy.manual_entity import get_patterns_and_pattern_ids, \
    remove_patterns_from_ruler, remove_patterns_from_ruler_basic
from app.services.utils import DataPreprocessor
from app.services.utils import error_message
from custom_logging import logger
# from ...services.ner_engine.utils import output_format
from . import api, document_input, manual_entity_input
# from . import bp
from ...services.ner_engine.utils import cleaning_output
import truecase
from load_parameters import get_parameters
import re
from utils.check_language import english_language_present
import json

@api.route('/return_entities')
class NER(Resource):
    """Class to return entities present in the given input"""

    @api.expect(document_input)
    # @token_required
    def post(self):
        """
        Post request to return entities present in the given input
        :param data: [{"id":1,"text":"samople data"}]
        :param client_id:
        return entities
        """
        try:

            logger.info("Parsing the document for entity recognition")
            parameters = get_parameters()
            truecase_flag = parameters.get("ner", "truecase_flag")
            data_attributes = parameters.get("ner", "data_attributes")
            # print(api.payload)
            # print
            tic = time.time()
            if api.payload in [None, [], '', ' ']:
                logger.warning(f'Please pass input parameters for [NER]')
                return {'entities': None, 'time': time.time() - tic}

                # keys = api.payload.keys()
            # for key in keys:
            #     if api.payload[key] in ['', ' ', None]:
            #         logger.warning(f'{key} passed is blank')
            #         break

            # if api.payload['document'] in ['', ' ', None]:
            #     logger.warning('Document passed should be containing strings rather than blanks')
            # document = DataPreprocessor(api.payload['document'], data_preprocessing_flag)()
            ner_file_name = os.path.join("input_files_ner",'ner_api_input_'+str(datetime.now().strftime("%d_%m_%Y_%H_%M_%S")) +'.json')
            os.makedirs(os.path.dirname(ner_file_name),exist_ok=True)
            with open(ner_file_name,'w',encoding='utf8') as f:
                json.dump(api.payload,f)
            client_id = api.payload['client_id']
            data = api.payload['data'].copy()

            combined_data = reformatting_input(data,data_attributes,truecase_flag)

            # for i in data:
            #     for j in i:
            #         if j != 'id':
            #             # if i[j]!="" and not english_language_present(i[j]):
            #             #     i[j]=""



            #             if truecase_flag and (j in data_attributes):

            #                 cased_text = truecase.get_true_case(
            #                     "," +
            #                     i[j])[1:].strip() if "&" not in i[j] else i[j]
            #                 cased_text = re.sub("(\-*\d*\.\d+\%*)|\d{4}\,*|\d+%|(ERROR:#N/A)|\-+\d+|(\.\d+E\-)"," ", cased_text)
            #                 cased_text = re.sub("(•)"," ", cased_text)
                            
            #                 i[j] = [cased_text, {'id': i['id']}]
            #             else:
            #                 i[j] = [i[j], {'id': i['id']}]
            #     i.pop('id')

            # combined_data = [
            #     list(i.values()[0])
            #     if isinstance(i.values(), list) else list(i.values())
            #     for i in data
            # ]
            final_data = list(itertools.chain(*combined_data))

            for i in range(len(final_data)):
                try:
                    final_data[i][0] = re.sub(r"\s*['’]\s*", "'", str(final_data[i][0]))
                    final_data[i][0] = final_data[i][0].encode("ascii", "ignore").decode('utf8')
                except:
                    final_data[i][0] = ""
                    logger.warning(f'Summary is null for the document')

            final_data_array = np.array(final_data)
            final_data_array[:, 0] = [
                DataPreprocessor(i[0], data_preprocessing_flag)()
                for i in final_data
            ]
            final_data = [tuple(i) for i in final_data_array]
            del final_data_array

            # docs = [i[0] for i in final_data]
            # indices = [i[1] for i in final_data]

            # document = DataPreprocessor('. '.join(list(api.payload.values())), data_preprocessing_flag)()

            # logger.debug(f'Clean data -----> {document}')
            temp_dict = defaultdict()
            # print(final_data)
            # spacy_model
            disable_clients = [
                str(i) for i in SpacyService.get_ruler_names()
                if i != client_id
            ]

            logger.info(f" Number of pages to process {len(final_data)}")
            batch_size = 100
            try:
                for batch in spacy.util.minibatch(final_data, size=batch_size):
                    for doc, context in SpacyService.model().pipe(
                            batch, as_tuples=True, disable=disable_clients):

                        if context['id'] not in temp_dict:
                            entities = defaultdict(set)
                            for ent in doc.ents:
                                entities[ent.label_].add(ent.text.title())
                            temp_dict[context['id']] = entities
                        else:
                            for ent in doc.ents:
                                temp_dict[context['id']][ent.label_].add(
                                    ent.text.title())
                    # print(temp_dict)
            except Exception as exception_all:
                logger.error(exception_all)
                logger.exception(exception_all)
                return {'entities': None, 'time': time.time() - tic}
            del doc, context, entities
            result = {
                doc_id: cleaning_output(temp_dict[doc_id])
                for doc_id in temp_dict
            }
            del temp_dict

            # result_spacy_ner = SpacyService.extract_entities(document)
            # logger.debug(f'{result_spacy_ner} -- OutputFormat')
            # document = api.payload['document']
            # return result_spacy_ner[1]
            location_count = 0
            org_count = 0

            # Loop through each entity to count "Location" and "Organization"
            for entity in result.values():
                location_count += len(entity.get("Location", []))
                org_count += len(entity.get("Organization", []))
            logger.info(f"Printing Result - Total Locations : {location_count}, Total Organizations : {org_count}, time: {time.time() - tic}")
            return ner_output_format(result, tic=tic)
        except Exception as exc:
            with open('ner_input_api_exception.json','w',encoding='utf8') as f:
                json.dump(api.payload,f)
            logger.error('[NER] View is not able to process the input')
            logger.exception(f'{exc}')


@api.route('/manual_entities')
class ManualEntity(Resource):
    """Class to add manual entities from user feedback"""

    @api.expect(manual_entity_input)
    # @token_required
    def post(self):
        """ Addition of Manual Entities in spacy model based on feedback given by user"""
        try:

            logger.info(f"Adding Custom Entities to the model")
            parameters = get_parameters()
            # print(api.payload)
            # print
            tic = time.time()
            if api.payload in [None, [], '', ' ']:
                logger.warning(
                    f'Please pass input parameters(client,project_id) for [NER]'
                )
                return error_message(tic, " No input is passed to the API")

            project_id = api.payload.get('project_id', None)
            client_id = api.payload.get('client_id', None)
            data = api.payload.get('data', [])
            on_the_fly_flag = api.payload.get('on_the_fly_flag', 0)
            delete_pattern_ids = api.payload.get('delete_pattern_ids', [])
            main_database_name = parameters.get("DEFAULT",
                                                "main_database_name")

            if len(data):

                input_label = [i['entity'] for i in data]
                input_pattern = [i['pattern'] for i in data]
                input_pattern_id = [i['pattern_id'] for i in data]
                if (len(input_label) != len(input_pattern)) or (
                        len(input_label) != len(input_pattern_id)):
                    return error_message(tic, "Mismatch length in input data")

                try:
                    pattern, pattern_ids = get_patterns_and_pattern_ids(
                        on_the_fly_flag=on_the_fly_flag,
                        main_database_name=main_database_name,
                        entity_ruler_collection_name=
                        entity_ruler_collection_name,
                        client_id=client_id,
                        project_id=None,
                        input_label=input_label,
                        input_pattern=input_pattern,
                        input_pattern_id=input_pattern_id)
                    # ruler = SpacyService.get_ruler()
                    if len(pattern) and len(pattern_ids):
                        remove_patterns_from_ruler_basic(SpacyService,
                                                   client_id=client_id,
                                                   pattern_ids=pattern_ids)
                        SpacyService.add_ruler(client_id=client_id,
                                               patterns=pattern)
                        logger.info(
                            f'Patterns are initialized to the spacy model')
                    else:
                        logger.info(
                            f'No patterns are added to the spacy model')
                        return error_message(
                            tic, "Check database input and output")
                        # {'status': False, 'time': time.time() - tic,'error':"Check database input and output"}

                except Exception as e:
                    logger.error(e)
                    logger.exception(e)
                    return error_message(tic, str(e))

            if (len(delete_pattern_ids)):
                try:
                    remove_patterns_from_ruler(SpacyService,
                                               client_id=client_id,
                                               pattern_ids=delete_pattern_ids)
                except Exception as e:
                    logger.error(
                        f'[Mannual Entity] Unable to delete the pattern_id {delete_pattern_ids}'
                    )
                    logger.error(e)
                    logger.exception(e)
                    return error_message(tic, str(e))
            return {'status': True, 'time': time.time() - tic}
            # return ner_output_format(result, tic=tic)
        except Exception as e:
            logger.error(
                '[Mannual Entity Creation] Entity Ruler is not able to add the input'
            )
            logger.exception(f'{e}')
            return error_message(tic, str(e))


# @api.route('/return_entities_and_suggestions(Not Working)')
# class NER(Resource):
#     @api.expect(document_input)
#     def post(self):
#         logger.info(f"Parsing the document for entity recognition and finding autocompletion suggestions'")
#         logger.debug(api.payload['document'])
#         if api.payload['document'] in ['', ' ', None]:
#             logger.warning('Document passed should be containing strings rather than blanks')
#         document = DataPreprocessor(api.payload['document'], data_preprocessing_flag)()
#         logger.debug(f'Clean data {document}')
#         result_spacy_ner = SpacyService.extract_entities(document)
#         logger.debug(f'{result_spacy_ner} -- OutputFormat')
#         suggestions_gram = AutoComplete.extract_autocomplete_suggestions_ngram(api.payload['document'])
#         suggestions_phraser = AutoComplete.extract_autocomplete_suggestions_phrases(api.payload['document'])
#         return {
#             'ner': result_spacy_ner[1],
#             'grams': suggestions_gram,
#             "phraser": suggestions_phraser}
