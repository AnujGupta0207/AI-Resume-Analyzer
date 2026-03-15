import re
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- LOAD TRAINED ML MODEL ---------------- #

classifier = pickle.load(open("model/resume_classifier.pkl", "rb"))
vectorizer_model = pickle.load(open("model/vectorizer.pkl", "rb"))

# ---------------- SKILL DATABASE ---------------- #

SKILLS_DB = [
    "python", "java", "c++", "javascript",
    "django", "flask", "spring boot", "react",
    "machine learning", "deep learning", "nlp",
    "data science", "sql", "mongodb", "postgresql",
    "aws", "docker", "kubernetes", "microservices",
    "rest api", "system design", "cloud computing"
]

# ---------------- SKILL EXTRACTION ---------------- #

def extract_skills(text):
    text_lower = text.lower()
    return [skill for skill in SKILLS_DB if skill in text_lower]

# ---------------- EXPERIENCE ---------------- #

def extract_experience(text):
    match = re.search(r'(\d+)\+?\s*(years|yrs)', text.lower())
    if match:
        return int(match.group(1))
    return 0

# ---------------- EDUCATION ---------------- #

def extract_education_score(text):
    text = text.lower()
    if "phd" in text:
        return 10
    elif "master" in text or "m.tech" in text:
        return 8
    elif "bachelor" in text or "b.tech" in text:
        return 6
    else:
        return 4

# ---------------- GRADE ---------------- #

def calculate_grade(score):
    if score >= 85:
        return "A+"
    elif score >= 75:
        return "A"
    elif score >= 65:
        return "B"
    elif score >= 55:
        return "C"
    else:
        return "D"

# ---------------- MAIN SCORING ---------------- #

def score_resume(resume_text, job_description):

    resume_text_lower = resume_text.lower()

    # ---------- 1️⃣ ML CATEGORY PREDICTION ---------- #
    resume_vector = vectorizer_model.transform([resume_text])
    predicted_category = classifier.predict(resume_vector)[0]

    job_categories = [
        "Data Science",
        "Web Development",
        "Cloud Computing",
        "Cyber Security",
        "Software Engineering",
        "UI UX"
    ]

    job_category_detected = None
    for cat in job_categories:
        if cat.lower() in job_description.lower():
            job_category_detected = cat
            break

    if job_category_detected:
        if predicted_category == job_category_detected:
            category_score = 15
        else:
            category_score = -5
    else:
        category_score = 0

    # ---------- 2️⃣ SKILL MATCH (25 points) ---------- #
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_description)

    matched_skills = set(resume_skills).intersection(set(job_skills))
    skill_score = min(len(matched_skills) * 5, 25)

    # ---------- 3️⃣ SEMANTIC SIMILARITY (25 points) ---------- #
    vectorizer = TfidfVectorizer(stop_words="english")
    vectors = vectorizer.fit_transform([resume_text, job_description])
    similarity = cosine_similarity(vectors[0], vectors[1])[0][0]
    similarity_score = similarity * 25

    # ---------- 4️⃣ EXPERIENCE (20 points) ---------- #
    experience = extract_experience(resume_text)
    experience_score = min(experience * 4, 20)

    # ---------- 5️⃣ EDUCATION (10 points) ---------- #
    education_score = extract_education_score(resume_text)

    # ---------- 6️⃣ PROJECT KEYWORDS (5 points) ---------- #
    project_keywords = ["project", "developed", "implemented", "designed", "built"]
    project_score = min(
        sum(word in resume_text_lower for word in project_keywords),
        5
    )

    # ---------- FINAL SCORE ---------- #
    final_score = (
        category_score +
        skill_score +
        similarity_score +
        experience_score +
        education_score +
        project_score
    )

    final_score = round(min(max(final_score, 0), 100), 2)
    grade = calculate_grade(final_score)

    # ---------- AI FEEDBACK ---------- #
    feedback = []

    feedback.append(f"Predicted Category: {predicted_category}")

    if job_category_detected:
        if predicted_category == job_category_detected:
            feedback.append("Resume category strongly matches job domain.")
        else:
            feedback.append("Resume category does not match job domain.")

    if skill_score < 10:
        feedback.append("Low required skill match.")
    else:
        feedback.append("Strong technical skill alignment.")

    if experience < 2:
        feedback.append("Insufficient professional experience.")
    elif experience < 5:
        feedback.append("Good experience level.")
    else:
        feedback.append("Highly experienced candidate.")

    if education_score >= 8:
        feedback.append("Strong academic background.")

    if final_score >= 85:
        recommendation = "Strongly Recommended"
    elif final_score >= 70:
        recommendation = "Recommended"
    elif final_score >= 55:
        recommendation = "Consider with Caution"
    else:
        recommendation = "Not Recommended"

    return {
        "final_score": float(final_score),
        "grade": grade,
        "feedback": feedback,
        "recommendation": recommendation
    }