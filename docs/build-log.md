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

## Scope 1 — 2026-03-08

**What:** Le pipeline complet — 20 questions, scoring agrege, failure patterns, Eval Gate automatique.

**Decisions:**
- Failure patterns groupes par type de verdict (HALLUCINATION, INCORRECT, PARTIAL) avec liste des questions concernees
- PARTIAL compte comme PASS dans les scores agreges — coherent avec la methode (PARTIAL = sur la bonne piste)
- Meta-tests (expected volontairement faux) inclus dans le dataset pour verifier que le juge et l'Eval Gate fonctionnent de bout en bout

**Problems:**
- Q11 (migration strategy) : le juge a note INCORRECT alors que la reponse decrivait du "shadow mode + split traffic" qui EST du parallel processing. Le juge a ete trop strict sur le wording exact. Cas limite — le juge compare les mots, pas toujours les concepts. A surveiller.
- Q16 (backend language) : le juge a note HALLUCINATION car l'expected disait "should mention or indicate not mentioned". DocuQuery a repondu "Go" — impossible de verifier sans relire le PDF. Cas d'expected_answer trop vague.
- Lecon : les expected_answers vagues ("should describe...") sont plus dures a juger que les expected precis ("$3,600"). Le PM doit ecrire des expected concrets quand c'est possible.

**Time:** ~30 min (dataset + code failure patterns + test + analyse)

**Result:** 8/8 micro-tests PASS. Accord juge vs humain 90% (18/20). Eval Gate fonctionne (NO-GO declenche par meta-tests BLOCKING).
