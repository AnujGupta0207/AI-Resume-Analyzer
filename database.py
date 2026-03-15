import sqlite3

def init_db():
    conn = sqlite3.connect("hiring.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_description TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER,
        name TEXT,
        score REAL,
        grade TEXT,
        feedback TEXT,
        recommendation TEXT,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    )
    """)

    conn.commit()
    conn.close()