"""LLM-as-judge module. Scores a response against an expected answer."""

import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

JUDGE_SYSTEM_PROMPT = """You are an evaluation judge. Your job is to compare an AI system's actual response to an expected answer and score it.

You MUST return a JSON object with exactly these fields:
- "verdict": one of "CORRECT", "PARTIAL", "INCORRECT", "HALLUCINATION"
- "justification": 1-2 sentences explaining your verdict

Scoring rules:
- CORRECT: The actual response contains the key facts from the expected answer. Minor wording differences are OK. Numbers must match (exact or within 2%).
- PARTIAL: The actual response is on the right track but missing important details, or the number is in the right ballpark but not precise enough.
- INCORRECT: The actual response is factually wrong or completely misses the point.
- HALLUCINATION: The actual response invents information that is not in the expected answer AND presents it as fact. This is worse than INCORRECT — it means the AI made something up.

Special case — refusal questions:
If the expected answer indicates the AI should refuse or say "I don't know" (e.g., "The document does not contain this information"), then:
- If the actual response correctly refuses → CORRECT
- If the actual response provides a made-up answer → HALLUCINATION

Be strict. Do not give CORRECT to a vague answer when the expected answer is specific.
Do not give CORRECT when the actual response contains the right answer buried in wrong information.
Always justify your verdict with specific evidence from both the actual and expected answers."""


def judge_response(question: str, actual_response: str, expected_answer: str) -> dict:
    """Score a single response against its expected answer.

    Returns: {"verdict": str, "justification": str}
    """
    user_prompt = f"""Question: {question}

Expected answer: {expected_answer}

Actual response: {actual_response}

Score the actual response against the expected answer. Return JSON only."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    result = json.loads(response.choices[0].message.content)
    return {
        "verdict": result.get("verdict", "ERROR"),
        "justification": result.get("justification", "No justification provided"),
    }
