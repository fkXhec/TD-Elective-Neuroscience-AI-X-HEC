# TD BCI SSVEP — guide étudiant

## Ce que vous allez faire

Vous allez utiliser un **vrai EEG déjà enregistré avec un casque Emotiv** pour reconstruire une petite BCI transparente :

```text
EEG enregistré
→ score SSVEP
→ décision JUMP / NONE
→ contrôleur
→ mini-jeu
```

L'objectif n'est pas de programmer toute une BCI.  
Vous allez surtout **changer deux réglages**, observer leurs conséquences, puis expliquer votre compromis.


> Ancienne version du TD centrée sur un bras robotique : [archive/robot-v1/README.md](archive/robot-v1/README.md).
> Elle est conservée comme archive et n'est plus le parcours à suivre en séance.

> **Pendant le TD, vous utilisez seulement deux fichiers :**
>
> 1. `README.md` — ce guide ;
> 2. `01_TD_SSVEP_GAME.ipynb` — le notebook à exécuter.
>
> Les autres fichiers sont utilisés automatiquement.

---

# 1 — Récupérer le dossier du cours

Dépôt GitHub :

**https://github.com/fkXhec/TD-Elective-Neuroscience-AI-X-HEC**

### Si vous n'utilisez pas Git

1. ouvrez le lien GitHub ;
2. bouton vert **Code** ;
3. **Download ZIP** ;
4. décompressez le ZIP ;
5. ouvrez le dossier :

```text
TD-Elective-Neuroscience-AI-X-HEC-main/
└── td/
    └── en-direct/
```

### Si vous utilisez déjà Git

```bash
git clone https://github.com/fkXhec/TD-Elective-Neuroscience-AI-X-HEC.git
cd TD-Elective-Neuroscience-AI-X-HEC/td/en-direct
```

---

# 2 — Ouvrir le TD dans VS Code — chemin recommandé

## VS Code n'est pas installé ?

Téléchargement officiel :

**https://code.visualstudio.com/download**

## Python est-il installé ?

Dans un terminal :

```bash
python --version
```

Sous Windows, si cette commande ne marche pas :

```powershell
py --version
```

Il faut Python 3.10 ou plus récent.

Si nécessaire :

**https://www.python.org/downloads/**

## Ouvrir le bon dossier

Dans VS Code :

1. **File → Open Folder…**
2. choisissez le dossier `td/en-direct`;
3. vous devez voir à gauche :

```text
README.md
01_TD_SSVEP_GAME.ipynb
setup_students.py
requirements.txt
_engine/
data/
```

Pour lire ce README avec la mise en page :

- Windows/Linux : `Ctrl + Shift + V`
- macOS : `Cmd + Shift + V`

## Extensions VS Code

Si VS Code les propose, installez :

- **Python** — Microsoft
- **Jupyter** — Microsoft

---

# 3 — Préparer l'environnement — une commande

Dans VS Code :

**Terminal → New Terminal**

Puis :

```bash
python setup_students.py
```

Sous Windows, si `python` n'est pas reconnu mais `py` fonctionne :

```powershell
py setup_students.py
```

### À quoi sert cette commande ?

Elle :

- installe/vérifie les bibliothèques Python ;
- vérifie que les **trois EEG du TD inclus dans le repo sont bien présents** ;
- vérifie que Python arrive à les lire.

**Elle ne télécharge aucune donnée EEG : les trois fichiers nécessaires sont déjà inclus dans `data/processed/`.**

À la fin, vous devez voir :

```text
✅ Tout est prêt.
```

---

# 4 — Ouvrir le notebook

Ouvrez :

**`01_TD_SSVEP_GAME.ipynb`**

En haut à droite, VS Code peut afficher **Select Kernel**.

Choisissez le Python indiqué à la fin de `setup_students.py`.

> **Kernel / noyau Python** = le Python qui exécute les cellules du notebook.

Ensuite, exécutez les cellules dans l'ordre :

- bouton ▶ ;
- ou `Shift + Entrée`.

Vous ne modifiez que les cellules marquées :

**✏️ À VOUS**

---

# 5 — Plan B : JupyterLab

Si VS Code ou ses extensions posent problème, utilisez le navigateur.

Depuis `td/en-direct` :

```bash
python setup_students.py
python -m jupyterlab
```

Puis cliquez sur :

**`01_TD_SSVEP_GAME.ipynb`**

Sous Windows, `python -m jupyterlab` est préférable à `jupyter lab` : il évite des problèmes lorsque plusieurs installations Python coexistent.

---

# 6 — Quels fichiers servent à quoi ?

## Vous utilisez vraiment

| Fichier | Votre action |
|---|---|
| `README.md` | le garder ouvert comme guide |
| `01_TD_SSVEP_GAME.ipynb` | exécuter les cellules et modifier les cellules **✏️ À VOUS** |

## Utilisés automatiquement

| Fichier / dossier | Faut-il l'ouvrir ? | Rôle |
|---|---:|---|
| `setup_students.py` | seulement le lancer une fois | prépare Python et vérifie les données |
| `requirements.txt` | non | liste technique des bibliothèques |
| `_engine/` | non | contient CCA, fenêtres, métriques, contrôleur et jeu |
| `data/processed/` | non | contient les trois EEG préparés |
| `data/ATTRIBUTION_MAMEM.md` | facultatif | source scientifique et licence des données |

Si vous êtes perdu : **revenez au README puis au notebook**.

---

# 7 — Les données utilisées

Nous utilisons un sous-ensemble du **MAMEM SSVEP Dataset III**.

À retenir :

- EEG enregistré avec **14 canaux Emotiv EPOC** ;
- fréquence d'échantillonnage : **128 Hz** ;
- 11 participants dans l'étude complète ;
- cinq cibles visuelles présentées simultanément ;
- fréquences nominales : **6.66 / 7.5 / 8.57 / 10 / 12 Hz**.

Pour le TD, nous transformons ce protocole en une commande simple :

| Étiquette du TD | Signification |
|---|---|
| **JUMP** | le participant portait son attention sur la cible 12 Hz |
| **NONE** | repos ou attention à une autre cible |
| **IGNORE** | zone proche d'une transition ; non utilisée pour régler ou évaluer le système |

**NONE n'est pas un “état cérébral neutre universel”.**  
C'est une classe de contrôle pratique pour notre mini-jeu.

---

# 8 — Pourquoi O1 et O2 ?

Nous commençons avec deux canaux postérieurs :

```text
O1 + O2
```

Le paradigme est visuel ; commencer près des régions occipitales est donc une hypothèse raisonnable.

Plus tard, si vous avez le temps, vous pourrez comparer :

```text
O1 + O2
```

à :

```text
P7 + O1 + O2 + P8
```

---

# 9 — Le score CCA, sans jargon inutile

Le stimulus visuel possède une fréquence connue : **12 Hz**.

Le programme construit donc des signaux théoriques à 12 Hz et à certaines harmoniques, puis pose une question :

> **Est-ce qu'une combinaison de nos canaux EEG ressemble à une combinaison de ces signaux périodiques ?**

CCA produit alors un **score de compatibilité**.

On peut résumer l'idée par :

```text
score_12Hz = meilleure corrélation entre
             une combinaison de l'EEG
             et une combinaison des références périodiques
```

Important :

```text
score = 0.70
```

ne signifie pas :

```text
70 % de probabilité que la personne veuille sauter
```

Le score doit encore être transformé en décision.

---

# 10 — Vos deux réglages

## 1. La durée de fenêtre

`window_s`

C'est la quantité de passé EEG utilisée pour produire un score.

Exemple :

```text
window_s = 2.0
```

signifie :

> pour décider maintenant, utiliser les 2 dernières secondes d'EEG.

En général :

- fenêtre courte → plus rapide, mais plus instable ;
- fenêtre longue → plus d'information, mais plus de délai.

## 2. Le seuil

`threshold`

Il transforme le score en décision :

```text
score ≥ seuil  → JUMP
score < seuil  → NONE
```

En général :

- seuil faible → sensible mais plus de faux JUMP ;
- seuil élevé → prudent mais plus de NONE / commandes ratées.

---

# 11 — Règle scientifique du TD

Vous disposez d'abord d'un fichier de **réglage**.

Vous pouvez y tester plusieurs fenêtres et plusieurs seuils.

Puis :

```text
🔒 LOCK PARAMETERS
```

Vous ne modifiez plus vos choix.

Ils sont ensuite appliqués à :

1. une autre session de la même personne ;
2. en bonus, une autre personne.

Cela évite de choisir les paramètres après avoir vu le résultat du test.

---

# 12 — Offline, replay et causalité

Le fichier EEG complet existe déjà.

Mais le jeu le révèle progressivement :

```text
passé disponible | présent | futur interdit
```

À l'instant `t`, le décodeur utilise uniquement une fenêtre du passé.

C'est ce qu'on appelle ici un **replay causal**.

Le jeu utilise les annotations du dataset pour :

- savoir quand créer un obstacle ;
- savoir ensuite si votre décision était correcte.

Mais :

> **les labels ne sont jamais fournis au décodeur.**

Le décodeur reçoit uniquement l'EEG.

---


### Fenêtres, événements et jeu : trois niveaux à ne pas confondre

1. **Score CCA** : un nombre à chaque fenêtre EEG.
2. **Décision / contrôleur** : `JUMP/NONE`, confirmation, one-shot et cooldown.
3. **Jeu** : visualisation de cinq blocs cibles.

Les métriques `HELD-OUT` portent sur la session complète.  
Le jeu compact sert à voir la boucle fonctionner, pas à remplacer cette évaluation.


# 13 — Le mini-jeu

Le replay du jeu est volontairement compact.

Au lieu de rejouer plusieurs minutes d'EEG, il conserve de courts extraits autour des **5 vrais blocs 12 Hz**.

Résultat attendu :

- environ 5 rounds ;
- partie typique de 15–25 secondes ;
- replay accéléré x3 ;
- barre violette = score CCA ;
- trait vert = seuil ;
- `ESC` ou `Q` = quitter.

Les scores CCA ont néanmoins été calculés causalement sur la chronologie EEG originale.

Avant le jeu, le notebook calcule deux familles de métriques sur la **session held-out complète** :

- métriques **par fenêtre** : hit rate, false positive rate, balanced accuracy ;
- métriques **contrôleur / événements** : blocs cibles détectés, faux JUMP, actions et latence.

Le mini-jeu affiche ensuite une version **compacte** de cinq événements pour rendre la boucle visible.
Ses faux JUMP ne concernent donc que les extraits montrés à l'écran ; ils ne remplacent pas l'évaluation held-out complète.

### Pourquoi le contrôleur n'émet-il pas plusieurs sauts pendant un même bloc ?

Un bloc SSVEP dure plusieurs secondes. Si le score reste au-dessus du seuil,
une règle naïve pourrait produire `JUMP, JUMP, JUMP...`.

Le contrôleur utilise donc un **verrou one-shot** :

```text
score élevé pendant plusieurs fenêtres
        ↓
une seule action JUMP
        ↓
contrôleur verrouillé
        ↓
le score doit revenir durablement à NONE
        ↓
contrôleur réarmé pour la cible suivante
```

Cette logique appartient à la couche **Decision / Control**, pas au décodeur CCA.

### Comment le jeu décide-t-il qu'un obstacle est franchi ?

Le dessin du saut est une animation. La réussite n'est **pas** décidée par une physique arbitraire.

Pour chaque bloc cible de 5 s, l'obstacle atteint le joueur à la fin du bloc :

```text
au moins un JUMP valide du contrôleur pendant le bloc
→ obstacle franchi

aucun JUMP valide
→ collision
```

Ainsi, la vitesse du replay ou la forme graphique du saut ne peuvent pas changer la performance BCI.
Le replay ×3 accélère uniquement l'affichage.

---


# 13 bis — Le challenge est identique pour tous

Le mini-jeu n'est **pas aléatoire** : tous les groupes utilisent la même session EEG de test, les mêmes 5 blocs cibles et la même physique du jeu.

Ce qui change d'un groupe à l'autre, ce sont uniquement les réglages qu'il a choisis sur les données de tuning :

```text
canaux + durée de fenêtre + seuil
                ↓
        décisions JUMP / NONE
                ↓
     performance dans le jeu
```

Cela permet de comparer les choix scientifiques entre groupes.

### Fixe pour tous

- même EEG held-out ;
- mêmes 5 obstacles ;
- même fréquence cible 12 Hz ;
- même confirmation et même contrôleur ;
- même physique du jeu.

### Choisi par votre groupe

- `FINAL_CHANNELS` ;
- `FINAL_WINDOW_S` ;
- `FINAL_THRESHOLD`.

### Conséquences mesurées

- blocs détectés / manqués ;
- faux JUMP ;
- latence ;
- obstacles franchis / collisions.

> **Le terrain est donc identique. La différence de score vient de votre pipeline, pas d'un jeu plus facile.**

Le ground truth sert seulement à savoir **quand créer les obstacles et comment évaluer votre résultat**. Il n'est jamais donné au décodeur CCA.

# 14 — Si le jeu ne démarre pas

Le jeu utilise la bibliothèque Python `pygame`.

Le notebook vérifie automatiquement si `pygame` est disponible dans **le Python du notebook**.

Si elle manque, il tente de l'installer dans ce même environnement.

Pourquoi cette précaution ?

Un ordinateur peut posséder plusieurs installations Python. Installer une bibliothèque dans un Python ne la rend pas automatiquement disponible dans un autre.

Si le problème persiste, vérifiez dans une cellule :

```python
import sys
print(sys.executable)
```

puis appelez l'enseignant.

---

# 15 — À la fin, votre groupe doit savoir expliquer

1. Pourquoi commencer avec O1/O2 ?
2. Qu'est-ce que le score CCA mesure intuitivement ?
3. Pourquoi un score CCA n'est-il pas une probabilité ?
4. Quel compromis avez-vous fait sur la durée de fenêtre ?
5. Quel compromis avez-vous fait sur le seuil ?
6. Quelle différence entre **score**, **décision** et **commande** ?
7. Pourquoi verrouiller les paramètres avant le test ?
8. Que devient la performance sur une autre session ?
9. Que se passe-t-il sur une autre personne ?

Une baisse de performance n'est pas un échec du TD.

C'est une observation sur la **généralisation** du système.

---

# Source des données

Voir :

`data/ATTRIBUTION_MAMEM.md`

Les fichiers distribués dans `data/processed/` sont des dérivés pédagogiques d'un sous-ensemble du MAMEM SSVEP Dataset III.


## Point important : pourquoi changer `window_s` ne change parfois pas immédiatement le jeu

Le notebook distingue volontairement **exploration** et **test final**.

Avant le verrouillage :

```text
window_s / threshold
= paramètres en cours d'essai
```

Après la cellule `🔒 LOCK PARAMETERS` :

```text
FINAL_WINDOW_S / FINAL_THRESHOLD
= paramètres utilisés par le held-out et le jeu
```

Ainsi, modifier `window_s` après le verrouillage ne modifie pas rétroactivement le jeu.
Pour tester un autre réglage, revenez au tuning, changez le paramètre, puis ré-exécutez
la cellule de verrouillage.

Le jeu affiche désormais en permanence `window`, `threshold` et `channels` réellement utilisés.

Deux réglages peuvent également franchir le même nombre d'obstacles tout en ayant des
comportements différents. Il faut alors regarder **aussi** :

- `detected_blocks` ;
- `false_jumps` ;
- `median_latency_s` ;
- `bci_score = detected_blocks - false_jumps`.

Le mini-jeu est une visualisation de la boucle ; les métriques restent l'évaluation scientifique.
