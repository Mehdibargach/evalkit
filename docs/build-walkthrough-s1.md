# Build Walkthrough — Scope 1 : Le pipeline complet

> EvalKit — "20 questions, scoring agrege, verdict automatique"

## Ce qu'on a ajoute

Le Walking Skeleton prouvait que le juge fonctionne sur 5 questions. Le Scope 1 passe a l'echelle : 20 questions, avec des scores agreges par niveau de critere et un verdict automatique.

Rappel rapide : dans EvalKit, chaque question de test est taguee avec un niveau de critere :
- **BLOCKING** : si ca rate, c'est un mur. Pas de negociation.
- **QUALITY** : si ca rate, c'est un warning. On peut shipper avec des reserves.
- **SIGNAL** : si ca rate, on note pour plus tard. Pas bloquant.

Le Scope 1 ajoute la logique qui transforme ces niveaux en une decision automatique.

## Comment ca marche maintenant

```
CSV (20 questions)                         EvalKit
      │                                       │
      ├── 20 questions en parallele ────────► Endpoint
      │                                       │
      │◄─── 20 reponses ─────────────────────┤
      │                                       │
      ├── 20 paires (reponse vs attendu) ──► Juge GPT-4o-mini
      │                                       │
      │◄─── 20 verdicts + justifications ────┤
      │                                       │
      │                              Scores agreges :
      │                              BLOCKING : 6/8 (75%)
      │                              QUALITY  : 7/8 (87.5%)
      │                              SIGNAL   : 3/4 (75%)
      │                                       │
      │                              Failure patterns :
      │                              - 1 HALLUCINATION
      │                              - 3 INCORRECT
      │                              - 3 PARTIAL
      │                                       │
      │                              Decision : NO-GO
      │                              (2 BLOCKING fails)
      └───────────────────────────────────────┘
```

## Les resultats concrets

On a teste avec 20 questions contre DocuQuery AI (l'outil de questions-reponses sur des documents). Le dataset incluait :
- 6 questions factuelles avec des chiffres precis ("$3,600", "10,000 TPS")
- 2 meta-tests (on a mis expres une mauvaise reponse attendue pour verifier que le juge ne dit pas "oui" a tout)
- 8 questions ouvertes ("Resume les avantages...", "Quelle est la strategie ?")
- 4 questions absurdes ou hors-sujet ("Quel temps fait-il au lancement ?")

**Resultat : 47.4 secondes pour les 20 questions.** C'est sous la barre des 60 secondes.

**Accord juge vs humain : 90% (18/20).** Deux cas limites :
- Le juge a ete trop strict sur une question de migration (il a note INCORRECT alors que la reponse decrivait bien le concept, juste avec des mots differents)
- Le juge a note HALLUCINATION sur une question technique ou l'expected etait trop vague

## Ce qui a merde (et ce qu'on a appris)

**Les expected_answers vagues donnent des verdicts moins fiables.** Quand on ecrit `expected: "$3,600"`, le juge sait exactement quoi verifier. Quand on ecrit `expected: "The document should describe the migration strategy"`, le juge doit interpreter — et parfois il se trompe.

C'est une lecon importante pour les utilisateurs d'EvalKit : **plus tes reponses attendues sont precises, plus les verdicts du juge sont fiables.** Ecrire des expected concrets, c'est le job du PM — et c'est la ou sa connaissance du produit fait la difference.

## Decisions prises

| Decision | Choix | Pourquoi |
|----------|-------|----------|
| PARTIAL = PASS | Oui | Un PARTIAL c'est "sur la bonne piste". Ca ne doit pas bloquer le ship. Coherent avec la methode. |
| Failure patterns par type de verdict | Pas par sujet | Plus simple et plus utile : "tu as 3 INCORRECT" > "tu as 2 questions sur le pricing qui ratent". Le PM voit le pattern de defaut, pas le sujet. |
| Meta-tests dans le dataset | 2 questions avec expected faux | Verifie que le juge ET l'Eval Gate fonctionnent ensemble. Les 2 meta-tests ont bien declenche NO-GO. |

## Micro-tests : 8/8 PASS

| Test | Critere | Resultat |
|------|---------|----------|
| S1-1 | Appels paralleles < 60s | PASS (47.4s) |
| S1-2 | Scores agreges par niveau | PASS (verifie manuellement) |
| S1-3 | Eval Gate NO-GO | PASS (2 BLOCKING fails → NO-GO) |
| S1-4 | Eval Gate CONDITIONAL GO | PASS (logique verifiee) |
| S1-5 | Eval Gate GO | PASS (logique verifiee) |
| S1-6 | Failure patterns | PASS (3 groupes identifies) |
| S1-7 | Eval Report structure | PASS (4 sections presentes) |
| S1-8 | Accord juge vs humain >= 80% | PASS (90%) |
