# Project Dossier — EvalKit

> Template from The Builder PM Method — post-SHIP

---

**Project Name:** EvalKit
**One-liner:** Teste les reponses de ton IA — CSV in, verdict GO / NO-GO out.
**Live URL:** https://the-evalkit.lovable.app
**Backend:** https://evalkit-vw7k.onrender.com
**GitHub:** github.com/Mehdibargach/evalkit
**Date Shipped:** 2026-03-09

---

## 1-Pager Summary

**Problem :** Les PMs qui buildent des produits AI evaluent la qualite au feeling ("vibe check") ou dans un spreadsheet (2-4h, zero diagnostic). Les outils existants (DeepEval, Ragas, Braintrust) sont faits pour les devs. Aucun outil ne permet a un PM de tester son API en 15 minutes sans ecrire de code.

**User :** Builder PM / solo builder avec un produit AI deploye. Builde avec du vibe coding, n'ecrit pas de scripts Python.

**Solution :** Upload un CSV (question + expected + criteria_level), donne l'URL de ton endpoint, clique. Un LLM-juge score chaque reponse (CORRECT / PARTIAL / INCORRECT / HALLUCINATION), classe les criteres (BLOCKING / QUALITY / SIGNAL), et genere un verdict GO / CONDITIONAL GO / NO-GO automatique.

---

## Architecture Diagram

```
┌─────────────┐     ┌──────────────────────────────────────┐
│  Frontend   │     │         Backend (FastAPI)             │
│  Lovable    │────→│                                      │
│  React/TW   │     │  CSV parse → call user endpoint      │
└─────────────┘     │      ↓                               │
                    │  capture responses                    │
                    │      ↓                               │
                    │  LLM judge (GPT-4o-mini)             │
                    │  compare actual vs expected           │
                    │      ↓                               │
                    │  aggregate scores                     │
                    │  BLOCKING / QUALITY / SIGNAL          │
                    │      ↓                               │
                    │  Eval Gate → GO / COND GO / NO-GO    │
                    └──────────────────────────────────────┘
```

---

## Key ADRs

| Decision | Choix | Why |
|----------|-------|-----|
| Modele du juge | GPT-4o-mini | Cout ~$0.01/run, suffisant pour scoring structure avec JSON mode. 90% accord humain prouve. |
| Scoring method | LLM-as-judge generique | Un seul juge pour tous les types d'IA. Le CSV est le contrat — le PM definit "correct". Pas de mode par typologie. |
| Input format | CSV (question, expected_answer, criteria_level) | Format universel, zero learning curve, exportable depuis tout spreadsheet. |
| Demo mode | Mock endpoint + 8 questions built-in | Resout le chicken-and-egg : l'utilisateur peut tester sans avoir d'API. Inclut 1 hallucination → produit un NO-GO. |

---

## Eval Results

| Metric | Target | Actual | Level | Verdict |
|--------|--------|--------|-------|---------|
| Accord juge vs humain | >= 80% | **90% (18/20)** | BLOCKING | PASS |
| Temps total 20 questions | < 60s | **37.7s** | BLOCKING | PASS |
| Zero auto-hallucination juge | 0 cas | **0** | BLOCKING | PASS |
| Decision Eval Gate correcte | 100% coherence | **100%** | QUALITY | PASS |
| Cout par run | < $0.05 | **~$0.01** | SIGNAL | PASS |

**Decision Eval Gate : GO** — Zero condition, zero reserve.

---

## What I Learned

1. **Technical :** Le CSV est le contrat. L'approche generique (un juge, pas un mode par typologie) fonctionne parce que c'est le PM qui definit ce que "correct" veut dire dans ses expected_answers. Plus les expected sont precis ("$3,600"), plus le juge est fiable. Les expected vagues ("should describe...") laissent trop de marge d'interpretation.

2. **Product :** Le demo mode resout l'onboarding. Sans demo, l'utilisateur a besoin d'un endpoint + un CSV — trop de friction. Avec demo, il clique et voit un rapport en 15 secondes. Les labels (BLOCKING / QUALITY / SIGNAL) sont du jargon tant qu'ils ne sont pas expliques — legendes obligatoires.

3. **Process :** Les micro-tests BUILD prouvent que les features marchent. L'eval prouve que le produit est assez bon. Ce sont deux choses differentes — 22/22 micro-tests PASS ne garantissent pas 90% d'accord juge-humain. Le PM doit ecrire le golden dataset lui-meme. C'est la que sa connaissance metier fait la difference.

---

## Content Extracted

- [x] Book chapter : Ch.4 (AI Evaluation tooling typology) + Ch.6 (meta-evaluation — EvalKit evalue EvalKit)
- [x] LinkedIn post : "From 'I think it works' to 'I know it does'" — EvalKit case study
- [x] STAR story : "Built an AI evaluation tool in 4 hours that achieves 90% agreement with human judgment"
- [ ] Newsletter : article Substack sur le Eval Gate framework (BLOCKING / QUALITY / SIGNAL)
