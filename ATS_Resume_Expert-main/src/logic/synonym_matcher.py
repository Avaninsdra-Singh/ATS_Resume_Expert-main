from nltk.stem import PorterStemmer

stemmer = PorterStemmer()

def stem_words(words):
    return [stemmer.stem(word.lower()) for word in words]

def match_with_synonyms(required, actual):
    stemmed_required = set(stem_words(required))
    stemmed_actual = set(stem_words(actual))
    return list(stemmed_required & stemmed_actual)
