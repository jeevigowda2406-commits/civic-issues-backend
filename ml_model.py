# ml_model.py
# Simple AI text classification for civic issues
# Categories: garbage, pothole, water leak

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# Sample training data
train_texts = [
    "garbage on the street", "trash dumped", "overflowing dustbin",
    "big pothole on road", "broken road", "damaged street surface",
    "water pipe leaking", "drainage water leak", "sewage overflow"
]
train_labels = [
    "garbage", "garbage", "garbage",
    "pothole", "pothole", "pothole",
    "water leak", "water leak", "water leak"
]

# Convert text to vectors
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(train_texts)

# Train classifier
model = MultinomialNB()
model.fit(X_train, train_labels)

def predict_issue(text: str) -> str:
    """Predict issue category from user description"""
    X_test = vectorizer.transform([text])
    return model.predict(X_test)[0]
