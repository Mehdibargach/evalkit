# Macro Retro — EvalKit

> Template from The Builder PM Method — POST-SHIP

---

**Project:** EvalKit
**Version shipped:** V1
**Eval Gate decision:** GO (5/5 PASS, zero condition)
**Date:** 2026-03-09

---

## 1. Harvest — What came out of the Eval Gate?

### Conditions (from GO)

Aucune condition. Eval Gate = GO sans reserve.

| # | Observation | Level | Impact |
|---|-------------|-------|--------|
| 1 | Expected vagues donnent des verdicts moins fiables (Q11, Q16 dans S1) | SIGNAL | Le PM doit ecrire des expected precis — c'est une contrainte utilisateur, pas un bug produit |
| 2 | PARTIAL compte comme PASS dans les scores agreges | SIGNAL | Choix de design valide pour V1, a monitorer si des utilisateurs le contestent |

### Build Learnings (from Build Log)

- **Le CSV est le contrat.** L'approche generique fonctionne : le meme juge score du factuel, de la synthese, des refus, des cas adversariaux. Pas besoin de mode par typologie. Insight transferable a tout produit AI qui prend des donnees utilisateur en entree.
- **Demo mode resout le chicken-and-egg.** Sans demo, l'onboarding demande un endpoint + un CSV. Trop de friction. Le demo mode avec 1 hallucination integree (→ produit un NO-GO) est la meilleure explication du produit.
- **Les labels sont du jargon tant qu'ils ne sont pas expliques.** BLOCKING / QUALITY / SIGNAL sont evidents apres 5 projets, opaques pour un nouvel utilisateur. Legendes obligatoires.

### User/PM Signals (from wild tests, demos, feedback)

- Le PM s'est trompe sur l'endpoint URL du premier coup ("/query" oublie). Insight : "si je me trompe, tout le monde va se tromper" → helper text ajoute.
- Le subtitle final ("From 'I think it works' to 'I know it does.'") a necessite 4 iterations — signe que le positionnement produit demande autant de soin que le code.
- EvalKit utilise par EvalKit pour les 4 projets precedents (meta-evaluation) : la methode se boucle.

---

## 2. Decision — What do we do next?

| Decision | When to use |
|----------|-------------|
| ITERATE (V+1) | Au moins une condition vaut d'etre fixee ET le produit a plus de valeur a debloquer |
| **STOP** | **Le produit est assez bon pour son objectif. Les conditions sont mineures ou ne valent pas l'investissement.** |
| PIVOT | L'hypothese fondamentale etait fausse. |

**Decision : STOP**

**Why (data-driven) :**
EvalKit est le 5eme et dernier side project du portfolio Builder PM. L'Eval Gate est GO sans condition — 90% accord juge-humain, zero hallucination, 37.7s latence, $0.01/run. Les 2 observations SIGNAL (expected vagues, PARTIAL=PASS) sont des contraintes utilisateur documentees, pas des bugs produit. Le ROI d'un V2 (dashboard, historique, multi-endpoint) est faible par rapport au cout d'opportunite : le temps restant doit aller au livre et au networking US. Les 5 typologies AI sont couvertes — le portfolio est complet.

---

## 3. Bridge

> Non applicable (decision = STOP).

---

## Completion

- [x] Eval Report reviewed (GO, 5/5 PASS)
- [x] Decision documentee avec justification
- [ ] Bridge section filled — N/A (STOP)
- [x] Project Dossier mis a jour avec la decision Macro Retro
- [x] CLAUDE.md mis a jour
