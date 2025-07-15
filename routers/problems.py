from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.services.problem_service import get_problem_with_references, get_all_problem
from backend.services.llm_service import run_llm_response
from backend.constants.system_messages import SYSTEM_MESSAGE
from backend.helpers.utils import prepare_llm_input

router = APIRouter(prefix="/problems", tags=["problems"])

@router.get("/")
def get_problems(db: Session = Depends(get_db)):
    result = get_all_problem(db)
    if not result:
        raise HTTPException(status_code=404, detail="Problem not found")
    return result

@router.get("/{question_id:path}/full")
def get_problem_full(question_id: str, db: Session = Depends(get_db)):
    result = get_problem_with_references(db, question_id)
    if not result:
        raise HTTPException(status_code=404, detail="Problem not found")
    return result

@router.get("/{question_id:path}/analysis")
def analyze_problem(question_id: str, db: Session = Depends(get_db)):
    result = get_problem_with_references(db, question_id)
    if not result or not result.get("problem"):
        raise HTTPException(status_code=404, detail="Problem not found")

    # Prepare the LLM input (prompt, context, etc.)
    llm_input = prepare_llm_input(result["problem"], result["additional_references"])

    try:
        # Join all chunks from the LLM to get the final result as a single string
        analysis_result = run_llm_response(
            SYSTEM_MESSAGE,
            llm_input["prompt"],
            llm_input["context"],
            llm_input["samples"]
        )
        status = "success"
    except Exception as e:
        analysis_result = f"LLM error: {e}"
        status = "error"

    return {
        "analysis_status": status,
        "analysis": analysis_result
    }
