# BUILD Gameplan

> Template from The Builder PM Method — BUILD phase (start)

---

**Project Name:** EvalKit
**Date:** 2026-03-08
**Cycle Appetite:** 1 semaine
**MVP Features (from 1-Pager):**
1. Upload CSV + appel endpoint automatique
2. LLM-as-judge scoring (accuracy, hallucination, faithfulness)
3. Classification BLOCKING/QUALITY/SIGNAL + decision Eval Gate
4. Eval Report structure (scores agreges + failure patterns + verdict)

**Riskiest Assumption (from 1-Pager):**
"Un LLM-juge (GPT-4o-mini) peut scorer des reponses LLM avec une fiabilite suffisante (>= 80% d'accord avec le jugement humain) pour qu'un PM fasse confiance au verdict — en moins de 60 secondes pour 20 questions."

---

## Context Setup

**CLAUDE.md** du projet a configurer avec : Problem, Solution, Architecture Decisions du 1-Pager. A faire avant le premier commit.

---

## Walking Skeleton — "Le juge score 5 reponses"

> Le chemin le plus fin possible de bout en bout. On envoie 5 questions a un endpoint existant (DocuQuery ou DataPilot), on capture les reponses, un LLM-juge les compare aux reponses attendues, et on obtient un score par question.

**What it does :** On fournit un mini CSV de 5 questions (question + expected_answer + criteria_level). EvalKit appelle l'endpoint pour chaque question, capture la reponse, envoie la paire (reponse recue, reponse attendue) au LLM-juge (GPT-4o-mini), et obtient un verdict (CORRECT / PARTIAL / INCORRECT / HALLUCINATION) avec une justification.

**End-to-end path :** CSV upload → parse questions → HTTP call endpoint utilisateur → capture reponse → LLM-juge compare (reponse vs expected) → verdict + justification → affichage resultats

**Done when :** On peut scorer 5 reponses d'un vrai endpoint, obtenir un verdict par question avec justification, et le tout prend moins de 30 secondes.

**Donnees de test :** 5 questions issues du golden dataset de DocuQuery AI (reponses attendues connues, endpoint disponible sur Render). Mix :
- 2 questions factuelles (reponse exacte verifiable)
- 1 question de synthese (reponse subjective)
- 1 cas adversarial (question dont la reponse n'est pas dans le document — le endpoint devrait refuser)
- 1 cas ou on fournit volontairement une MAUVAISE reponse attendue (pour verifier que le juge ne dit pas toujours CORRECT)

**Endpoint de test :** `https://docuquery-ai-5rfb.onrender.com` (DocuQuery AI — deploye, stable)

**Micro-tests :**

| # | Test | Pass Criteria |
|---|------|---------------|
| WS-1 | CSV parsing | Le systeme lit un CSV avec 3 colonnes (question, expected_answer, criteria_level) et extrait correctement les 5 lignes. |
| WS-2 | Appel endpoint | Les 5 questions sont envoyees a l'endpoint DocuQuery. Les 5 reponses sont capturees (status 200, texte non vide). Timeout 30s par appel. |
| WS-3 | Scoring juge — reponse correcte | Pour les 2 questions factuelles dont la reponse est connue et juste, le juge retourne CORRECT. |
| WS-4 | Scoring juge — reponse partielle/subjective | Pour la question de synthese, le juge retourne CORRECT ou PARTIAL (pas INCORRECT). |
| WS-5 | Scoring juge — refus correct | Pour la question adversariale (info absente du document), si l'endpoint refuse correctement, le juge retourne CORRECT. Si l'endpoint hallucine, le juge retourne HALLUCINATION. |
| WS-6 | Scoring juge — meta-test | Pour le cas ou expected_answer est volontairement faux (on dit que la bonne reponse est "$999" alors que c'est "$3,600"), le juge ne doit PAS retourner CORRECT. Il doit retourner INCORRECT. Ce test verifie que le juge ne valide pas tout aveuglement. |
| WS-7 | Justification | Chaque verdict est accompagne d'une justification en texte (1-2 phrases) qui explique pourquoi le juge a donne ce score. Zero verdict sans justification. |

→ **RITUAL: Skeleton Check** — GPT-4o-mini est-il un juge fiable ?
- WS-3 a WS-6 = 4 tests qui mesurent directement la fiabilite du juge.
- Si >= 3/4 verdicts sont coherents avec le jugement humain → GO, continuer.
- Si < 3/4 → Tester GPT-4o. Si toujours NON → Pivoter (scoring deterministe uniquement, pas de LLM-juge).

---

## Scope 1 — "Le pipeline complet"

**What it adds :** Passage de 5 a 20 questions. Scoring agrege. Classification BLOCKING/QUALITY/SIGNAL. Decision Eval Gate automatique (GO / CONDITIONAL GO / NO-GO). Eval Report structure.

**Done when :** On peut uploader un CSV de 20 questions, recevoir un Eval Report complet avec : score par question, scores agreges par niveau (BLOCKING / QUALITY / SIGNAL), failure patterns identifies, decision Eval Gate. Le tout en < 60 secondes.

**Donnees de test :** 20 questions construites sur le modele du golden dataset DataPilot (reponses pre-verifiees avec pandas). Mix de niveaux :
- 8 questions BLOCKING (accuracy, hallucination)
- 8 questions QUALITY (pertinence, completude)
- 4 questions SIGNAL (ton, format)

**Micro-tests :**

| # | Test | Pass Criteria |
|---|------|---------------|
| S1-1 | Appels paralleles | Les 20 questions sont envoyees a l'endpoint en parallele (pas sequentiel). Temps total < 60 secondes. |
| S1-2 | Scores agreges par niveau | Le rapport affiche 3 scores : BLOCKING (% PASS parmi les criteres BLOCKING), QUALITY (% PASS parmi les QUALITY), SIGNAL (% PASS parmi les SIGNAL). Calcul verifie manuellement sur 3 cas. |
| S1-3 | Decision Eval Gate — NO-GO | Si on injecte 1 question BLOCKING qui FAIL (hallucination volontaire), la decision finale est NO-GO. Pas de negociation. |
| S1-4 | Decision Eval Gate — CONDITIONAL GO | Si 0 BLOCKING fail + 1 QUALITY fail, la decision est CONDITIONAL GO avec la condition documentee. |
| S1-5 | Decision Eval Gate — GO | Si 0 BLOCKING fail + 0 QUALITY fail, la decision est GO. |
| S1-6 | Failure patterns | Les questions qui FAIL sont groupees par pattern (ex: "2 HALLUCINATION, 1 INCORRECT"). Chaque pattern liste les questions concernees. |
| S1-7 | Eval Report structure | Le rapport contient : (1) tableau question par question, (2) scores agreges par niveau, (3) failure patterns, (4) decision finale avec justification. Format JSON + affichage lisible. |
| S1-8 | Accord juge vs humain | Sur les 20 questions, comparer les verdicts du juge avec le jugement humain (Mehdi). Accord >= 80% (>= 16/20). |

---

## Scope 2 — "Le produit fini"

**What it adds :** Frontend Lovable (upload CSV, config endpoint, resultats visuels), deploy Render. Demo-ready.

**Done when :** Un visiteur peut aller sur l'URL, uploader un CSV, entrer l'URL de son endpoint, cliquer "Run Eval", et voir un Eval Report complet avec verdict GO / CONDITIONAL GO / NO-GO.

**Micro-tests :**

| # | Test | Pass Criteria |
|---|------|---------------|
| S2-1 | Upload CSV | Drag & drop ou file picker → le fichier est lu, les colonnes sont detectees, preview des 3 premieres lignes affichee. |
| S2-2 | Config endpoint | L'utilisateur entre : URL de l'endpoint, methode (POST), champ de la requete (ex: "question"), champ de la reponse (ex: "answer"). Un bouton "Test connection" envoie 1 question et affiche la reponse brute. |
| S2-3 | Run Eval | Bouton "Run Eval" → loader avec progression (X/20 questions) → resultats affiches. |
| S2-4 | Affichage resultats | Tableau question par question (question, reponse recue, expected, verdict, justification). Code couleur : vert = CORRECT, jaune = PARTIAL, rouge = INCORRECT/HALLUCINATION. |
| S2-5 | Verdict final | Bandeau en haut : GO (vert) / CONDITIONAL GO (jaune) / NO-GO (rouge) avec scores agreges BLOCKING / QUALITY / SIGNAL. |
| S2-6 | Deploy | Backend Render + frontend Lovable connectes, demo fonctionnelle sur URL publique. |

---

## DOR/DOD Compliance Tracker

| Slice | R1 Gate | R2 Deps | R3 Data | R4 Tests | R5 CLAUDE.md | D1 Tests | D2 Log | D3 Walk | D4 CLAUDE | D5 Commit |
|-------|---------|---------|---------|----------|-------------|----------|--------|---------|-----------|-----------|
| WS | — | | | | | | | | | |
| S1 | | | | | | | | | | |
| S2 | | | | | | | | | | |

---

## Exit Criteria (BUILD → EVALUATE)

- [ ] Les 4 features MVP fonctionnelles de bout en bout
- [ ] Riskiest Assumption testee (Skeleton Check passe : juge fiable >= 80%)
- [ ] Open Questions du 1-Pager resolues ou converties en ADR
- [ ] Build Log a jour
- [ ] Pret pour evaluation formelle contre les Success Metrics
