from sklearn.metrics.pairwise import cosine_similarity
import pickle

model = pickle.load(open("model/vectorizer.pkl", "rb"))

def semantic_match(resume_text, job_desc):
    vectors = model.transform([resume_text, job_desc])
    similarity = cosine_similarity(vectors[0:1], vectors[1:2])
    return round(similarity[0][0] * 100, 2)

