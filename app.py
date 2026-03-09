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


class FailurePattern(BaseModel):
    verdict: str  # INCORRECT, HALLUCINATION, PARTIAL
    count: int
    questions: list[str]


class EvalReport(BaseModel):
    total_questions: int
    results: list[QuestionResult]
    scores: dict  # {"BLOCKING": {"pass": X, "total": Y}, ...}
    failure_patterns: list[FailurePattern]
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


def compute_failure_patterns(results: list[QuestionResult]) -> list[FailurePattern]:
    """Group failed questions by verdict type."""
    patterns: dict[str, list[str]] = {}
    for r in results:
        if r.verdict not in ("CORRECT",):
            verdict = r.verdict
            if verdict not in patterns:
                patterns[verdict] = []
            patterns[verdict].append(r.question)

    return [
        FailurePattern(verdict=verdict, count=len(questions), questions=questions)
        for verdict, questions in sorted(patterns.items())
    ]


# --- Demo mode: mock endpoint + built-in dataset ---

DEMO_DATASET = [
    {"question": "What is the total development budget?", "expected_answer": "$18.5 million", "criteria_level": "BLOCKING"},
    {"question": "What security certifications are planned?", "expected_answer": "PCI DSS v4.0 Level 1 and SOC 2 Type II", "criteria_level": "BLOCKING"},
    {"question": "What is the customer acquisition cost at 200 customers?", "expected_answer": "$3,600", "criteria_level": "BLOCKING"},
    {"question": "What was the company revenue in Q4 2025?", "expected_answer": "The document does not contain revenue figures.", "criteria_level": "BLOCKING"},
    {"question": "Summarize the main advantages of the product.", "expected_answer": "Faster processing, lower fees, modern cloud infrastructure, and AI-powered fraud detection.", "criteria_level": "QUALITY"},
    {"question": "What is the go-to-market strategy?", "expected_answer": "Closed beta with design partners, then limited availability, then general availability with content marketing and outbound sales.", "criteria_level": "QUALITY"},
    {"question": "What is the pricing model?", "expected_answer": "Three tiers: Standard (2.7% + $0.25/tx), Growth ($499/mo), Enterprise (custom).", "criteria_level": "QUALITY"},
    {"question": "What is the recommended font size for the dashboard?", "expected_answer": "Not specified in the document.", "criteria_level": "SIGNAL"},
]

# Mock responses: simulate a real AI with some correct, some partial, some wrong
MOCK_RESPONSES = {
    "What is the total development budget?": "The total development budget across all phases is $18.5 million.",
    "What security certifications are planned?": "PCI DSS v4.0 Level 1 and SOC 2 Type II are planned.",
    "What is the customer acquisition cost at 200 customers?": "The CAC at 200 customers is $3,600.",
    "What was the company revenue in Q4 2025?": "The company earned $12M in Q4 2025.",  # HALLUCINATION — info not in doc
    "Summarize the main advantages of the product.": "The product offers integrated analytics, transparent pricing, and self-serve onboarding for mid-market companies.",  # PARTIAL — misses key points
    "What is the go-to-market strategy?": "The GTM includes a closed beta with 15 design partners, limited availability for 100 merchants, then general availability with content marketing, developer community, partnerships, and outbound sales.",
    "What is the pricing model?": "There are three plans: Standard at 2.7% + $0.25 per transaction, Growth at $499/month, and Enterprise with custom pricing.",
    "What is the recommended font size for the dashboard?": "I don't have enough information to answer this question.",
}


@app.post("/mock/query")
async def mock_query(request: dict):
    """Mock endpoint that simulates an AI answering questions."""
    question = request.get("question", "")
    answer = MOCK_RESPONSES.get(question, "I don't have enough information to answer this question.")
    return {"answer": answer}


@app.post("/demo", response_model=EvalReport)
async def demo_evaluate():
    """Run evaluation with built-in demo dataset against built-in mock endpoint."""
    start_time = time.time()

    async def process_demo_question(q: dict) -> QuestionResult:
        # Call our own mock endpoint
        mock_response = MOCK_RESPONSES.get(q["question"], "I don't have enough information.")

        judge_result = judge_response(
            question=q["question"],
            actual_response=mock_response,
            expected_answer=q["expected_answer"],
        )

        return QuestionResult(
            question=q["question"],
            expected_answer=q["expected_answer"],
            criteria_level=q["criteria_level"],
            actual_response=mock_response,
            verdict=judge_result["verdict"],
            justification=judge_result["justification"],
        )

    results = await asyncio.gather(*[process_demo_question(q) for q in DEMO_DATASET])
    results = list(results)

    scores = compute_scores(results)
    failure_patterns = compute_failure_patterns(results)
    decision, decision_reason = compute_eval_gate(results)

    latency = round(time.time() - start_time, 1)

    return EvalReport(
        total_questions=len(results),
        results=results,
        scores=scores,
        failure_patterns=failure_patterns,
        decision=decision,
        decision_reason=decision_reason,
        latency_seconds=latency,
    )


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

    # 4. Compute scores, failure patterns, and decision
    scores = compute_scores(results)
    failure_patterns = compute_failure_patterns(results)
    decision, decision_reason = compute_eval_gate(results)

    latency = round(time.time() - start_time, 1)

    return EvalReport(
        total_questions=len(results),
        results=results,
        scores=scores,
        failure_patterns=failure_patterns,
        decision=decision,
        decision_reason=decision_reason,
        latency_seconds=latency,
    )
