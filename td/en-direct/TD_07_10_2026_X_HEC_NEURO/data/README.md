# Données du TD

Le notebook lit trois fichiers préparés, **déjà inclus dans le dépôt** :

- `processed/sub-01_tune.npz` — sujet 1, sessions A+B : réglage de la fenêtre et du seuil ;
- `processed/sub-01_game.npz` — sujet 1, session C : test held-out + replay gamifié ;
- `processed/sub-02_generalization.npz` — sujet 2, session C : bonus généralisation.

## Pour les étudiants

Vous ne téléchargez ni ne convertissez aucune donnée EEG pendant la séance.

`python setup_students.py` vérifie simplement que ces trois fichiers sont présents et lisibles,
puis prépare les bibliothèques Python nécessaires.

## Source

MAMEM SSVEP Database v1.0.0 — Experiment 3  
PhysioNet : https://physionet.org/content/mssvepdb/1.0.0/dataset3/  
DOI : https://doi.org/10.13026/C29591

Voir `ATTRIBUTION_MAMEM.md` pour la licence et les citations.
