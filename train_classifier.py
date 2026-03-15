import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import os

# -------- LOAD DATASET FROM dataset FOLDER -------- #

DATA_PATH = "dataset/resume_dataset.csv"

if not os.path.exists(DATA_PATH):
    print("❌ Dataset not found at:", DATA_PATH)
    exit()

df = pd.read_csv(DATA_PATH)

print("✅ Dataset Loaded")
print("Total Records:", len(df))

X = df["resume_text"]
y = df["category"]

# -------- VECTORIZE -------- #

vectorizer = TfidfVectorizer(stop_words="english")
X_vectorized = vectorizer.fit_transform(X)

# -------- TRAIN MODEL -------- #

model = LogisticRegression(max_iter=300)
model.fit(X_vectorized, y)

# -------- SAVE MODEL INSIDE model FOLDER -------- #

if not os.path.exists("model"):
    os.makedirs("model")

pickle.dump(model, open("model/resume_classifier.pkl", "wb"))
pickle.dump(vectorizer, open("model/vectorizer.pkl", "wb"))

print("🎉 Category Classifier Trained Successfully")
print("Model saved inside /model folder")