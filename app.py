"""EvalKit — AI evaluation tool for PMs.
Upload a CSV of test cases, connect your endpoint, get a GO / NO-GO verdict.
"""

import csv
import io
import asyncio
import time

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from judge import judge_response
from runner import call_endpoint

load_dotenv()

app = FastAPI(title="EvalKit", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvalRequest(BaseModel):
    endpoint_url: str
    request_field: str = "question"
    response_field: str = "answer"


class QuestionResult(BaseModel):
    question: str
    expected_answer: str
    criteria_level: str
    actual_response: str
    verdict: str
    justification: str
    error: str | None = None


class EvalReport(BaseModel):
    total_questions: int
    results: list[QuestionResult]
    scores: dict  # {"BLOCKING": {"pass": X, "total": Y}, ...}
    decision: str  # GO / CONDITIONAL_GO / NO_GO
    decision_reason: str
    latency_seconds: float


def parse_csv(content: str) -> list[dict]:
    """Parse CSV content into list of question dicts."""
    reader = csv.DictReader(io.StringIO(content))
    rows = []
    for row in reader:
        rows.append({
            "question": row["question"].strip(),
            "expected_answer": row["expected_answer"].strip(),
            "criteria_level": row["criteria_level"].strip().upper(),
        })
    return rows


def compute_eval_gate(results: list[QuestionResult]) -> tuple[str, str]:
    """Apply Eval Gate rules: BLOCKING fail = NO-GO, QUALITY fail = CONDITIONAL GO.

    Returns: (decision, reason)
    """
    blocking_fail = []
    quality_fail = []
    signal_fail = []

    for r in results:
        is_pass = r.verdict in ("CORRECT", "PARTIAL")
        if r.criteria_level == "BLOCKING" and not is_pass:
            blocking_fail.append(r.question)
        elif r.criteria_level == "QUALITY" and not is_pass:
            quality_fail.append(r.question)
        elif r.criteria_level == "SIGNAL" and not is_pass:
            signal_fail.append(r.question)

    if blocking_fail:
        reason = f"{len(blocking_fail)} BLOCKING fail(s): {'; '.join(blocking_fail[:3])}"
        return "NO_GO", reason

    if quality_fail:
        reason = f"0 BLOCKING fail, {len(quality_fail)} QUALITY fail(s): {'; '.join(quality_fail[:3])}"
        return "CONDITIONAL_GO", reason

    if signal_fail:
        reason = f"0 BLOCKING fail, 0 QUALITY fail, {len(signal_fail)} SIGNAL fail(s)"
        return "CONDITIONAL_GO", reason

    return "GO", "All criteria PASS."


def compute_scores(results: list[QuestionResult]) -> dict:
    """Compute pass rates per criteria level."""
    scores = {}
    for level in ("BLOCKING", "QUALITY", "SIGNAL"):
        level_results = [r for r in results if r.criteria_level == level]
        if level_results:
            passed = sum(1 for r in level_results if r.verdict in ("CORRECT", "PARTIAL"))
            scores[level] = {
                "pass": passed,
                "total": len(level_results),
                "rate": round(passed / len(level_results) * 100, 1),
            }
    return scores


@app.get("/health")
def health():
    return {"status": "ok", "service": "evalkit"}


@app.post("/evaluate", response_model=EvalReport)
async def evaluate(
    file: UploadFile = File(...),
    endpoint_url: str = Form(...),
    request_field: str = Form("question"),
    response_field: str = Form("answer"),
):
    """Run an evaluation: parse CSV, call endpoint for each question, judge responses."""
    start_time = time.time()

    # 1. Parse CSV
    content = await file.read()
    questions = parse_csv(content.decode("utf-8"))

    # 2. Call endpoint for each question
    async def process_question(q: dict) -> QuestionResult:
        endpoint_result = await call_endpoint(
            endpoint_url=endpoint_url,
            question=q["question"],
            request_field=request_field,
            response_field=response_field,
        )

        if endpoint_result["error"]:
            return QuestionResult(
                question=q["question"],
                expected_answer=q["expected_answer"],
                criteria_level=q["criteria_level"],
                actual_response="",
                verdict="INCORRECT",
                justification=f"Endpoint error: {endpoint_result['error']}",
                error=endpoint_result["error"],
            )

        # 3. Judge the response
        judge_result = judge_response(
            question=q["question"],
            actual_response=endpoint_result["response"],
            expected_answer=q["expected_answer"],
        )

        return QuestionResult(
            question=q["question"],
            expected_answer=q["expected_answer"],
            criteria_level=q["criteria_level"],
            actual_response=endpoint_result["response"],
            verdict=judge_result["verdict"],
            justification=judge_result["justification"],
        )

    # Run all questions in parallel
    results = await asyncio.gather(*[process_question(q) for q in questions])
    results = list(results)

    # 4. Compute scores and decision
    scores = compute_scores(results)
    decision, decision_reason = compute_eval_gate(results)

    latency = round(time.time() - start_time, 1)

    return EvalReport(
        total_questions=len(results),
        results=results,
        scores=scores,
        decision=decision,
        decision_reason=decision_reason,
        latency_seconds=latency,
    )
