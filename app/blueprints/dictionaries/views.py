import time

from flask_restx import Resource
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services import DataPreprocessor
from app.services.auto_correction_engine.data_dictionary import DidYouMean
from app.services.config_constants import did_you_mean_flag
from custom_logging import logger
from . import dictionary_api
from . import document_input


@dictionary_api.route('/dictionary')
class DataDictionary(Resource):
    """class to create vocabulary dicitonary from the input corpus"""

    @dictionary_api.expect(document_input)
    # @token_required
    def post(self):
        """
        Post request for sending request to dicitonary API
        """
        try:

            logger.info("Parsing the document for dictionary creation")
            if len(dictionary_api.payload['projectid_to_process']) == 0:
                return {}
            if len(dictionary_api.payload['data']) == 0:
                return {}

            output_index = {}
            all_indexes = []
            # Save the input data in a file
            # json.dump(dictionary_api.payload, open('input_dictionary_api_data.json', 'w'))
            p_id_to_process = dictionary_api.payload['projectid_to_process']
            corpus = dictionary_api.payload['data']
            tic = time.time()
            for pid in p_id_to_process:
                logger.debug(f"[data dictionary] Running for project- {pid}")
                project_data = [i[j] for i in [records for records in corpus if str(records.get('project_id', '')) == str(pid)] for j in 
                                list(i.keys()) if j != 'project_id']

                chunk_size = 5000
                num_workers = 4  # Number of threads

                def process_chunk(chunk_data):
                    start_time = time.time()
                    clean_words_chunk = DataPreprocessor(chunk_data, flag_section_name=did_you_mean_flag)()
                    end_time = time.time()
                    time_taken = end_time - start_time
                    return clean_words_chunk, time_taken

                def process_in_chunks(project_data, chunk_size=5000, num_workers=4):
                    all_clean_words = []
                    num_chunks = len(project_data) // chunk_size + (1 if len(project_data) % chunk_size else 0)
                    with ThreadPoolExecutor(max_workers=num_workers) as executor:
                        future_to_chunk = {executor.submit(process_chunk, project_data[i * chunk_size:(i + 1) * chunk_size]): i for i in range(num_chunks)}
                        
                        for future in as_completed(future_to_chunk):
                            i = future_to_chunk[future]
                            try:
                                clean_words_chunk, time_taken = future.result()
                                logger.info(f"Time taken for chunk {i+1}: {time_taken:.2f} seconds")
                                all_clean_words.extend(clean_words_chunk)
                            except Exception as e:
                                logger.info(f"Chunk {i+1} generated an exception: {e}")
                    return all_clean_words
                
                if len(project_data) > chunk_size:
                    clean_words = process_in_chunks(project_data, chunk_size)
                else:
                    clean_words = DataPreprocessor(project_data, flag_section_name=did_you_mean_flag)()
                
                vocabulary_soundex = DidYouMean(pid).output(clean_words)
                all_indexes.extend(vocabulary_soundex)

            output_index['time_elapsed'] = time.time() - tic
            output_index['dictionary_index'] = all_indexes
            return output_index
        except Exception as e:
            logger.error('[Data Dictionary] view unable to create dicitionary ')
            logger.exception(e)

        # else:
        #     return {}

        # clean_text = DataPreprocessor(dictionary_api.payload, flag_section_name=did_you_mean_flag)()
        # output = DidYouMean().output(clean_text)
        # return project_data

        # print(api.payload)
        # keys = dictionary_api.payload.keys()
        # for key in keys:
        #     if api.payload[key] in ['', ' ', None]:
        #         logger.warning(f'{key} passed is blank')
        #
        # # if api.payload['document'] in ['', ' ', None]:
        # #     logger.warning('Document passed should be containing strings rather than blanks')
        # # document = DataPreprocessor(api.payload['document'], data_preprocessing_flag)()
        # document = DataPreprocessor('. '.join(list(api.payload.values())), data_preprocessing_flag)()
        #
        # logger.debug(f'Clean data {document}')
        #
        # result_spacy_ner = SpacyService.extract_entities(document)
        # logger.debug(f'{result_spacy_ner} -- OutputFormat')
        # # document = api.payload['document']
        # return result_spacy_ner[1]
