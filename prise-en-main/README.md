# Prise en main — Voir ce que mesure réellement un EEG

Cette activité est facultative et indépendante des deux TD. Elle dure une quinzaine de minutes et ne nécessite **ni casque, ni installation, ni programmation**.

## Ce que vous devez comprendre à la fin

Après cette prise en main, vous devez pouvoir répondre à quatre questions simples :

1. **À quoi ressemble une mesure EEG ?**
2. **Que représentent un canal, un microvolt et une fréquence d’échantillonnage ?**
3. **Pourquoi deux électrodes ou deux conditions peuvent-elles donner des signaux différents ?**
4. **Pourquoi une différence visible sur une courbe ne suffit-elle pas encore à construire une interface cerveau-machine ?**

---

## 1. Un EEG est d’abord une série de nombres

L’**électroencéphalographie**, ou **EEG**, mesure de petites différences de tension électrique à la surface de la tête.

Une **électrode** est un contact conducteur posé sur le cuir chevelu.

Un **canal EEG** est la suite des valeurs mesurées au cours du temps pour une position donnée.

La figure suivante montre deux canaux réels, **F3** et **O1**, enregistrés simultanément pendant cinq secondes chez un participant au repos.

![Deux canaux EEG réels entre 10 et 15 secondes, avec un zoom sur les valeurs successives.](../images/lire-un-eeg.png)

F3 est situé plutôt vers l’avant gauche de la tête ; O1 vers l’arrière gauche.

### Comment lire la figure

- **Axe horizontal : le temps**, en secondes.
- **Axe vertical : la tension**, en **microvolts (µV)**.
- Les deux courbes correspondent au **même participant et au même moment**, mais à deux positions différentes.
- Chaque courbe n’est pas continue à l’origine : elle est constituée d’une succession de mesures.

Ici, le système enregistre **160 valeurs par seconde et par canal**. On dit que la **fréquence d’échantillonnage est de 160 Hz**.

Deux mesures consécutives sont donc séparées de :

**1 / 160 s = 6,25 ms.**

À 10 secondes, par exemple, les valeurs visibles dans cet enregistrement sont environ :

- F3 : **−174 µV**
- O1 : **112 µV**

Le point important n’est pas de mémoriser ces nombres.

**À retenir : une courbe EEG est simplement la représentation graphique d’une longue série de mesures électriques prises au cours du temps.**

---

## 2. Pourquoi les deux courbes ne sont-elles pas identiques ?

Comparez F3 et O1 sur les mêmes cinq secondes.

Elles ne présentent pas exactement les mêmes variations alors qu’elles sont enregistrées au même moment.

C’est normal : une électrode ne mesure pas « une pensée » ni l’activité exclusive d’une petite région située juste en dessous d’elle. Chaque canal reçoit un mélange de contributions électriques, et ce mélange varie selon la position de mesure.

### À observer

Sans chercher à interpréter chaque pic, repérez simplement :

- des variations lentes et rapides ;
- des moments où les deux canaux évoluent différemment ;
- des variations parfois importantes sur quelques dizaines ou centaines de millisecondes.

Un grand pic ne signifie pas nécessairement qu’un événement cérébral important vient de se produire.

Les yeux, les muscles, un mouvement du participant ou un mauvais contact avec une électrode peuvent aussi modifier fortement le signal. Ce sont des exemples d’**artefacts**.

**À retenir : voir une variation dans l’EEG ne suffit pas à savoir ce qui l’a provoquée.**

[Approfondissement : exemples d’artefacts EEG avec MNE](https://mne.tools/stable/auto_tutorials/preprocessing/10_preprocessing_overview.html)

---

## 3. Une condition expérimentale peut-elle modifier ce que l’on mesure ?

Nous allons maintenant comparer deux enregistrements du **même participant au repos** :

- [Yeux ouverts — S001R01](https://physionet.org/lightwave/?db=eegmmidb/1.0.0&record=S001/S001R01.edf)
- [Yeux fermés — S001R02](https://physionet.org/lightwave/?db=eegmmidb/1.0.0&record=S001/S001R02.edf)

Les données sont hébergées par **PhysioNet** et affichées avec le visualiseur **LightWAVE**.

Dans les noms des fichiers :

- `S001` = participant 1 ;
- `R01` et `R02` = deux enregistrements différents ;
- `.edf` = format de fichier utilisé pour enregistrer des signaux physiologiques.

[Description du jeu de données](https://physionet.org/content/eegmmidb/1.0.0/)

### Ce qu’il faut faire

Ouvrez les deux fichiers dans deux onglets.

Choisissez **le même canal** dans les deux enregistrements et observez plusieurs passages de quelques secondes.

Essayez de répondre à cette seule question :

> **Le signal semble-t-il présenter des différences reproductibles entre les conditions yeux ouverts et yeux fermés ?**

Vous pouvez par exemple regarder si certaines oscillations paraissent plus régulières ou plus marquées dans une condition.

Il est tout à fait possible que la différence ne soit **pas évidente à l’œil nu**.

C’est justement un résultat intéressant.

---

## 4. Observer n’est pas encore mesurer

Supposons que vous ayez l’impression que le signal est plus régulier lorsque les yeux sont fermés.

Cette impression ne suffit pas pour conclure.

Il faudrait définir une quantité mesurable, par exemple :

- l’amplitude des variations dans une certaine gamme de fréquences ;
- leur puissance moyenne ;
- leur répétition au cours de plusieurs passages.

Puis vérifier si cette quantité distingue réellement les deux conditions.

On passe alors de :

**« les courbes ont l’air différentes »**

à :

**« je calcule une caractéristique permettant de quantifier cette différence »**.

C’est une étape essentielle pour la suite.

---

## 5. Du signal EEG à une interface cerveau-machine

Une **interface cerveau-machine**, ou **BCI** (*Brain–Computer Interface*), ajoute encore une étape.

Elle ne se contente pas d’afficher les courbes.

Elle cherche à transformer certaines propriétés du signal en une **décision**.

Par exemple :

**mesures EEG → caractéristique → décision → commande d’un objet**

Dans le TD en direct, l’objectif sera d’aller jusqu’à une action physique réalisée par un bras robotique.

La difficulté centrale sera donc exactement celle rencontrée ici :

> **Comment passer d’un signal qui varie en permanence à une différence suffisamment fiable pour prendre une décision ?**

---

## Ce qu’il faut retenir

À ce stade, vous n’avez pas besoin de savoir analyser un EEG.

Vous devez seulement avoir compris que :

- un EEG est une série de mesures électriques au cours du temps ;
- plusieurs électrodes donnent plusieurs canaux ;
- les signaux peuvent différer selon la position, le moment et la condition expérimentale ;
- toutes les variations ne sont pas d’origine cérébrale ;
- observer une différence est une première étape, mais une BCI doit ensuite la **quantifier et la reconnaître suffisamment fiablement pour produire une commande**.

La suite du cours consistera précisément à franchir ces étapes.
