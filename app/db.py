import sqlite3
from datetime import datetime, timezone
from .config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_message_id INTEGER UNIQUE NOT NULL,
        company TEXT,
        role TEXT,
        location TEXT,
        skills TEXT,
        experience TEXT,
        education TEXT,
        apply_url TEXT,
        hr_email TEXT,
        description TEXT,
        raw_text TEXT NOT NULL,
        match_score INTEGER,
        status TEXT NOT NULL DEFAULT 'NEW',
        created_at TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_id INTEGER NOT NULL,
        resume_path TEXT,
        application_method TEXT,
        status TEXT NOT NULL DEFAULT 'READY_FOR_REVIEW',
        created_at TEXT NOT NULL,
        FOREIGN KEY(job_id) REFERENCES jobs(id)
    );
    ''')
    conn.commit()
    conn.close()


def insert_job(job, telegram_message_id, raw_text):
    conn = get_connection()
    try:
        cursor = conn.execute('''
        INSERT INTO jobs (
            telegram_message_id, company, role, location, skills,
            experience, education, apply_url, hr_email, description,
            raw_text, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            telegram_message_id,
            job.get('company', ''),
            job.get('role', ''),
            job.get('location', ''),
            ', '.join(job.get('skills', [])),
            job.get('experience', ''),
            job.get('education', ''),
            job.get('apply_url', ''),
            job.get('hr_email', ''),
            job.get('description', ''),
            raw_text,
            datetime.now(timezone.utc).isoformat()
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def update_job_match(job_id, score, status):
    conn = get_connection()
    conn.execute('UPDATE jobs SET match_score = ?, status = ? WHERE id = ?', (score, status, job_id))
    conn.commit()
    conn.close()


def insert_application(job_id, resume_path, method):
    conn = get_connection()
    conn.execute('''
    INSERT INTO applications (job_id, resume_path, application_method, created_at)
    VALUES (?, ?, ?, ?)
    ''', (job_id, resume_path, method, datetime.now(timezone.utc).isoformat()))
    conn.commit()
    conn.close()
