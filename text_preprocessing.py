#Preprocessing Module
#Prepares user submitted text for processing by removing any non-relevant characters. 

import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

class TextPreprocessor:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
    def clean_text(self, text):
        # Remove HTML tags, special characters, etc.
        text = re.sub(r'<[^>]+>', ' ', text)  
        text = re.sub(r'\s+', ' ', text).strip()  # Remove extra whitespaces
        cleaned_text = text.lower() 
        return cleaned_text

    def tokenize(self, text):
        tokens = word_tokenize(text)
        lemmatized_tokens = [self.lemmatizer.lemmatize(token) for token in tokens if token not in self.stop_words and token.isalpha()]
        return lemmatized_tokens
    
    def preprocess(self, text):
        cleaned_text = self.clean_text(text)
        tokens = self.tokenize(cleaned_text)
        return ' '.join(tokens)

