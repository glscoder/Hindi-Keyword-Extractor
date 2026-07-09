from preprocess import preprocess_text
from tfidf_model import extract_tfidf_keywords

with open("data/sample_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

clean_text = preprocess_text(text)

print("\nCleaned Text:")
print(clean_text)

print("\nTF-IDF Keywords:")
print(extract_tfidf_keywords(clean_text))
