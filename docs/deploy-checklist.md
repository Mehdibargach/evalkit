# Deploy Checklist — EvalKit

> Template from The Builder PM Method — SHIP phase

**Project Name:** EvalKit
**Deploy Date:** 2026-03-09

---

## Infrastructure

- [x] Application deployed — API endpoint: `https://evalkit-vw7k.onrender.com`
- [x] Web interface deployed — URL: `https://the-evalkit.lovable.app`
- [x] Environment variables set (OPENAI_API_KEY on Render)
- [x] CORS configured (Lovable origin autorisee)

## Pre-Deploy Gate

- [x] Eval Gate passed — **GO** (5/5 Success Metrics PASS, zero condition)

## Quality

- [x] Error handling : timeout par question (30s), message clair si endpoint down
- [x] Teste sur mobile (two-path landing responsive)
- [x] Teste sur Chrome, Safari (minimum)
- [x] Aucune API key exposee dans le code client (cles cote backend uniquement)

## Documentation

- [x] README a jour avec demo link
- [x] Build Log complete (WS + S1 + S2)
- [x] Architecture reflete l'etat final (CLAUDE.md a jour)

## Post-Deploy

- [x] Demo URL fonctionne end-to-end : `/demo` → NO_GO (15.6s), `/evaluate` GO dataset → GO (9s)
- [x] Demo mode : 8 questions built-in avec mock endpoint, zero-config tryout
- [x] PM a teste les deux paths (demo + custom eval)
