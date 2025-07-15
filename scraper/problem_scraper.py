import requests
from bs4 import BeautifulSoup
import ast
from backend.models import Problem

def scrape_reference_link(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; MyBot/0.1; +https://example.com/bot)"}
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code != 200:
            return {"url": url, "error": f"Failed ({resp.status_code})"}
        soup = BeautifulSoup(resp.content, "html.parser")
        code_blocks = soup.find_all('pre')
        snippet = "\n\n".join(cb.get_text("\n", strip=True) for cb in code_blocks) if code_blocks else ""
        if not snippet:
            snippet = soup.get_text("\n", strip=True)[:500]
        return {"url": url, "snippet": snippet}
    except Exception as e:
        return {"url": url, "error": str(e)}
    
def scrape_codeforces_full_problem(contest_id: str, problem_index: str):
    from bs4 import BeautifulSoup
    import requests

    urls = [
        f"https://codeforces.com/problemset/problem/{contest_id}/{problem_index}",
        f"https://codeforces.com/contest/{contest_id}/problem/{problem_index}"
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyBot/0.1; +https://example.com/bot)"
    }
    for url in urls:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            title_tag = soup.find(class_="title")
            statement_tag = soup.find(class_="problem-statement")
            input_spec = soup.find(class_="input-specification")
            output_spec = soup.find(class_="output-specification")
            sample_tests = soup.find_all(class_="sample-test")
            note_spec = soup.find_all(class_="note")

            statement = statement_tag.get_text("\n", strip=True) if statement_tag else ""
            input_text = input_spec.get_text("\n", strip=True) if input_spec else ""
            output_text = output_spec.get_text("\n", strip=True) if output_spec else ""
            note_text = "\n".join(note.get_text("\n", strip=True) for note in note_spec) if note_spec else ""

            # Raw HTML for frontend rendering
            statement_html = statement_tag.decode_contents() if statement_tag else ""
            input_html = input_spec.decode_contents() if input_spec else ""
            output_html = output_spec.decode_contents() if output_spec else ""
            note_html = "\n".join(note.decode_contents() for note in note_spec) if note_spec else ""

            samples = []
            for sample in sample_tests:
                input_blocks = sample.find_all('div', class_='input')
                output_blocks = sample.find_all('div', class_='output')
                inputs = [
                    block.find('pre').get_text("\n", strip=True) if block.find('pre') else ""
                    for block in input_blocks
                ]
                outputs = [
                    block.find('pre').get_text("\n", strip=True) if block.find('pre') else ""
                    for block in output_blocks
                ]
                samples.append({"inputs": inputs, "outputs": outputs})

            return {
                "url": url,
                "title": title_tag.text.strip() if title_tag else "",
                "statement": statement,
                "input_spec": input_text,
                "output_spec": output_text,
                "note_text": note_text,
                "samples": samples,
                "raw": {
                    "statement": statement_html,
                    "input_spec": input_html,
                    "output_spec": output_html,
                    "note": note_html
                }
            }
        else:
            print(f"Failed with status code: {resp.status_code}")
    print("Failed to fetch problem from both URLs.")
    return None


def get_problem_with_references(db, question_id):
    # 1. Fetch the problem from your DB
    problem_obj = db.query(Problem).filter(Problem.question_id == question_id).first()
    if not problem_obj:
        return None

    # 2. Parse contest_id/problem_index from problem_link
    import re
    match = re.search(r'/(\d+)/([A-Z][0-9]?)$', problem_obj.problem_link)
    if not match:
        parts = problem_obj.problem_link.rstrip('/').split('/')
        contest_id, problem_index = parts[-2], parts[-1]
    else:
        contest_id, problem_index = match.group(1), match.group(2)

    # 3. Scrape Codeforces problem
    problem = scrape_codeforces_full_problem(contest_id, problem_index)

    # 4. Parse response_links (JSON array string or CSV)
    references = []
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

    return {
        "problem": problem,
        "additional_references": additional_references
    }
