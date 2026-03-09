# Build Walkthrough — Scope 2 : Le produit fini

> EvalKit — "Frontend, demo mode, deploy"

## Ce qu'on a ajoute

Le Scope 1 avait un pipeline complet mais accessible uniquement en ligne de commande (via curl ou un outil comme Postman). Le Scope 2 transforme ca en produit utilisable : une interface web ou n'importe qui peut tester son IA en quelques clics.

Trois ajouts majeurs :
1. **Une interface web** (construite avec Lovable) avec upload de CSV, configuration d'endpoint, et affichage des resultats
2. **Un mode demo** pour tester sans avoir d'API — EvalKit fournit un faux endpoint et un jeu de questions integre
3. **Le deploiement** sur Render pour que le produit soit accessible a tous

## Le probleme de la poule et de l'oeuf

Le Scope 2 a revele un probleme UX qu'on n'avait pas anticipe : pour utiliser EvalKit, il faut deja avoir un endpoint AI deploye ET un fichier CSV de questions. C'est beaucoup a demander a quelqu'un qui decouvre l'outil.

La solution : un **mode demo**. EvalKit embarque un faux endpoint (qui simule une IA repondant a des questions sur un document business) et un jeu de 8 questions pre-definies. L'utilisateur clique "Try with demo data", attend 15 secondes, et voit un rapport complet — sans rien configurer.

Le mock inclut volontairement un cas de hallucination (l'IA invente un chiffre de revenue qui n'existe pas dans le document) pour que le resultat soit NO-GO. Ca montre immediatement la valeur d'EvalKit : le juge detecte l'hallucination et bloque le ship.

## L'interface a deux chemins

```
Page d'accueil
      │
      ├── "Try with demo data"          ├── "Test your own AI"
      │                                  │
      │   Zero config                    │   Upload CSV
      │   Clic → resultats              │   Entrer URL endpoint
      │                                  │   Config champs (question/answer)
      │                                  │   Clic "Run Eval"
      │                                  │
      └──────────── Resultats ───────────┘
                      │
              Verdict banner (GO / CONDITIONAL GO / NO-GO)
              Score cards (BLOCKING / QUALITY / SIGNAL)
              Resultats detailles par question
```

## Ce qui a merde (et ce qu'on a appris)

**1. L'URL de l'endpoint, c'est un piege UX.**
Mehdi a entre `https://docuquery-ai-5rfb.onrender.com` au lieu de `https://docuquery-ai-5rfb.onrender.com/query`. Resultat : 404. Sa reaction : "Si je me trompe, tout le monde va se tromper." On a ajoute un helper text qui dit d'inclure le path complet (ex: `/query`, `/ask`, `/chat`). C'est un rappel que les PMs ne sont pas des devs — ce qui semble evident pour un developpeur est un piege pour l'utilisateur cible.

**2. Les virgules dans les CSV, c'est traitre.**
Le parser CSV du frontend coupait `"$3,600"` en deux colonnes (`$3` et `600`). Le probleme : les virgules a l'interieur des guillemets doivent etre ignorees. C'est la spec CSV standard (RFC 4180), mais le parser initial ne la respectait pas. Fix rapide, mais un bon rappel qu'il faut tester avec des donnees reelles, pas juste des cas simples.

**3. Les resultats sans contexte, c'est du bruit.**
La premiere version de la page de resultats affichait les scores BLOCKING / QUALITY / SIGNAL sans explication. Mehdi a dit : "Je me mets a la place de quelqu'un qui n'est pas expert. Il ne sait pas ce que BLOCKING veut dire." On a ajoute des legendes sous chaque score card :
- BLOCKING → "Must pass. Any failure = NO-GO."
- QUALITY → "Should pass. Failures won't block release."
- SIGNAL → "Nice to have. Tracked for improvement."

Et un badge de couleur (rouge/jaune/bleu) sur chaque question dans les resultats detailles, pour voir immediatement quel niveau de critere est concerne. La lecon : **les labels sont du jargon tant qu'ils ne sont pas expliques**.

**4. Le subtitle, c'est 4 iterations.**
"Get a verdict" — trop vague. "In 60 seconds" — pas une promesse qu'on peut tenir. "Evaluate your AI agent" — trop etroit (pas que des agents). "Evaluate your AI in seconds" — "ai ai" dans la phrase, lourd. Final : **"From 'I think it works' to 'I know it does.'"** — c'est la douleur du PM, pas une feature technique.

## Decisions prises

| Decision | Choix | Pourquoi |
|----------|-------|----------|
| Demo mode | Mock endpoint integre + 8 questions | Resout le chicken-and-egg. L'utilisateur voit la valeur sans rien configurer. |
| Preview CSV retiree | Decision PM | "Trop de noise." Le demo mode remplace l'utilite de la preview. |
| Legendes sur les scores | Toujours visibles, pas en tooltip | Si l'utilisateur doit hover pour comprendre, c'est qu'on a rate l'UX. |
| Badges criteres par question | Couleur + texte | Le PM veut voir d'un coup d'oeil quelles questions sont BLOCKING vs SIGNAL. |

## Micro-tests : 6/6 PASS

| Test | Critere | Resultat |
|------|---------|----------|
| S2-1 | Upload CSV | PASS — file picker fonctionne, colonnes detectees |
| S2-2 | Config endpoint | PASS — URL + request_field + response_field configurables, helper text ajoute |
| S2-3 | Run Eval | PASS — bouton fonctionne, loader subtil, resultats affiches |
| S2-4 | Affichage resultats | PASS — verdicts couleur, badges criteres, justifications |
| S2-5 | Verdict final | PASS — bandeau GO/CONDITIONAL GO/NO-GO + score cards avec legendes |
| S2-6 | Deploy | PASS — backend Render + frontend Lovable connectes |
