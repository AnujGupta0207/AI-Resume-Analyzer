import spacy
import re

nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    text = re.sub(r'\n', ' ', text)
    doc = nlp(text.lower())

    tokens = [
        token.lemma_
        for token in doc
        if not token.is_stop and not token.is_punct
    ]

    return " ".join(tokens)
