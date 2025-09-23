# app.py
# Flask backend for Civic Issues AI Classification
# Categories: garbage, pothole, water leak

from flask import Flask, request, jsonify
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

app = Flask(__name__)

# ----------------------------
# Step 1: Simple AI model
# ----------------------------

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

# Convert text to numeric vectors
vectorizer = CountVectorizer()
X_train = vectorizer.fit_transform(train_texts)

# Train classifier
model = MultinomialNB()
model.fit(X_train, train_labels)

# Function to predict category
def predict_issue(text: str) -> str:
    X_test = vectorizer.transform([text])
    return model.predict(X_test)[0]

# ----------------------------
# Step 2: Flask API route
# ----------------------------

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()
    description = data.get("description", "")
    
    if not description:
        return jsonify({"error": "No description provided"}), 400
    
    category = predict_issue(description)
    return jsonify({"predicted_category": category})

# ----------------------------
# Step 3: Run the app
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)
