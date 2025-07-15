from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from backend.db import get_db
from backend.services.problem_service import get_problem_with_references
from backend.services.llm_service import run_llm_response
from backend.constants.system_messages import SYSTEM_MESSAGE
from backend.helpers.utils import prepare_llm_input

router = APIRouter(
    prefix="/problems",
    tags=["problems"]
)

@router.websocket("/{question_id:path}/analysis/ws")
async def analyze_problem_ws(websocket: WebSocket, question_id: str):
    await websocket.accept()
    db = None
    try:
        db_gen = get_db()
        db = next(db_gen)
        print(f"WebSocket connected for question_id: {question_id}")

        # STEP 1: Fetching problem details
        await websocket.send_text("[[STEP]]Fetching problem details...")
        result = get_problem_with_references(db, question_id)
        if not result or not result.get("problem"):
            await websocket.send_text("[[ERROR]]Problem not found")
            await websocket.close()
            return

        # STEP 2: Generating additional context and system message
        await websocket.send_text("[[STEP]]Generating additional context and system message...")
        # (Pretend to generate - in reality it's in result)
        await websocket.send_text(f"[[CONTEXT]]{len(result.get('additional_references', []))} context references found.")

        # STEP 3: Preparing LLM input data
        await websocket.send_text("[[STEP]]Preparing LLM input data...")
        llm_input = prepare_llm_input(result["problem"], result["additional_references"])

        # STEP 4: Interacting with LLM...
        await websocket.send_text("[[STEP]]Interacting with LLM...")

        # Send LLM output, chunk by chunk
        for chunk in run_llm_response(
            SYSTEM_MESSAGE,
            llm_input["prompt"],
            llm_input["context"],
            llm_input["samples"]
        ):
            if chunk:
                print("SENDING CHUNK:", repr(chunk))
                try:
                    await websocket.send_text(chunk)
                except WebSocketDisconnect:
                    print("Client disconnected while streaming.")
                    break

        # STEP 5: Final result
        await websocket.send_text("[[STEP]]Analysis complete, final result below.")
        await websocket.send_text("[[ANALYSIS_COMPLETE]]")
        await websocket.close()
    except WebSocketDisconnect:
        print("WebSocket client disconnected.")
    except Exception as e:
        print("WebSocket error:", e)
        try:
            await websocket.send_text(f"[[ERROR]]{e}")
        except WebSocketDisconnect:
            pass
        await websocket.close()
    finally:
        if db:
            db.close()
