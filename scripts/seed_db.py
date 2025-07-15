import sys
import pandas as pd
from backend.db import engine, SessionLocal, Base
from backend.models.problem import Problem
import numpy as np

def clean_row(row, columns):
    clean = {}
    for col in columns:
        val = row.get(col)
        if pd.isnull(val) or (isinstance(val, float) and (np.isnan(val) or np.isinf(val))):
            clean[col] = None
        else:
            clean[col] = str(val).strip() if not isinstance(val, (list, dict)) else val
    return clean

def load_excel_to_db(excel_path):
    Base.metadata.create_all(bind=engine)
    df = pd.read_excel(excel_path)
    columns = ["question_id", "title", "Problem Link", "response_links"]
    for col in columns:
        if col not in df.columns:
            df[col] = None

    df = df.where(pd.notnull(df), None)
    session = SessionLocal()
    for _, row in df.iterrows():
        question_id = str(row["question_id"])
        existing = session.query(Problem).filter(Problem.question_id == question_id).first()
        if existing:
            existing.title = str(row["title"])
            existing.problem_link = str(row["Problem Link"])
            existing.response_links = str(row["response_links"]) or "[]"
        else:
            problem = Problem(
                question_id=question_id,
                title=str(row["title"]),
                problem_link=str(row["Problem Link"]),
                response_links=str(row["response_links"]) or "[]"
            )
            session.add(problem)
    session.commit()
    session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python backend/scripts/seed_db.py <excel_path>")
        sys.exit(1)
    excel_path = sys.argv[1]
    load_excel_to_db(excel_path)
    print("Seeding complete!")
