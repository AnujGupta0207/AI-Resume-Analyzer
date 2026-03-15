import pickle

model = pickle.load(open("model/resume_classifier.pkl", "rb"))
vectorizer = pickle.load(open("model/vectorizer.pkl", "rb"))

def predict_category(resume_text):
    vector = vectorizer.transform([resume_text])
    prediction = model.predict(vector)
    return prediction[0]
