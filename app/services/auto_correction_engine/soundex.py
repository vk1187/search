# from app.services.auto_correction_engine import AutoCorrectionVocab
import string

from app.services.config_constants import auto_correction_none_output
from custom_logging import logger
from elastic_connection.elastic.helper import elastic_query_results

puncts = string.punctuation


class Soundex():

    def __init__(self, word, index_name, project_id):
        """Initialization Constructor"""
        super().__init__()
        self.word = word
        self.index_name = index_name
        self.project_id = project_id
        # self.soundex_hash = self.soundex_code()

    def soundex_code(self):
        """return soundex code for the given input word"""
        query = self.word.lower()
        if query.isnumeric() or sum(
            [1 for i in list(puncts) if query.find(i) != -1]) > 0:
            return None
        letters = [char for char in query if char.isalpha()]

        # Step 1: Save the first letter. Remove all occurrences of a, e, i, o, u, y, h, w.

        # If query contains only 1 letter, return query+"000" (Refer step 5)
        if len(query) == 1:
            return query + "000"

        to_remove = ('a', 'e', 'i', 'o', 'u', 'y', 'h', 'w')

        first_letter = letters[0]
        letters = letters[1:]
        letters = [char for char in letters if char not in to_remove]

        if len(letters) == 0:
            return first_letter + "000"

        # Step 2: Replace all consonants (include the first letter) with digits according to rules

        to_replace = {
            ('b', 'f', 'p', 'v'): 1,
            ('c', 'g', 'j', 'k', 'q', 's', 'x', 'z'): 2,
            ('d', 't'): 3,
            ('l', ): 4,
            ('m', 'n'): 5,
            ('r', ): 6
        }

        first_letter = [
            value if first_letter else first_letter
            for group, value in to_replace.items() if first_letter in group
        ]
        letters = [
            value if char else char for char in letters
            for group, value in to_replace.items() if char in group
        ]

        # Step 3: Replace all adjacent same digits with one digit.
        letters = [
            char for ind, char in enumerate(letters)
            if (ind == len(letters) -
                1 or (ind + 1 < len(letters) and char != letters[ind + 1]))
        ]

        # Step 4: If the saved letter’s digit is the same the resulting first digit, remove the digit (keep the letter)
        if first_letter == letters[0]:
            letters[0] = query[0]
        else:
            letters.insert(0, query[0])

        # Step 5: Append 3 zeros if result contains less than 3 digits.
        # Remove all except first letter and 3 digits after it.

        first_letter = letters[0]
        letters = letters[1:]

        letters = [char for char in letters if isinstance(char, int)][0:3]

        while len(letters) < 3:
            letters.append(0)

        letters.insert(0, first_letter)

        string = "".join([str(letter) for letter in letters])

        return string

    def __call__(self):
        return self.get_soundex_candidates()

    def get_soundex_candidates(self):
        """return the candidates corresponding the soundex code from elastic"""
        soundex_hash = self.soundex_code()
        suggestions = elastic_query_results(
            index_name=self.index_name,
            vocab_type='soundex',
            project_id=self.project_id,
            candidate_key=' ' if soundex_hash is None else soundex_hash,
            property_attribute='values')

        # print(suggestions)
        # print(auto_correction_none_output,auto_correction_none_output==suggestions)
        if suggestions == auto_correction_none_output:
            return suggestions[None]
        else:
            logger.debug(
                f"{self.get_soundex_candidates.__qualname__}--> any 10 suggestions = {list(suggestions.values())[:10]}"
            )
            return suggestions[soundex_hash]

    #
    # def get_soundex_candidates(self):
    #     suggestions = self.vocabulary_soundex_codes.get(self.soundex_code(), None)
    #     logger.debug(f"{self.get_soundex_candidates.__qualname__}--> any 10 suggestions = {suggestions[:10]}")
    #     return suggestions
