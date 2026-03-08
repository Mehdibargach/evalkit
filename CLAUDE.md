# EvalKit

## What this project is
AI-powered evaluation tool for PMs. Upload a CSV of test cases (question + expected answer), connect your API endpoint, get a scored Eval Report with a GO / CONDITIONAL GO / NO-GO verdict. Tests the responses of your backend API, not the frontend UI.

## AI Typology
AI Evaluation (tooling) — side project #5/5 in the Builder PM portfolio.

## Architecture Decisions (from 1-Pager)
- **LLM judge**: GPT-4o-mini (OpenAI) — cheap, sufficient for structured scoring with JSON mode
- **Input format**: CSV (question, expected_answer, criteria_level)
- **Scoring method**: LLM-as-judge generic — compares actual response vs expected, returns CORRECT/PARTIAL/INCORRECT/HALLUCINATION + justification
- **Approach**: Generic judge, not per-typology. The CSV is the contract — the PM defines what "correct" means.
- **Endpoint call**: HTTP POST configurable (URL + headers + field mapping)
- **Backend**: FastAPI (Python) — same stack as 4 previous projects
- **Frontend**: Lovable (React + Tailwind)
- **Deploy**: Render ($7/mo)

## Current Phase
BUILD — Scope 1

### Walking Skeleton — DONE (7/7 PASS)
- 5 questions against DocuQuery AI endpoint (https://docuquery-ai-5rfb.onrender.com)
- End-to-end: CSV → parse → call endpoint → capture response → LLM judge scores → verdict + justification
- Skeleton Check: GO — 4/4 judge verdicts coherent with human judgment
- Latency: 25.7s for 5 questions (parallel)
- Bug fixed: .env not loaded before OpenAI client init in judge.py
- Eval Gate decision logic works (meta-test triggered NO_GO correctly)

### Scope 1 — DONE (8/8 PASS)
- 20 questions against DocuQuery, 47.4s total (parallel)
- Scores agreges: BLOCKING 75%, QUALITY 87.5%, SIGNAL 75%
- Failure patterns: 1 HALLUCINATION, 3 INCORRECT, 3 PARTIAL
- Eval Gate: NO-GO (2 meta-tests BLOCKING triggered correctly)
- Accord juge vs humain: 90% (18/20)
- Lecon: expected_answers precis > expected vagues pour la fiabilite du juge

### Scope 2 — "Le produit fini"
- Frontend Lovable: upload CSV, config endpoint, resultats visuels, verdict
- Deploy: backend Render + frontend Lovable
- 6 micro-tests (S2-1 to S2-6)

## Riskiest Assumption
"An LLM judge (GPT-4o-mini) can score LLM responses with sufficient reliability (>= 80% agreement with human judgment) for a PM to trust the verdict — in under 60 seconds for 20 questions."

## Scope (4 IN, 4 OUT)
**IN:** CSV upload + auto endpoint call, LLM-as-judge scoring, BLOCKING/QUALITY/SIGNAL + Eval Gate, Eval Report
**OUT:** Dashboard visuel, Historique runs, Golden dataset generator, Multi-endpoint comparison

## Anti-patterns
- NEVER decompose into backend → frontend → integration
- Always vertical slices (Walking Skeleton → Scopes)

## Build Rules (applies to all projects)
1. Micro-test = gate, pas une etape. Code → Micro-test PASS → Doc → Commit.
2. Le gameplan fait autorite sur les donnees de test.
3. Checklist qualite walkthrough — audience non-technique.
4. Pas de mode batch.
5. Test first, code if needed.
6. UX dans les prompts — no jargon leaked to user.
7. PM Validation Gate — apres micro-tests PASS, AVANT commit : attendre GO explicite du PM.

## Build Checklist
See `/Users/mbargach/Claude Workspace/Projects/builder-pm/templates/build-checklist-claude.md`
