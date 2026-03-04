# Ordonnancement des Taches - Comparaison GA vs SA vs ACO vs TABU vs HH

Projet de comparaison de **5 algorithmes metaheuristiques** pour le **Job-Shop Scheduling Problem** (ordonnancement des taches) sur un jeu de **1000 taches** et **10 machines**.

---

## Les 5 Algorithmes

| Algorithme | Fichier | Comment ca marche (explication simple) |
|------------|---------|---------------------------------------|
| **GA** (Algorithme Genetique) | `ga.py` | Imite l'evolution naturelle : on cree une "population" de solutions, on garde les meilleures, on les croise entre elles et on mute pour trouver de meilleures solutions a chaque generation. |
| **SA** (Recuit Simule) | `sa.py` | Imite le refroidissement d'un metal : au debut on accepte meme des solutions moins bonnes (pour explorer), puis au fur et a mesure que la "temperature" baisse, on n'accepte plus que les ameliorations. |
| **ACO** (Colonie de Fourmis) | `aco.py` | Imite les fourmis qui cherchent de la nourriture : chaque fourmi construit une solution, les bonnes solutions laissent plus de "pheromones" pour guider les fourmis suivantes. |
| **TABU** (Recherche Tabou) | `tabu.py` | Explore les voisins de la solution actuelle (en echangeant des taches), mais interdit de revenir aux solutions recemment visitees (liste tabou) pour eviter de tourner en rond. |
| **HH** (Hyper-Heuristique) | `hh.py` | Un algorithme qui choisit automatiquement la meilleure strategie parmi plusieurs (swap, reverse, shift). Il apprend au fil du temps quelle heuristique marche le mieux et l'utilise plus souvent. |

---

## Structure du projet

```
NEWPROJECT/
  utils.py          # Fonctions partagees (chargement donnees, decodage, Gantt)
  ga.py             # Algorithme Genetique
  sa.py             # Recuit Simule
  aco.py            # Colonie de Fourmis
  tabu.py           # Recherche Tabou
  hh.py             # Hyper-Heuristique
  run_all.py        # Lance les 5 algorithmes et sauvegarde les resultats
  dashboard.py      # Dashboard Streamlit pour visualiser et comparer
  machines.json     # Donnees des 10 machines
  tasks1000.json    # Donnees des 1000 taches
  requirements.txt  # Dependances Python
  results/          # Dossier de sortie (genere automatiquement)
```

---

## Installation

```bash
cd NEWPROJECT
pip install -r requirements.txt
```

## Utilisation

### Etape 1 : Lancer les 5 algorithmes

```bash
cd NEWPROJECT
python run_all.py
```

Cela va :
- Charger `tasks1000.json` (1000 taches) et `machines.json` (10 machines)
- Executer GA, SA, ACO, TABU, et HH sur les 1000 taches
- Sauvegarder les resultats JSON + diagrammes de Gantt dans `results/`

### Etape 2 : Ouvrir le Dashboard

```bash
cd NEWPROJECT
streamlit run dashboard.py
```

Le dashboard s'ouvrira automatiquement dans votre navigateur.

---

## Ce que vous verrez dans le Dashboard (explication pour la presentation)

### 1. Tableau Recapitulatif
Un tableau qui resume les resultats de chaque algorithme :
- **Makespan** = le temps total pour finir TOUTES les taches (en minutes et en heures).
  Plus c'est bas, meilleur c'est.
- **Temps d'execution** = combien de temps l'algorithme a mis pour calculer sa solution.
- Le meilleur algorithme est affiche en vert.

### 2. Graphiques en Barres (Bar Charts)
Deux graphiques cote a cote :
- **A gauche - Makespan** : la hauteur de la barre = qualite de la solution.
  La barre la plus courte = le meilleur algorithme.
- **A droite - Temps d'execution** : la hauteur = temps de calcul.
  La barre la plus courte = l'algorithme le plus rapide.

### 3. Performance Relative
- **Barres horizontales** : montre le makespan de chaque algorithme en heures,
  ce qui permet de comparer visuellement les ecarts.
- **Pourcentages d'amelioration** : montre combien chaque algorithme
  fait mieux que le pire resultat. Exemple : "+33%" veut dire 33% meilleur
  que le pire algorithme.

### 4. Courbes de Convergence
Ce graphique montre **comment chaque algorithme ameliore sa solution au fil du temps** :
- L'axe X = le numero de l'iteration (ou generation pour le GA)
- L'axe Y = le meilleur makespan trouve jusqu'a ce point
- Une courbe qui descend vite = l'algorithme converge rapidement
- Une courbe plate = l'algorithme stagne (n'arrive plus a ameliorer)
- SA descend progressivement, GA descend par paliers, TABU descend regulierement,
  HH descend vite au debut, ACO descend peu.

### 5. Diagrammes de Gantt
Pour **chaque algorithme**, un planning visuel montrant :
- Chaque ligne = une machine
- Chaque rectangle colore = une operation d'une tache sur cette machine
- La largeur du rectangle = la duree de l'operation
- On peut voir comment les machines sont utilisees et les temps morts entre operations.

### 6. Parametres Utilises
Les reglages de chaque algorithme (taille population, nombre d'iterations,
taux de mutation, temperature, etc.)

---

## Configuration de chaque algorithme

### GA - Algorithme Genetique (`ga.py`)

| Parametre | Valeur | Explication |
|-----------|--------|-------------|
| `pop_size` | 30 | Nombre d'individus (solutions) dans la population |
| `generations` | 100 | Nombre maximum de generations (iterations) |
| `cx_rate` | 0.9 (90%) | Taux de crossover : probabilite de croiser 2 parents pour creer un enfant |
| `mut_rate` | 0.2 (20%) | Taux de mutation : probabilite de modifier une solution (swap 2 taches) |
| `early_stop` | 20 | Arret si pas d'amelioration pendant 20 generations |
| `seed` | 42 | Graine aleatoire pour reproductibilite |

- **Selection** : Tournoi de taille 3 (on prend 3 individus au hasard, on garde le meilleur)
- **Crossover** : PPX (Precedence Preserving Crossover) - croise 2 parents en respectant l'ordre
- **Mutation** : Swap de 2 taches + reparation si precedence violee
- **Elitisme** : On garde les 10% meilleurs de chaque generation

### SA - Recuit Simule (`sa.py`)

| Parametre | Valeur | Explication |
|-----------|--------|-------------|
| `iters` | 2000 | Nombre total d'iterations |
| `t0` | 200.0 | Temperature initiale (haute = explore beaucoup au debut) |
| `alpha` | 0.995 | Facteur de refroidissement (T = T * 0.995 a chaque iteration) |
| `seed` | 42 | Graine aleatoire pour reproductibilite |

- **Voisinage** : Swap de 2 taches aleatoires + reparation precedence
- **Acceptation** : Si le voisin est meilleur, on l'accepte toujours. Sinon, on l'accepte avec probabilite exp(-delta/T). Quand T est haute, on accepte souvent les degradations. Quand T est basse, on n'accepte presque plus.

### ACO - Colonie de Fourmis (`aco.py`)

| Parametre | Valeur | Explication |
|-----------|--------|-------------|
| `n_ants` | 30 | Nombre de fourmis (chacune construit une solution complete) |
| `iterations` | 100 | Nombre de cycles de fourmis |
| `evap_rate` | 0.3 (30%) | Taux d'evaporation des pheromones (oubli progressif) |
| `alpha` | 1.0 | Importance des pheromones dans le choix |
| `beta` | 2.0 | Importance de l'heuristique (duree courte = prioritaire) |
| `seed` | 42 | Graine aleatoire pour reproductibilite |

- **Construction** : Chaque fourmi choisit la prochaine tache en fonction des pheromones et de l'heuristique (taches courtes preferees)
- **Mise a jour** : Les pheromones sont evaporees puis renforcees sur le meilleur chemin trouve

### TABU - Recherche Tabou (`tabu.py`)

| Parametre | Valeur | Explication |
|-----------|--------|-------------|
| `max_iters` | 500 | Nombre total d'iterations |
| `tabu_tenure` | 15 | Taille de la liste tabou (les 15 derniers mouvements sont interdits) |
| `n_neighbors` | 20 | Nombre de voisins generes a chaque iteration |
| `seed` | 42 | Graine aleatoire pour reproductibilite |

- **Voisinage** : 20 swaps aleatoires sont testes a chaque iteration
- **Liste tabou** : Les 15 derniers swaps (i,j) effectues sont interdits pour eviter de boucler
- **Aspiration** : Si un mouvement tabou donne un resultat meilleur que le record global, il est quand meme accepte

### HH - Hyper-Heuristique (`hh.py`)

| Parametre | Valeur | Explication |
|-----------|--------|-------------|
| `iterations` | 500 | Nombre total d'iterations |
| `seed` | 42 | Graine aleatoire pour reproductibilite |

- **3 heuristiques bas-niveau** :
  - **swap** : echange 2 taches aleatoires
  - **reverse** : inverse un petit segment de l'ordre (2 a 8 taches)
  - **shift** : retire une tache et la reinserere ailleurs
- **Selection adaptative** : chaque heuristique a un score. Si elle ameliore la solution, son score augmente et elle est choisie plus souvent. Sinon, son score diminue.
- **Resultat** : l'algorithme apprend automatiquement que "shift" et "swap" marchent mieux que "reverse" pour ce probleme.

---

## Complexite Algorithmique

Variables utilisees :
- **n** = nombre de taches (1000 dans notre cas)
- **m** = nombre moyen d'operations par tache (~5)
- **P** = taille de la population (GA)
- **K** = nombre de fourmis (ACO)
- **V** = nombre de voisins par iteration (TABU)
- **I** = nombre d'iterations

### Complexite temporelle (par iteration)

| Algorithme | Complexite par iteration | Complexite totale | Explication |
|------------|-------------------------|-------------------|-------------|
| **GA** | O(P * n * m) | O(I * P * n * m) | A chaque generation : P individus a evaluer, chacun necessite un decodage en O(n*m) plus crossover O(n) et reparation O(n) |
| **SA** | O(n * m) | O(I * n * m) | A chaque iteration : 1 swap O(1), 1 reparation O(n), 1 decodage O(n*m). Le plus simple. |
| **ACO** | O(K * n^2) | O(I * K * n^2) | Chaque fourmi construit une solution en n etapes. A chaque etape, elle calcule les probabilites sur les taches disponibles. Plus le decodage O(n*m). |
| **TABU** | O(V * n * m) | O(I * V * n * m) | A chaque iteration : V voisins generes, chacun necessite reparation O(n) + decodage O(n*m). |
| **HH** | O(n * m) | O(I * n * m) | A chaque iteration : 1 heuristique appliquee O(n), 1 reparation O(n), 1 decodage O(n*m). Similaire a SA. |

### Complexite spatiale (memoire)

| Algorithme | Memoire | Explication |
|------------|---------|-------------|
| **GA** | O(P * n) | Stocke P solutions de taille n (la population entiere) |
| **SA** | O(n) | Stocke seulement 2 solutions : la courante et la meilleure |
| **ACO** | O(n + K * n) | Pheromones O(n) + K solutions construites par iteration |
| **TABU** | O(n + T) | Solution courante O(n) + liste tabou de taille T |
| **HH** | O(n) | Stocke seulement 2 solutions : la courante et la meilleure |

### Avec nos parametres (n=1000, m=5)

| Algorithme | Operations par iteration | Total operations | Memoire |
|------------|------------------------|-----------------|---------|
| **GA** | 30 * 1000 * 5 = 150,000 | 100 * 150,000 = **15 M** | 30 * 1000 = 30K entiers |
| **SA** | 1000 * 5 = 5,000 | 2000 * 5,000 = **10 M** | 2 * 1000 = 2K entiers |
| **ACO** | 30 * 1000^2 = 30,000,000 | 100 * 30,000,000 = **3 G** | 30 * 1000 = 30K entiers |
| **TABU** | 20 * 1000 * 5 = 100,000 | 500 * 100,000 = **50 M** | 1000 + 15 = ~1K entiers |
| **HH** | 1000 * 5 = 5,000 | 500 * 5,000 = **2.5 M** | 2 * 1000 = 2K entiers |

**Observations** :
- **HH et SA** ont la complexite la plus basse (O(I * n * m)), ce qui explique qu'ils sont les plus rapides
- **ACO** a la complexite la plus haute (O(I * K * n^2)) a cause de la construction de solution par chaque fourmi, ce qui explique qu'il est le plus lent (212s)
- **TABU** a une complexite moderee mais explore plus de voisins, ce qui lui permet de trouver de meilleures solutions
- **GA** a une complexite moderee aussi, mais le crossover et la gestion de population ajoutent du surcoput

---

## Comparaison Finale : Quel est le meilleur algorithme ?

Apres execution sur 1000 taches, voici les resultats :

| Rang | Algorithme | Makespan | Heures | Runtime | Forces | Faiblesses |
|------|-----------|----------|--------|---------|--------|------------|
| 1 | **TABU** | 32,238 min | 537h | 81.4s | Meilleur makespan, exploration locale efficace, evite les cycles | Plus lent (20 voisins par iteration) |
| 2 | **SA** | 37,212 min | 620h | 16.0s | Tres bon makespan, rapide, bon equilibre exploration/exploitation | Resultat depend du refroidissement |
| 3 | **HH** | 42,373 min | 706h | 4.0s | Le plus rapide, apprend quelle strategie marche le mieux | N'explore pas assez en profondeur |
| 4 | **GA** | 43,869 min | 731h | 23.5s | Bonne diversite, amelioration continue par generations | Besoin de plus de generations pour converger |
| 5 | **ACO** | 47,978 min | 800h | 212.8s | Inspire de la nature, resultat ameliore avec 30 fourmis | Le plus lent, convergence limitee sur grands problemes |

**Conclusion** : La Recherche Tabou (TABU) donne le meilleur makespan (32,238 min)
car elle explore methodiquement 20 voisins a chaque iteration et sa liste tabou
l'empeche de tourner en rond. Le Recuit Simule (SA) arrive en 2eme position
avec un bon compromis qualite/rapidite. L'Hyper-Heuristique (HH) est tres rapide
(4 secondes) et arrive 3eme en apprenant quelle strategie utiliser. Le GA converge
regulierement mais lentement. L'ACO avec 30 fourmis est le plus lent et donne
le moins bon resultat sur 1000 taches.

---

## Fichiers de resultats

Apres execution, le dossier `results/` contient :

| Fichier | Contenu |
|---------|---------|
| `ga_results.json` | Resultats detailles du GA |
| `sa_results.json` | Resultats detailles du SA |
| `aco_results.json` | Resultats detailles de l'ACO |
| `tabu_results.json` | Resultats detailles du TABU |
| `hh_results.json` | Resultats detailles de l'HH |
| `comparison.json` | Resume comparatif des 5 algorithmes |
| `ga_gantt.png` | Diagramme de Gantt du GA |
| `sa_gantt.png` | Diagramme de Gantt du SA |
| `aco_gantt.png` | Diagramme de Gantt de l'ACO |
| `tabu_gantt.png` | Diagramme de Gantt du TABU |
| `hh_gantt.png` | Diagramme de Gantt de l'HH |

## Donnees d'entree

- **machines.json** : 10 machines (Hydraulic Press, CNC Lathe, etc.)
- **tasks1000.json** : 1000 taches, chaque tache a plusieurs operations sur differentes machines, avec des contraintes de precedence (certaines taches doivent finir avant que d'autres commencent)
