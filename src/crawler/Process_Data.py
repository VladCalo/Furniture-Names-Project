import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Extraction import Extraction

class Process_Data(Extraction):
    def __init__(self):
        super().__init__(headless=True)
        
    def get_data(self):
        raw_data, h_elements = super().get_data(iterations=3)
        super().close()
        return raw_data, h_elements
        
    # no Stemming or Lemmatization as it will modify the original furniture title
    def preprocess(self, text):
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_tokens = [word for word in tokens if word.lower() not in stop_words]

        # Retain numbers using regular expression
        filtered_tokens_with_numbers = [word for word in filtered_tokens if re.match(r'^-?\d+(?:\.\d+)?$', word) or word.isdigit()]
        
        # Remove newline characters
        filtered_tokens_with_numbers = [word for word in filtered_tokens_with_numbers if word != '\n']

        # Remove specific punctuation
        filtered_tokens_with_numbers = [word for word in filtered_tokens_with_numbers if re.match(r'\b(?:\w|-)+\b', word)]
        
        preprocessed_text = ' '.join(filtered_tokens)
        return preprocessed_text  
    
    def preprocess_raw_data(self, text_list):
        process_data = []
        for text in text_list:
            preprocess_text = self.preprocess(text)
            process_data.append(preprocess_text)
        return process_data
    
    def preprocess_h_data(self):
        _, list_of_tuples = self.get_data()
        process_data = []
        for t in list_of_tuples:
            l = t[1]
            for text in l:
                preprocess_text = self.preprocess(text)
                process_data.append(preprocess_text)
        return process_data

p = Process_Data()
data = p.preprocess_h_data()
print("\n################ DATA #################")
print(data)

