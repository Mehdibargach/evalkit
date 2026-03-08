# Build Walkthrough — Walking Skeleton

> EvalKit — "Le juge score 5 reponses"

## Ce qu'on a construit

Imagine que tu as cree une application qui utilise de l'IA — par exemple, un outil qui repond a des questions sur tes documents. Tu veux savoir si les reponses sont bonnes avant de le montrer a des vrais utilisateurs. Aujourd'hui, tu ferais ca a la main : poser des questions une par une, lire chaque reponse, noter dans un tableur. Ca prend des heures.

EvalKit fait ca pour toi. Tu lui donnes :
1. Un fichier CSV avec tes questions de test et les reponses attendues
2. L'adresse de ton application (son URL)

Et il te renvoie un verdict : GO (c'est bon), CONDITIONAL GO (ca passe mais avec des reserves), ou NO-GO (il y a un probleme bloquant).

## Comment ca marche

```
CSV (5 questions)           Ton application           Le juge (GPT-4o-mini)
      │                          │                           │
      ├── question 1 ──────────► │                           │
      │                          ├── reponse 1 ─────────────►│
      │                          │                           ├── CORRECT ✓
      ├── question 2 ──────────► │                           │
      │                          ├── reponse 2 ─────────────►│
      │                          │                           ├── CORRECT ✓
      ...                        ...                         ...
      │                                                      │
      └──────────────── Verdict final : GO / NO-GO ◄─────────┘
```

Le juge, c'est un deuxieme modele d'IA qui joue le role de correcteur. Comme un prof qui a le corrige (ta reponse attendue) et qui compare avec la copie de l'eleve (la reponse de ton application).

## Ce qu'on a teste (et les resultats)

On a teste EvalKit contre DocuQuery AI (un des projets precedents — un outil qui repond a des questions sur des documents PDF).

| # | Question | Reponse de DocuQuery | Verdict du juge | Coherent ? |
|---|----------|---------------------|----------------|------------|
| 1 | "Quel est le cout d'acquisition a 200 clients ?" | "$3,600" | CORRECT | Oui — le chiffre est exact |
| 2 | "Combien de transactions par seconde au lancement ?" | "10,000 TPS" | CORRECT | Oui — le chiffre est exact |
| 3 | "Resume les avantages de NovaPay" | Reponse detaillee (5 points) | PARTIAL | Oui — la reponse est bonne mais manque des details specifiques de l'attendu |
| 4 | "Quel etait le revenue Q4 2025 ?" (piege — l'info n'existe pas) | "Je n'ai pas assez d'information" | CORRECT | Oui — le refus est correct |
| 5 | Meme question que Q1, mais on a mis "$999" comme reponse attendue (faux expres) | "$3,600" (la vraie reponse) | INCORRECT | Oui — le juge n'a pas valide aveuglement |

**5/5 verdicts coherents avec le jugement humain.** Le juge est fiable.

## Ce qui a merde

Pas grand-chose sur ce Walking Skeleton. Un seul bug technique :

Le fichier qui contient la cle API (comme un mot de passe pour acceder au service d'IA) n'etait pas lu au bon moment. Le programme essayait de se connecter a OpenAI avant d'avoir lu le mot de passe. Fix simple : lire le fichier de configuration plus tot dans le code.

## Decisions prises

| Decision | Choix | Pourquoi |
|----------|-------|----------|
| Modele du juge | GPT-4o-mini | Suffisant pour comparer reponse vs attendu. Pas besoin du modele le plus cher. |
| Temperature | 0 (= pas de creativite) | On veut que le juge soit le plus deterministe possible — meme question = meme score |
| Format de sortie | JSON structure | Le juge retourne toujours le meme format : verdict + justification. Pas d'ambiguite. |
| Appels paralleles | Oui | Les 5 questions sont envoyees en meme temps. 25.7 secondes au total au lieu de ~100 secondes en sequentiel. |

## Micro-tests : 7/7 PASS

| Test | Critere | Resultat |
|------|---------|----------|
| WS-1 | CSV parsing (3 colonnes, 5 lignes) | PASS |
| WS-2 | Appel endpoint (5 reponses, zero erreur) | PASS |
| WS-3 | Scoring correcte (2 factuelles → CORRECT) | PASS |
| WS-4 | Scoring partielle (synthese → PARTIAL) | PASS |
| WS-5 | Scoring refus (adversariale → CORRECT) | PASS |
| WS-6 | Meta-test (expected faux → INCORRECT) | PASS |
| WS-7 | Justification (5/5 justifiees) | PASS |

## Skeleton Check

**La Riskiest Assumption tient-elle ?** Oui. GPT-4o-mini est un juge fiable — 4/4 verdicts coherents avec le jugement humain (seuil : 3/4). Et bonus : la decision Eval Gate a fonctionne aussi (le meta-test a declenche un NO-GO, comme attendu).

**→ GO pour le Scope 1.**
