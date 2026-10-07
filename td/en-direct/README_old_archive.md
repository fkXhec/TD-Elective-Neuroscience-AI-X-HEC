# TD en direct — Commander un bras robotique avec un EPOC X

## Objectif

Construire progressivement une interface cerveau-machine capable de commander un **petit bras robotique** avec un **Emotiv EPOC X**, puis comprendre ce qui change lorsque l'on passe d'une démonstration prête à l'emploi à un décodage explicite, d'un signal évoqué par l'environnement à une activité mentale endogène, et enfin d'un participant à un autre.

Le TD est organisé en **quatre couches**, précédées d'un test purement robotique :

```text
0. Robot seul              clavier → bras
1. Boucle BCI rapide       Cortex Mental Commands → bras
2. BCI transparente        attention visuelle SSVEP → CCA → bras
3. BCI endogène            imagerie motrice → CSP/LDA → bras
4. Généralisation          même système → nouveau participant → adaptation minimale
```

Les couches sont cumulatives : on conserve le même bras, la même interface de commande et autant que possible les mêmes outils. On ajoute une difficulté scientifique à la fois.

Le vocabulaire de commande du robot reste indépendant du décodeur :

```text
LEFT     tourner/déplacer le bras d'un pas vers la gauche
RIGHT    tourner/déplacer le bras d'un pas vers la droite
ACTION   saisir si la pince est vide ; déposer si elle tient un objet
NONE     ne rien faire
STOP     arrêt manuel prioritaire
```

Le modèle exact du bras n'est pas figé dans ce document. Il doit pouvoir être commandé depuis l'ordinateur et disposer d'un arrêt manuel fiable.

---

## Couche 0 — Valider le robot sans BCI

Avant d'utiliser le casque, vérifier indépendamment la partie robotique.

Le programme devra pouvoir envoyer manuellement les mêmes commandes que celles qui seront ensuite produites par les différentes couches :

```text
clavier → LEFT / RIGHT / ACTION / HOME / STOP → bras
```

Cette étape permet de distinguer une panne de communication avec le robot d'une erreur de décodage EEG.

Pour les premiers essais : utiliser un objet léger, limiter l'amplitude et la vitesse des mouvements, dégager la zone de travail et conserver un arrêt manuel accessible.

---

## Couche 1 — Vérifier rapidement qu'une boucle BCI complète fonctionne

### Principe

La première couche utilise les **Mental Commands** de l'écosystème Emotiv.

```text
participant
   ↓
EPOC X
   ↓
Cortex / Mental Commands
   ↓
LEFT / RIGHT / ACTION / NONE
   ↓
contrôleur du bras
   ↓
bras robotique
```

Cette couche sert à tester rapidement :

- la mise en place du casque et la qualité de contact ;
- l'entraînement et l'utilisation des Mental Commands ;
- l'ergonomie des commandes ;
- la logique `NONE` et l'arrêt de sécurité ;
- la liaison entre une décision BCI et une action physique ;
- la latence et les faux déclenchements de la chaîne complète.

Le décodage interne est fourni par Emotiv. Cette couche permet donc de montrer qu'une boucle BCI fonctionne, mais pas d'expliquer précisément comment les mesures EEG sont transformées en décision.

Documentation : [EmotivBCI](https://emotiv.gitbook.io/emotivbci) · [Cortex API](https://emotiv.gitbook.io/cortex-api).

---

## Couche 2 — Une BCI transparente : regarder la commande que l'on veut envoyer

### Le fond du SSVEP

La deuxième couche utilise un **SSVEP** (*Steady-State Visual Evoked Potential*).

L'écran présente simultanément plusieurs cibles visuelles. Chaque cible change de luminosité ou d'apparence selon un rythme différent.

Par exemple, sans fixer encore les fréquences réelles :

```text
┌──────────┐      ┌──────────┐      ┌──────────┐
│  LEFT    │      │  ACTION  │      │  RIGHT   │
│ rythme f1│      │ rythme f2│      │ rythme f3│
└──────────┘      └──────────┘      └──────────┘
```

Pour envoyer `LEFT`, le participant **regarde la cible LEFT pendant qu'elle clignote**. Pour envoyer `ACTION`, il regarde `ACTION`. Il n'a pas à mémoriser puis réimaginer la cible.

La stimulation visuelle périodique provoque une réponse mesurable dans l'EEG, particulièrement vers l'arrière de la tête. Le programme cherche alors laquelle des fréquences connues des cibles correspond le mieux à la fenêtre EEG récente.

```text
regarder ACTION
      ↓
stimulation visuelle à f2
      ↓
réponse EEG postérieure
      ↓
CCA : f1 ? f2 ? f3 ?
      ↓
f2 gagne avec assez de confiance
      ↓
ACTION
      ↓
bras robotique
```

Il s'agit donc d'une **sélection par attention visuelle utilisant une réponse cérébrale évoquée**. Ce n'est pas la lecture d'une pensée libre.

### Pourquoi cette couche est simple et utile

L'EPOC X comporte notamment **O1 et O2**, ainsi que P7/P8, ce qui rend son montage cohérent avec une première expérience visuelle. La méthode de base connaît déjà les fréquences qu'elle doit rechercher : elle n'a pas besoin d'apprendre de zéro la forme d'une « pensée LEFT » propre au participant.

Cette propriété fera aussi du SSVEP notre meilleur candidat pour tester ensuite la généralisation à une autre personne.

### Concevoir les cibles visuelles

Les fréquences ne sont **pas fixées à l'avance** dans ce dépôt. Elles doivent être compatibles avec le taux de rafraîchissement réel de l'écran.

**PsychoPy** sera utilisé pour contrôler les changements image par image et vérifier les images perdues. [Timing des stimuli — PsychoPy](https://psychopy.org/coder/codeStimuli.html).

Le protocole doit prévoir le confort visuel et les contre-indications pertinentes aux stimulations clignotantes. Si le protocole SSVEP n'est pas approprié pour un participant, il ne doit pas être utilisé avec cette personne.

### Vérifier l'acquisition EEG

Avant toute classification :

1. connecter l'EPOC X et vérifier la qualité des contacts ;
2. afficher les canaux et confirmer leur ordre, leurs unités et la fréquence d'échantillonnage effective ;
3. enregistrer un court signal accompagné des événements de stimulation ;
4. confirmer que les canaux postérieurs, notamment O1 et O2, sont exploitables ;
5. conserver la sortie dans un dossier local `data/`, ignoré par Git.

L'accès aux données EEG brutes dépend des droits Emotiv disponibles et doit être confirmé avec le compte utilisé.

### Transporter et synchroniser les flux

La chaîne privilégiée est :

```text
EPOC X → sortie EEG Emotiv → LSL → MNE-LSL → traitement Python
```

**LSL** transporte des flux horodatés. **MNE-LSL** permet de recevoir un flux dans l'écosystème MNE et de rejouer un enregistrement comme s'il arrivait progressivement.

Les marqueurs indiquant la cible présentée et son début doivent être enregistrés sur la même chronologie que l'EEG. [LSL](https://labstreaminglayer.readthedocs.io/info/intro.html) · [MNE-LSL](https://mne.tools/mne-lsl/stable/index.html).

### Baseline canonique : CCA

La première méthode à tester est la **CCA** (*Canonical Correlation Analysis*).

Pour chaque fréquence candidate, le programme construit des signaux de référence sinusoïdaux à la fréquence fondamentale et à plusieurs harmoniques. Il compare ensuite ces références avec les canaux EEG sélectionnés sur une fenêtre temporelle.

```text
O1 / O2 / éventuellement P7 / P8
            ↓
      fenêtre EEG récente
            ↓
 CCA avec les fréquences connues
      des différentes cibles
            ↓
 LEFT / RIGHT / ACTION / NONE
```

Le score le plus élevé indique la cible la plus compatible avec le signal observé. Une règle de confiance doit permettre de répondre `NONE` si aucune cible n'est suffisamment convaincante.

La CCA est utilisée d'abord parce qu'elle est simple à expliquer et peut fonctionner sans apprentissage individuel complexe. Une version **FBCCA** (*Filter-Bank CCA*) pourra ensuite être comparée si la baseline est insuffisante.

### Rejeu avant le direct

Avant de laisser le décodeur commander le bras :

1. enregistrer plusieurs séquences avec des cibles connues ;
2. vérifier hors ligne que le signal contient une information exploitable ;
3. rejouer l'enregistrement progressivement avec la même logique que le direct ;
4. vérifier qu'aucune étape n'utilise des données futures ;
5. mesurer le temps de calcul ;
6. seulement ensuite connecter la décision au robot.

---

## Couche 3 — Une commande endogène : imaginer plutôt que regarder

### Ce que l'on veut changer

Le SSVEP est robuste parce que le système connaît un signal extérieur périodique à rechercher. La couche 3 retire cette aide.

Le participant produit volontairement une activité mentale **sans cible visuelle clignotante qui porte la fréquence de la commande**. La première famille retenue pour cette exploration est l'**imagerie motrice** : imaginer un mouvement sans l'exécuter.

Pendant la calibration, une consigne visuelle ou sonore peut toujours indiquer quel mouvement imaginer et quand commencer. Cette consigne sert à connaître l'étiquette de l'essai ; le signal discriminant recherché n'est plus une réponse entraînée par une fréquence extérieure comme dans le SSVEP.

### Pourquoi commencer par l'imagerie motrice

L'imagerie motrice est l'un des paradigmes historiques et les plus étudiés des BCI endogènes. Elle modifie notamment les rythmes sensorimoteurs dans les bandes µ et β.

La première baseline sera volontairement classique :

```text
EEG
 ↓
filtrage approximatif 8–30 Hz
 ↓
fenêtres correspondant aux essais d'imagerie
 ↓
CSP — Common Spatial Patterns
 ↓
LDA — Linear Discriminant Analysis
 ↓
classe mentale détectée
```

[MNE fournit un exemple canonique CSP + LDA sur de l'imagerie motrice](https://mne.tools/stable/auto_examples/decoding/decoding_csp_eeg.html).

### Une difficulté importante avec l'EPOC X

L'EPOC X ne possède pas C3, Cz et C4, positions centrales très courantes pour étudier les rythmes sensorimoteurs. Il dispose notamment de FC5/FC6 et de sites plus frontaux, temporaux, pariétaux et occipitaux.

La couche 3 est donc **une expérience plus ambitieuse que la couche 2**, pas une réussite garantie.

On commencera par une discrimination **binaire** simple — par exemple deux types d'imagerie motrice — avant de chercher à produire trois commandes actives. Si deux classes ne sont pas fiables avec ce montage et ce participant, ajouter une troisième classe n'aurait pas de sens.

### Comment relier une expérience binaire au robot

Le but de la couche 3 est d'abord de démontrer une commande endogène fiable, pas de reproduire immédiatement toute l'ergonomie de la couche 2.

Deux étapes sont possibles :

1. **preuve de principe** : distinguer deux états mentaux en direct et déclencher deux actions du robot ;
2. **extension** : ajouter une troisième classe si les données le permettent, ou utiliser une petite machine à états pour transformer deux décisions fiables en plusieurs actions possibles.

Le critère important reste `NONE` : l'absence de volonté de commander ne doit pas être forcée dans l'une des classes actives.

---

## Couche 4 — Changer de participant : qu'est-ce qui se généralise vraiment ?

La dernière couche ne change pas le robot. Elle change **la personne qui porte le casque**.

L'expérience devient :

> Un système préparé avec le participant A fonctionne-t-il avec le participant B sans rien modifier ? Si non, quelle est la quantité minimale d'adaptation nécessaire ?

Cette couche doit être testée séparément pour le SSVEP et pour l'imagerie motrice, car on ne s'attend pas au même comportement.

### 4A. SSVEP : tester d'abord sans réentraînement

Avec la CCA de la couche 2, les références utilisées par le décodeur sont des sinusoïdes construites à partir des fréquences des cibles, pas un modèle appris uniquement sur le cerveau du participant A.

La première expérience doit donc être **zéro calibration spécifique** :

```text
mêmes cibles
mêmes fréquences
même CCA
mêmes canaux candidats
mêmes règles de décision
        ↓
nouveau participant B
```

On ne modifie d'abord que ce qui est physiquement nécessaire : positionnement du casque et qualité des contacts.

Si les performances sont insuffisantes, l'adaptation minimale consiste à mesurer quelques courts passages `LEFT`, `ACTION`, `RIGHT` et `NONE` pour régler des paramètres simples comme le seuil de confiance, la durée de fenêtre ou le sous-ensemble de canaux. On évite de reconstruire toute la méthode tant que ce n'est pas nécessaire.

### 4B. Imagerie motrice : mesurer explicitement le coût de calibration

Pour l'imagerie motrice, un transfert parfait entre personnes n'est **pas** l'hypothèse de départ. Les caractéristiques EEG et les filtres spatiaux varient fortement entre individus.

Le protocole doit donc mesurer successivement :

1. **zéro-shot** : appliquer au participant B le pipeline appris sur A, sans le modifier ;
2. **quelques essais de B** : ajouter une petite calibration étiquetée et réajuster le même pipeline CSP + LDA ;
3. si nécessaire seulement, tester une méthode d'alignement entre participants avant le même décodeur.

Une option simple d'approfondissement est l'**alignement euclidien** (*Euclidean Alignment*) : il cherche à rapprocher les distributions EEG de différents participants avant d'appliquer les mêmes étapes de traitement. Il peut être calculé sans connaître les étiquettes des essais du nouveau participant. [Référence : He & Wu, 2020](https://pubmed.ncbi.nlm.nih.gov/31034407/).

### Ce que l'on mesure dans cette couche

Pour chaque participant et chaque méthode, conserver :

- performance sans calibration ;
- performance après une courte calibration ;
- nombre d'essais ou minutes de calibration ajoutés ;
- faux déclenchements pendant `NONE` ;
- latence ;
- réussite de la tâche robotique complète.

La question finale devient alors quantitative :

> **Combien de données propres au nouveau participant faut-il ajouter pour retrouver une commande utilisable ?**

---

## Une interface robotique commune à toutes les couches

Les différentes voies doivent aboutir à **la même interface de commande du robot**.

```text
clavier ────────────────────────┐
Cortex Mental Commands ─────────┤
SSVEP / CCA ────────────────────┼──→ LEFT / RIGHT / ACTION / NONE → contrôleur bras → robot
imagerie motrice / CSP + LDA ───┘
```

Le code spécifique au robot ne doit pas connaître la manière dont la commande a été produite.

Une commande maintenue pendant plusieurs fenêtres ne doit pas provoquer une série involontaire d'actions. Une stratégie possible est d'imposer une confirmation sur plusieurs décisions successives, puis une courte période de verrouillage après chaque mouvement.

---

## Ce qu'il faut enregistrer

Pour chaque essai, conserver au minimum :

| Information | Pourquoi |
|---|---|
| début et fin de la consigne ou stimulation | savoir ce qui était demandé |
| cible / classe attendue | établir la vérité de référence du protocole |
| décision produite | évaluer le décodeur |
| score ou niveau de confiance disponible | comprendre les erreurs et régler `NONE` |
| commande envoyée au bras | distinguer décision et action logicielle |
| action réellement exécutée | détecter les erreurs robotiques |
| participant et niveau de calibration | étudier la généralisation |
| horodatages | mesurer la latence |

## Critères de réussite

Le système n'est pas évalué uniquement sur le fait que le robot « bouge ».

Mesurer au minimum :

- le taux de commandes attendues correctement reconnues ;
- les confusions entre commandes ;
- les **faux déclenchements** pendant les périodes `NONE` ;
- la latence entre le repère choisi et le mouvement physique ;
- la réussite de la tâche complète, par exemple saisir puis déposer un objet ;
- en couche 4, la performance en fonction du **temps de calibration ajouté**.

Si le système exploite principalement un clignement, une contraction musculaire ou un mouvement de tête, le résultat doit être décrit comme tel et non comme un décodage EEG de la réponse recherchée.

---

## Pistes gardées pour comparaison

- **P300 :** sélection basée sur la réponse à des événements cibles ; demande une gestion précise des événements et souvent plusieurs répétitions.
- **FBCCA :** extension de CCA exploitant plusieurs bandes de fréquences pour le SSVEP.
- **Alignement inter-participants :** à tester seulement après les baselines simples de la couche 4.
- **Timeflux :** framework public d'orchestration temps réel. Il pourra être réévalué si le programme Python devient suffisamment complexe pour justifier des graphes de nœuds. Il n'est pas une dépendance initiale.

## Logiciels retenus pour la première implémentation

| Rôle | Outil |
|---|---|
| Casque et accès Emotiv | EPOC X + outils Emotiv nécessaires |
| Couche 1 | Cortex / Mental Commands |
| Transport temporel des couches 2–4 | LSL |
| Réception / rejeu EEG | MNE-LSL |
| Analyse EEG | MNE-Python + NumPy/SciPy |
| Stimuli SSVEP | PsychoPy |
| Couche 2 | CCA, puis éventuellement FBCCA |
| Couche 3 | CSP + LDA avec MNE / scikit-learn |
| Couche 4 | mêmes pipelines ; calibration courte puis alignement seulement si nécessaire |
| Benchmark hors ligne si nécessaire | MOABB |
| Robot | interface à préciser après choix du modèle |

## Quand ajouter le code au dépôt

Le dépôt reste documentaire tant que le modèle de bras et l'accès réel au casque n'ont pas été vérifiés. Après choix du robot, l'implémentation pourra rester minimale :

```text
td/en-direct/
├── README.md
├── requirements.txt
└── code/
    ├── robot.py            # seule couche dépendante du modèle de bras
    ├── keyboard.py         # couche 0
    ├── cortex.py           # couche 1
    ├── stimulus.py         # stimuli SSVEP de la couche 2
    ├── ssvep.py            # CCA / FBCCA
    ├── motor_imagery.py    # CSP + LDA de la couche 3
    └── generalization.py   # expériences de la couche 4
```

Ces fichiers ne doivent être ajoutés qu'une fois leur contenu réellement testé avec le matériel.
