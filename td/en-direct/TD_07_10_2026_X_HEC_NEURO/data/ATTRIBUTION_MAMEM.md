# Attribution et licence — données MAMEM utilisées dans le TD

Les fichiers `data/processed/*.npz` sont un petit sous-ensemble transformé de :

**MAMEM SSVEP Database v1.0.0 — Experiment 3**  
Source : https://physionet.org/content/mssvepdb/1.0.0/  
Experiment 3 : https://physionet.org/content/mssvepdb/1.0.0/dataset3/  
DOI : https://doi.org/10.13026/C29591

La page PhysioNet indique pour les fichiers la licence :

**Open Data Commons Attribution License v1.0 (ODC-By-1.0)**  
https://opendatacommons.org/licenses/by/1-0/

Notice d'attribution :

> Contains information from the MAMEM SSVEP Database, which is made available under the Open Data Commons Attribution License v1.0.

Lorsque vous utilisez ou redistribuez ces données, conservez cette notice et le lien de licence.

## Citation originale demandée par PhysioNet

V. P. Oikonomou, G. Liaros, K. Georgiadis, E. Chatzilari, K. Adam, S. Nikolopoulos, I. Kompatsiaris.  
*Comparative evaluation of state-of-the-art algorithms for SSVEP-based BCIs.*  
arXiv:1602.00904, 2016.

## Citation PhysioNet

PhysioNet demande également de citer la plateforme PhysioNet selon la citation affichée sur la page du dataset.

## Ce que contient notre dérivé pédagogique

- Sujet 1 : sessions A+B pour le réglage ; session C pour le test/jeu.
- Sujet 2 : session C pour le test de généralisation.
- Les 14 canaux EEG sont conservés.
- Fréquence d'échantillonnage : 128 Hz.
- Convention pédagogique : `JUMP = cible ~12 Hz`, `NONE = repos ou autre cible`.

Cette notice concerne la licence des données. Le code du TD peut avoir une licence distincte au niveau du dépôt principal.
