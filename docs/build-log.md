# Build Log — EvalKit

## Walking Skeleton — 2026-03-08

**What:** Le juge score 5 reponses contre DocuQuery AI.

**Decisions:**
- GPT-4o-mini comme juge avec `temperature=0` et `response_format=json_object` — scoring deterministe et structure
- Appels paralleles avec `asyncio.gather` — les 5 questions traitees en 25.7s (endpoint DocuQuery inclus)
- Meta-test integre dans le golden dataset (expected_answer volontairement faux) — verifie que le juge ne valide pas tout aveuglement

**Problems:**
- `.env` pas charge au bon moment — le client OpenAI etait cree au niveau module dans `judge.py` avant que `load_dotenv()` soit appele dans `app.py`. Fix : ajouter `load_dotenv()` directement dans `judge.py`.
- DocuQuery necessite un upload de document avant de pouvoir requeter — pas un bug EvalKit, mais a noter pour la doc utilisateur (l'endpoint doit etre pret a recevoir des questions).

**Time:** ~1h (code + tests + debug .env)

**Result:** 7/7 micro-tests PASS. Skeleton Check GO — le juge est fiable (4/4 verdicts coherents avec le jugement humain).
