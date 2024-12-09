import spacy
import numpy as np

nlp = spacy.load('en_core_web_lg')

# search_doc = nlp("This was very strange argument between american and british person")
qq = "convalescent plasma is being investigated for the treatment of covid because there is no approved treatment for this disease and there is some information that suggests it might help some patients recover from covid."
main_doc = nlp(qq)

print(np.asarray(nlp(qq).vector).tolist()
      )

# print(np.asarray(np.zeros(300)).tolist())

print(np.nan_to_num([np.nan, np.nan, 56.4]))
