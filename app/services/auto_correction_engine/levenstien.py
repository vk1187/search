# from app.services.auto_correction_engine import AutoCorrectionVocab
# from services.auto_correction_engine.helpers import Helper
from app.services.config_constants import auto_correction_none_output
from app.services.config_constants import min_edit_distance_letters
from custom_logging import logger
from elastic_connection.elastic.helper import elastic_query_results


class Levenshtein:

    def __init__(self, word, index_name, project_id):
        """Initialization Constructor"""
        super().__init__()
        self.word = word
        self.index_name = index_name
        self.project_id = project_id  # self.vocab = search_results(index_name, project_query('data_dictionary',  # project_id)).keys()

        # logger.debug(f'Correction Check :  {Helper(word).run_correction_check}') if Helper(  # word).run_correction_check:  #  #     self.levenshtein_autocorrection = self.get_levenshtein_corrections()  # else:  #     self.levenshtein_autocorrection = self.word  # {  #     "candidate": self.word, "frequency": 1  # }

    def __call__(self):
        return self.get_levenshtein_candidates()

    def input_word(self, token=None):
        """Extracting Input from the class object or directly from input """
        if token is None:
            word = self.word
        else:
            word = token
        return word

    def delete_letter(self, token=None):
        """Creating Combinations of the token via deleting a character at each position"""
        word = self.input_word(token)
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)
                   if word[i:]]
        delete_l = [L + R[1:] for L, R in split_l if R]
        # logger.debug(f"input word {word}, \nsplit_l = {split_l}, \ndelete_l = {delete_l}")
        return delete_l

    def switch_letter(self, token=None):
        """Creating Combinations of the token via switching a character at each position"""
        word = self.input_word(token)
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)
                   if word[i:]]
        switch_l = [L + R[1] + R[0] + R[2:] for L, R in split_l if len(R) > 1]
        # logger.debug(f"Input word = {word} \nsplit_l = {split_l} \nswitch_l = {switch_l}")
        return switch_l

    def replace_letter(self, token=None):
        """Creating Combinations of the token via replacing a character at each position"""
        word = self.input_word(token)
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)
                   if word[i:]]
        replace_l = [
            l + c + r[1:] for l, r in split_l if r
            for c in min_edit_distance_letters
        ]
        replace_set = set([i for i in replace_l if i != word])
        replace_l = sorted(list(replace_set))
        # logger.debug(f"Input word = {word} \nsplit_l = {split_l} \nreplace_l {replace_l}")
        return replace_l

    def insert_letter(self, token=None):
        """Creating Combinations of the token via inserting a character at each position"""
        word = self.input_word(token)
        split_l = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        insert_l = [
            l + c + r for l, r in split_l for c in min_edit_distance_letters
        ]
        # logger.debug(f"Input word {word} \nsplit_l = {split_l} \ninsert_l = {insert_l}")
        return insert_l

    def edit_one_letter(self, token=None, allow_switches=True):
        """
        Input:
            word: the string/word for which we will generate all possible wordsthat are one edit away.
        Output:
            edit_one_set: a set of words with one possible edit.
        """
        word = self.input_word(token)
        edit_one_set = set()
        edit_one_set.update(self.insert_letter(word))
        edit_one_set.update(self.replace_letter(word))
        edit_one_set.update(self.delete_letter(word))
        if allow_switches:
            edit_one_set.update(self.switch_letter(word))
        # logger.debug(f'{edit_one_set}')
        return edit_one_set

    def edit_two_letters(self, token):
        """
        Input:
            word: the input string/word
        Output:
            edit_two_set: a set of strings with all possible two edits
        """
        word = self.input_word(token)
        edit_two_set = set()
        for token in self.edit_one_letter(word):
            edit_two_set.update(self.edit_one_letter(token))
        return edit_two_set

    def edit_three_letters(self, token):
        """
        Input:
            word: the input string/word
        Output:
            edit_two_set: a set of strings with all possible three edits
        """
        word = self.input_word(token)
        edit_three_set = set()
        for token in self.edit_two_letters(word):
            edit_three_set.update(self.edit_one_letter(token))
        return edit_three_set

    def get_suggestions(self, token=None):
        """
        Input Control to choose the suggestions on the basis of token length
        """
        # word = self.input_word(token)
        logger.debug(f'Input for suggestions ->{self.word}')
        if len(self.word) >= 5:
            logger.debug('Input length greater than 5')
            return list(  # Helper(word).vocab_check
                # or
                set(list(self.edit_letter_suggestions(edit_distance=2))))

        elif 3 < len(self.word) < 5:
            logger.debug('Input Length from than 3 to 5')
            return list(  # Helper(word).vocab_check
                # or
                self.edit_letter_suggestions(edit_distance=1))
        else:
            logger.debug('As is')
            return self.word.split()

    def get_levenshtein_candidates(self, token=None):
        """Returns candidates for the the token on the basis of levenstien distance"""

        logger.info(
            f'In function --> {self.get_levenshtein_candidates.__qualname__}')
        # word = self.input_word(token)
        suggestions = self.get_suggestions()
        logger.debug(
            f'{self.get_levenshtein_candidates.__qualname__} any 10 suggestions are ->{suggestions[:10]}'
        )
        return suggestions

    def edit_letter_suggestions(self, edit_distance=1, token=None):
        """Returns candidates on the basis of levenstien distance"""

        # word = self.input_word(token)
        logger.debug(f'edit distance : {edit_distance}')

        # logger.debug(f'self.edit_two_letters(self.word).intersection(set(self.vocab)):'
        #              f'{self.edit_two_letters(self.word).intersection(set(self.vocab))}')
        try:
            if edit_distance == 1:
                # logger.debug(f'self.edit_one_letter : {self.edit_one_letter(self.word)}')
                # logger.debug(f'self.edit_one_letter(self.word).intersection(set(self.vocab)):'
                #              f'{self.edit_one_letter(self.word).intersection(set(self.vocab))}')
                # outputs = self.edit_one_letter(self.word).intersection(set(self.vocab))
                outputs = list(
                    elastic_query_results(
                        index_name=self.index_name,
                        vocab_type='data_dictionary',
                        project_id=self.project_id,
                        candidate_key=list(
                            self.edit_one_letter(self.word.lower())),
                        property_attribute='probabilities').keys())
            if edit_distance == 2:
                # outputs = self.edit_two_letters(self.word).intersection(set(self.vocab))
                outputs = list(
                    elastic_query_results(
                        index_name=self.index_name,
                        vocab_type='data_dictionary',
                        project_id=self.project_id,
                        candidate_key=list(
                            self.edit_two_letters(self.word.lower())),
                        property_attribute='probabilities').keys()
                )  # logger.debug(f'self.edit_two_letters(self.word).intersection(set(self.vocab)):'  #              f'{self.edit_two_letters(self.word).intersection(set(self.vocab))}')
            if edit_distance == 3:
                outputs = list(
                    elastic_query_results(
                        index_name=self.index_name,
                        vocab_type='data_dictionary',
                        project_id=self.project_id,
                        candidate_key=list(self.edit_three_letters(self.word)),
                        property_attribute='probabilities').keys()
                )  # outputs = self.edit_three_letters(self.word).intersection(set(self.vocab))
            # else:
            #     raise ValueError("Edit distance>3 not allowed")

            if outputs is None or outputs == [
                    None
            ] or outputs == auto_correction_none_output:
                return []
            return [i.lower() for i in outputs if i[0] == self.word.lower()[0]]
        except ValueError as ve:
            logger.error(ve)
            logger.exception(ve)
