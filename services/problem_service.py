import ast
import re
import json
from backend.models.problem import Problem
from backend.scraper.problem_scraper import scrape_codeforces_full_problem, scrape_reference_link

def get_all_problem(db):
    problems = db.query(Problem).all()
    return problems

def get_problem_with_references(db, question_id):
    problem_obj = db.query(Problem).filter(Problem.question_id == question_id).first()
    if not problem_obj:
        return None

    # 1. Try to load problem data from cache
    if problem_obj.scraped_json:
        # This will convert the JSON string to a Python object (could be None if 'null')
        problem_data = json.loads(problem_obj.scraped_json)
        if problem_data is not None:
            # Use cached value
            return problem_data
    else:
        # Parse contest_id and problem_index from the link
        match = re.search(r'/(\d+)/([A-Z][0-9]?)$', problem_obj.problem_link)
        if not match:
            parts = problem_obj.problem_link.rstrip('/').split('/')
            contest_id, problem_index = parts[-2], parts[-1]
        else:
            contest_id, problem_index = match.group(1), match.group(2)

        # Scrape Codeforces problem
        problem_data = scrape_codeforces_full_problem(contest_id, problem_index)

        # 2. Parse and fetch additional reference links (not cached)
        links = []
        if problem_obj.response_links:
            try:
                if problem_obj.response_links.strip().startswith("["):
                    links = ast.literal_eval(problem_obj.response_links)
                else:
                    links = [l.strip() for l in problem_obj.response_links.split(",") if l.strip()]
            except Exception:
                links = []

        additional_references = [scrape_reference_link(url) for url in links]

        result =  {
            "problem": problem_data,
            "additional_references": additional_references
        }
        # Save to DB for future fast access
        problem_obj.scraped_json = json.dumps(result)
        db.commit()
