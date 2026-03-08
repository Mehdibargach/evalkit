# Builder PM 1-Pager

> Template from The Builder PM Method — FRAME phase

---

**Project Name:** EvalKit
**One-liner:** Teste les reponses de ton IA — CSV in, verdict GO / NO-GO out.
**Date:** 2026-03-08
**Builder PM Method Phase:** AI Evaluation (tooling) — side project #5/5 dans le portfolio Builder PM.

---

## Problem

1. **Le "vibe check" ne scale pas.** Un PM qui a builde un produit AI verifie la qualite en posant quelques questions a la main et en lisant les reponses. C'est du feeling, pas de la mesure. Il ne peut pas tester 50 ou 200 cas comme ca. Et quand il change un prompt, il n'a aucun moyen de savoir s'il a casse quelque chose.

2. **Le spreadsheet eval est lent et fragile.** Les PMs plus rigoureux ouvrent un Google Sheet : question en colonne A, reponse copiee en colonne B, score manuel en colonne C. C'est mieux que le vibe check, mais c'est 2 a 4 heures par session, pas reproductible, et ca ne donne aucun diagnostic — juste des chiffres bruts.

3. **Les outils d'eval existants sont faits pour les devs.** DeepEval, Ragas, Braintrust... tous demandent d'ecrire du Python, de configurer des pipelines, de comprendre des concepts ML. Un PM qui builde avec du vibe coding (Claude Code, Lovable, Cursor) n'a pas acces a ces outils.

4. **Pas de decision structuree.** Meme avec des scores, le PM n'a pas de framework pour decider : est-ce que 82% d'accuracy, c'est assez bien pour shipper ? Quels criteres sont bloquants vs acceptables ? Aujourd'hui, cette decision se prend au feeling.

### Comment le marche resout ca aujourd'hui

| Outil | Approche | Limite |
|-------|----------|--------|
| Vibe check (manuel) | Poser quelques questions, lire les reponses, juger au feeling | Pas de mesure, pas reproductible, rate les regressions |
| Google Sheets | Question / reponse / score dans un tableur | 2-4h par session, zero automatisation, pas de diagnostic |
| DeepEval / Ragas (gratuit, open-source) | Frameworks Python avec 14+ metriques | Faut ecrire du code, cible les ML engineers |
| Braintrust / Maxim AI ($249+/mo) | Plateformes SaaS completes | Enterprise, cher, config complexe |
| ChatGPT (copier-coller) | Coller des reponses et demander "c'est bon ?" | Pas reproductible, pas structure, pas de scoring |

**Le trou :** Aucun outil ne permet a un PM de tester les reponses de son API backend en 15 minutes — sans ecrire de code, avec un verdict GO / NO-GO structure.

### Ce qu'EvalKit teste (et ne teste pas)

EvalKit evalue **les reponses de ton backend** (ton API qui appelle un LLM), pas ton interface utilisateur. Concretement : EvalKit appelle ton endpoint comme le ferait Postman, compare ce que l'IA repond vs ce qu'elle devrait repondre, et score chaque reponse. Le frontend (boutons, layout, CSS) n'est pas dans le perimetre — ce qu'on evalue, c'est la qualite de l'intelligence, pas l'affichage.

---

## User

- **Primary :** Builder PM / solo builder qui a un produit AI deploye (ou en cours) et veut evaluer la qualite avant de shipper. Il builde avec du vibe coding, il n'ecrit pas de scripts Python.
- **Secondary :** Petit team produit AI (PM + 1-2 devs) qui veut un process d'eval reproductible sans investir dans une plateforme enterprise.
- **Context :** Fin de BUILD, avant SHIP. Le PM a un endpoint qui marche, il a des questions de test en tete, mais pas d'outil pour les executer systematiquement et obtenir un verdict.

---

## Solution

| Pain | Feature |
|------|---------|
| Vibe check ne scale pas | **Execution automatique :** EvalKit appelle l'endpoint pour chaque question du dataset et capture les reponses. Plus de copier-coller. |
| Spreadsheet lent et fragile | **Scoring automatique :** un LLM-juge (= un deuxieme modele de langage qui joue le role de correcteur) note chaque reponse — accuracy, hallucination, faithfulness. Plus de notation manuelle. |
| Outils existants = pour devs | **CSV in → Verdict out :** pas de code, pas de config. Upload un CSV, donne un endpoint, clique. |
| Pas de decision structuree | **Eval Gate automatique :** chaque critere classe BLOCKING / QUALITY / SIGNAL → decision GO / CONDITIONAL GO / NO-GO generee automatiquement. |

### Approche generique (pas de "mode" par typologie)

Evaluer un RAG (reponses texte) ≠ evaluer un classifier (etiquettes) ≠ evaluer un moteur de recs (liste de films). Plutot que de creer un mode par type d'IA, EvalKit utilise un juge generique : "compare la reponse recue a la reponse attendue". C'est le **CSV qui est le contrat** — c'est le PM qui definit ce que "correct" veut dire en ecrivant sa reponse attendue. Si le PM ecrit `expected: "thriller coreen post-2015"`, le juge verifie ca. Si le PM ecrit `expected: "$76,381"`, le juge verifie ca aussi.

---

## Riskiest Assumption

**"Un LLM-juge (GPT-4o-mini) peut scorer des reponses LLM avec une fiabilite suffisante pour qu'un PM fasse confiance au verdict."**

Les 3 contraintes critiques :
- **Fiabilite :** >= 80% d'accord avec le jugement humain (si le PM dit CORRECT, le juge dit CORRECT 80%+ du temps)
- **Latence :** < 60 secondes pour 20 questions (execution + scoring)
- **Zero auto-hallucination :** le juge ne doit JAMAIS inventer un score sans justification verifiable

> Contraintes non-fonctionnelles integrees des le FRAME (lecon LeakFinder).

---

## Scope Scoring

| Feature | Pain | Risk | Effort | Score | In/Out |
|---------|------|------|--------|-------|--------|
| Upload CSV + appel endpoint automatique | 3 | 2 | 1 | **4** | **IN** |
| LLM-as-judge scoring (accuracy, hallucination, faithfulness) | 3 | 3 | 2 | **4** | **IN** |
| Classification BLOCKING/QUALITY/SIGNAL + decision Eval Gate | 3 | 2 | 1 | **4** | **IN** |
| Eval Report structure (scores agreges + failure patterns + verdict) | 3 | 1 | 1 | **3** | **IN** |
| Dashboard visuel (charts, distributions, side-by-side) | 1 | 1 | 2 | **0** | OUT |
| Historique des runs (versioning, comparaison avant/apres) | 1 | 1 | 3 | **-1** | OUT |
| Golden dataset generator (l'outil cree les questions pour toi) | 2 | 2 | 3 | **1** | OUT |
| Multi-endpoint comparison (tester 2 prompts cote a cote) | 2 | 1 | 2 | **1** | OUT |

### MVP (Score >= 3) — 4 features

1. **CSV upload + appel endpoint automatique :** l'utilisateur upload un fichier de test (question + reponse attendue + niveau de critere) et donne l'URL de son API. EvalKit envoie chaque question et capture les reponses.
2. **LLM-as-judge scoring :** un deuxieme modele joue le correcteur — il compare chaque reponse recue a la reponse attendue et note : CORRECT / PARTIAL / INCORRECT / HALLUCINATION, avec une justification.
3. **Classification BLOCKING/QUALITY/SIGNAL + Eval Gate :** chaque critere du CSV est tague avec son niveau. EvalKit applique les regles : 1 BLOCKING fail = NO-GO, pas de discussion.
4. **Eval Report structure :** tableau des resultats, scores agreges par niveau, failure patterns identifies, decision finale (GO / CONDITIONAL GO / NO-GO).

### Out of Scope

- **Dashboard visuel** — Le frontend Lovable affichera les resultats. Pas besoin de charts avances pour le MVP.
- **Historique des runs** — V2 potentiel. Pour le MVP, chaque run est independant.
- **Golden dataset generator** — Creer les questions reste le job du PM. C'est la qu'est la valeur humaine.
- **Multi-endpoint comparison** — Utile pour A/B testing de prompts, mais pas necessaire pour valider la RA.

---

## Success Metrics

| Metric | Target | Level | How to Test |
|--------|--------|-------|-------------|
| Accord juge LLM vs jugement humain | >= 80% | **BLOCKING** | Comparer les scores EvalKit vs les scores manuels de Mehdi sur un golden dataset existant (DocuQuery ou DataPilot) |
| Temps total pour 20 questions | < 60 secondes | **BLOCKING** | Timer end-to-end (upload → rapport) |
| Zero auto-hallucination du juge | 0 cas ou le juge invente un verdict sans justification | **BLOCKING** | Verifier chaque justification du juge |
| Decision Eval Gate correcte | 100% coherence avec les regles | **QUALITY** | Verifier que 1 BLOCKING fail = NO-GO, toujours. Tester avec des cas ou BLOCKING passe et QUALITY fail = CONDITIONAL GO. |
| Cout par run (20 questions) | < $0.05 | **SIGNAL** | Verifier usage OpenAI apres un run |

> **Eval Gate Framework :**
> - **BLOCKING** : doit passer, sinon NO-GO
> - **QUALITY** : devrait passer, sinon CONDITIONAL GO (condition documentee)
> - **SIGNAL** : nice-to-have, note pour V2

---

## Key Architecture Decisions

| Decision | Choix | Rationale |
|----------|-------|-----------|
| Modele du juge | GPT-4o-mini | Cout faible (~$0.01 pour 20 questions), suffisant pour du scoring structure avec JSON mode. Si l'eval dit NO-GO, on upgrade vers GPT-4o. |
| Input format | CSV (question, expected_answer, criteria_level) | Format universel, zero learning curve, exportable depuis n'importe quel spreadsheet. |
| Scoring method | LLM-as-judge generique avec structured output (JSON) | Un seul juge pour tous les types d'IA — c'est le CSV qui definit ce que "correct" veut dire, pas le juge. |
| Appel endpoint | HTTP POST configurable (URL + headers + mapping champs) | Couvre FastAPI, Flask, Express, n'importe quel backend REST. Le PM configure quel champ envoyer et quel champ lire dans la reponse. |
| Backend | FastAPI (Python) | Meme stack que les 4 projets precedents. |
| Frontend | Lovable (React + Tailwind) | Meme stack. |
| Deploy | Render ($7/mo) | Meme stack. |

---

## Dependance externe et risque

| Dependance | Risque | Mitigation |
|------------|--------|-----------|
| OpenAI API (pour le juge) | Si l'API est lente ou down, EvalKit ne peut pas scorer | Timeout par question (30s) + message clair a l'utilisateur. Le scoring n'est pas temps-reel — 60s de latence totale est acceptable. |
| Endpoint utilisateur | Si l'endpoint de l'utilisateur est down ou lent, EvalKit ne peut pas tester | Timeout par appel (30s) + rapport partiel (les questions qui ont repondu sont scorees, les autres marquees "timeout"). |

---

## Adversarial Test Cases

> Le Walking Skeleton DOIT inclure au moins 1 cas difficile pour le juge.

| Cas | Pourquoi c'est dur | Attendu |
|-----|-------------------|---------|
| Reponse partiellement correcte : "$76,000" au lieu de "$76,381" | Le juge doit distinguer PARTIAL (bon ordre de grandeur) de CORRECT (exact). | PARTIAL, pas CORRECT |
| Reponse correcte mais mal formulee : "environ 76K" au lieu de "$76,381.39" | Le juge doit reconnaitre que le fond est correct malgre la forme. | CORRECT ou PARTIAL selon la tolerance definie |
| Hallucination flagrante : "Le revenue 2023 est de $2.4M" (absent des donnees) | Le juge doit detecter une invention. | HALLUCINATION |
| Reponse vide ou erreur : "Je ne peux pas repondre" | Le juge ne doit pas scorer ca comme INCORRECT mais comme un refus (correct si la question est adversariale). | Depend du expected_answer dans le CSV |
| Le juge juge le juge : soumettre un scoring volontairement faux | Meta-test : est-ce que le juge donne CORRECT a une reponse clairement fausse ? | INCORRECT — si le juge dit CORRECT, c'est un bug du juge |

---

## Open Questions

1. **GPT-4o-mini vs GPT-4o comme juge :** Est-ce que GPT-4o-mini est assez fiable pour scorer, ou faut-il GPT-4o (plus cher mais plus precis) ? Le Walking Skeleton tranchera — c'est la Riskiest Assumption.

2. **Format d'endpoint configurable :** Comment gerer les endpoints qui ne sont pas un simple `POST /ask` ? Certaines APIs attendent un champ `query`, d'autres `question`, d'autres `input`. Le mapping request/response doit etre configurable. A designer dans le WS.

3. **Meta-evaluation :** Comment verifier que le juge ne dit pas "CORRECT" a tout ? Prevoir des cas adversariaux dans le golden dataset de test d'EvalKit lui-meme. Le cas adversarial #5 ci-dessus couvre ca.
