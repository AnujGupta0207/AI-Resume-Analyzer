import pandas as pd
import pickle
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report


# ==============================
# 1️⃣ Dataset Path (IMPORTANT)
# ==============================

DATASET_PATH = "dataset/resume_dataset.csv"

if not os.path.exists(DATASET_PATH):
    print("❌ Dataset file not found!")
    print("Expected path:", DATASET_PATH)
    exit()

df = pd.read_csv(DATASET_PATH)

print("✅ Dataset Loaded Successfully")
print("Total Records:", len(df))
print("Columns:", df.columns)


# ==============================
# 2️⃣ Data Cleaning
# ==============================

df = df.dropna()
df.columns = df.columns.str.strip()

if "resume_text" not in df.columns or "category" not in df.columns:
    print("❌ Dataset must contain 'resume_text' and 'category' columns")
    exit()

X = df["resume_text"]
y = df["category"]


# ==============================
# 3️⃣ TF-IDF Vectorizer
# ==============================

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=15000,
    ngram_range=(1, 2)
)

X_vectorized = vectorizer.fit_transform(X)


# ==============================
# 4️⃣ Train Test Split
# ==============================

X_train, X_test, y_train, y_test = train_test_split(
    X_vectorized,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# ==============================
# 5️⃣ Model Training
# ==============================

model = LinearSVC()
model.fit(X_train, y_train)


# ==============================
# 6️⃣ Evaluation
# ==============================

y_pred = model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)

print("\n🎯 Accuracy:", round(accuracy * 100, 2), "%")
print("\n📊 Classification Report:\n")
print(classification_report(y_test, y_pred))


# ==============================
# 7️⃣ Save Model & Vectorizer
# ==============================

with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("vectorizer.pkl", "wb") as f:
    pickle.dump(vectorizer, f)

print("\n🎉 Model and Vectorizer Saved Successfully!")