#!/usr/bin/env python3
"""Préparation étudiante en une commande.

Ce script :
1) installe/vérifie les bibliothèques Python du TD ;
2) vérifie que les trois fichiers EEG préparés sont déjà inclus dans le repo ;
3) affiche la suite.

Il ne télécharge AUCUNE donnée EEG pendant la séance.
"""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

print("1/2 — Vérification de Python et des bibliothèques…")
subprocess.check_call([
    sys.executable, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")
])

needed = [
    ROOT / "data/processed/sub-01_tune.npz",
    ROOT / "data/processed/sub-01_game.npz",
    ROOT / "data/processed/sub-02_generalization.npz",
]

print("\nVérification des bibliothèques importables…")
for module in ("numpy", "matplotlib", "pygame", "ipykernel"):
    __import__(module)
    print("   ✓", module)

print("\n2/2 — Vérification des données EEG du TD…")
missing = [p for p in needed if not p.exists() or p.stat().st_size == 0]
if missing:
    print("\n❌ Le dossier distribué est incomplet : les données EEG préparées manquent.")
    print("   Aucun téléchargement étudiant n'est prévu pendant la séance.")
    print("   Fichiers attendus dans data/processed/ :")
    for p in needed:
        print("   -", p.name)
    print("\n→ Appelez l'enseignant : il doit distribuer la version du repo contenant ces 3 fichiers.")
    sys.exit(2)

from _engine.data import load_npz
for p in needed:
    ds = load_npz(p)
    print(f"   ✓ {p.name}: {len(ds.eeg):,} échantillons, "
          f"{len(ds.channels)} canaux, {ds.sfreq:g} Hz")

print("\n✅ Tout est prêt.")
print("\nChemin recommandé — VS Code :")
print("  1. Ouvrez 01_TD_SSVEP_GAME.ipynb.")
print("  2. Si demandé, installez les extensions Microsoft Python + Jupyter.")
print("  3. Cliquez sur 'Select Kernel' et choisissez ce Python :")
print(f"     {sys.executable}")
print("  4. Exécutez les cellules de haut en bas.")
print("\nPlan B — JupyterLab :")
print(f'  "{sys.executable}" -m jupyterlab')
print("  puis ouvrez 01_TD_SSVEP_GAME.ipynb")
