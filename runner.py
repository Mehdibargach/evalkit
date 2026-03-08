"""Endpoint runner. Calls the user's API endpoint for each question."""

import httpx


async def call_endpoint(
    endpoint_url: str,
    question: str,
    request_field: str = "question",
    response_field: str = "answer",
    timeout: float = 30.0,
) -> dict:
    """Call a user's endpoint with a question and capture the response.

    Returns: {"response": str, "status": int, "error": str | None}
    """
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            payload = {request_field: question}
            resp = await client.post(endpoint_url, json=payload)

            if resp.status_code != 200:
                return {
                    "response": "",
                    "status": resp.status_code,
                    "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
                }

            data = resp.json()
            answer = data.get(response_field, "")
            if not answer and isinstance(data, dict):
                # Try to find the answer in nested structure
                for key, value in data.items():
                    if isinstance(value, str) and len(value) > 10:
                        answer = value
                        break

            return {
                "response": str(answer),
                "status": resp.status_code,
                "error": None,
            }

        except httpx.TimeoutException:
            return {
                "response": "",
                "status": 0,
                "error": f"Timeout after {timeout}s",
            }
        except Exception as e:
            return {
                "response": "",
                "status": 0,
                "error": str(e),
            }
