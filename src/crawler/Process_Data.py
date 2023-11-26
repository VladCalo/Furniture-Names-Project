import re
import spacy
from spacy.matcher import Matcher
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Extraction import Extraction
import nltk
import subprocess
import pandas as pd
from nltk import pos_tag
from nltk.corpus import wordnet

class Process_Data(Extraction):
    def __init__(self):
        super().__init__(headless=True)
        
    def get_data(self):
        raw_data, h_elements = super().get_data()
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
        
    def preprocess_raw_data(self):
        print("################################## PREPROCESSING RAW DATA #################################")
        raw_data, _ = self.get_data()
        text_list = [data[1] for data in raw_data]
        process_data = []
        for text in text_list:
            preprocess_text = self.preprocess(text)
            process_data.append(preprocess_text)
        return process_data
    
    def preprocess_h_data(self):
        _, list_of_tuples = self.get_data()
        print("################################## PREPROCESSING HEADER DATA #################################")
        process_data = []
        for t in list_of_tuples:
            l = t[1]
            for text in l:
                preprocess_text = self.preprocess(text)
                process_data.append(preprocess_text)
        return process_data

    def contains_verb_adverb_pronoun_in_context(self, sentence):

        def check_len(s):
            tokens = nltk.word_tokenize(s)
            tokens = [word for word in tokens if word.isalpha()]
            return len(tokens) <= 2
        
        if check_len(sentence):
            return True
        
        def has_furniture_name(s):
            furniture_list = [
                "chair", "table", "desk", "stool", "bench", "shelf", "cabinet", "bed", 
                "sofa", "ottoman", "dresser", "wardrobe", "nightstand", "sideboard", 
                "bookcase", "buffet", "etagere", "chaise", "barstool", 
                "couch", "mirror", "lamp", "candlestand", "drawer", "armoire", 
                "vanity", "bookshelf", "cupboard", "recliner", "stand",
                "settee", "rockingchair", "futon", "chifforobe", "daybed", 
                "tuffet",  "bookstand", "bedstead", "mattress", "coffeetable", "armchair", 
                "ottoman", "bench", "sofa",  "recliner" "rug", "mat", "carpet"
            ]
            tokens = nltk.word_tokenize(s)
            for token in tokens:
                if token.lower() in furniture_list:
                    return True
            
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(sentence)

        # Check if there is at least one token with a part-of-speech tag of "VERB", "ADV", or "PRON"
        if any(token.pos_ in ["VERB", "ADV", "PRON"] for token in doc):
            if not has_furniture_name(sentence):
                return True

        # Check if there is at least one token with a head (governing word) that is a "VERB", "ADV", or "PRON"
        if any(token.head.pos_ in ["VERB", "ADV", "PRON"] for token in doc):
            if not has_furniture_name(sentence):
                return True

        # Check if there is at least one token with a dependency relation of "amod" (adjectival modifier) that is a "VERB", "ADV", or "PRON"
        if any(token.dep_ == "amod" and token.head.pos_ in ["VERB", "ADV", "PRON"] for token in doc):
            if not has_furniture_name(sentence):
                return True

        # Check if there is at least one token with a child that is a "VERB", "ADV", or "PRON"
        if any(child.pos_ in ["VERB", "ADV", "PRON"] for token in doc for child in token.children):
            if not has_furniture_name(sentence):
                return True

        # Check if there is at least one token with a sibling that is a "VERB", "ADV", or "PRON"
        if any(sibling.pos_ in ["VERB", "ADV", "PRON"] for token in doc for sibling in token.head.children if sibling != token):
            if not has_furniture_name(sentence):
                return True

        return False

    def heuristic_matching(self):
        filtered_data = []
        string_list = self.preprocess_h_data()
        print("################################## STARTED HEURISTING MATCHING #################################")
        for string in string_list:      
            if self.contains_verb_adverb_pronoun_in_context(string):
                continue
            else:
                filtered_data.append(string)
        return filtered_data
        
    def label_data(self):
        result = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        repo_dir = result.stdout.strip()
        output_csv = repo_dir + "/data/traning_data.csv"
        
        data = self.heuristic_matching()
        print("################################## LABELING DATA #################################")
        df = pd.DataFrame({"Text": data})
        df['Label'] = "PRODUCT"
        df.to_csv(output_csv, index=False)
        



