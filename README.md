# Gestion de bibliothèque – IIT

**Type d'application :** application console. Elle s'utilise dans le terminal, sans fenêtre ni souris. Le programme affiche un menu, on tape un numéro puis la touche Entrée.

**Ce que fait l'application :** elle aide à gérer une petite bibliothèque. Elle garde la liste des livres avec leur stock, la liste des lecteurs, et les emprunts. Elle donne la date limite pour rendre chaque livre (14 jours), compte les jours restants, et calcule la pénalité si le livre est rendu en retard (100 FCFA par jour). Le stock s'écrit sous la forme disponibles/total : par exemple 1/6 veut dire qu'il reste 1 exemplaire sur 6. Les informations sont gardées dans une base de données, donc rien n'est perdu quand on ferme le programme.

**Outils utilisés :** le langage Python, et SQLite pour la base de données (le fichier `bibliotheque_iit.db`). SQLite est déjà inclus avec Python : il n'y a rien d'autre à installer.

**Comment lancer l'application :**
1. Mettez le fichier `bibliotheque_console.py` dans un dossier.
2. Ouvrez un terminal dans ce dossier.
3. Tapez : `py bibliotheque_console.py`
4. Au premier lancement, la base de données est créée toute seule avec une quinzaine de livres. Si vous aviez lancé une ancienne version, supprimez d'abord le fichier `bibliotheque_iit.db` pour repartir de zéro.

**Les éléments du menu :**
1. **Voir les livres et le stock** : affiche tous les livres avec leur stock. `Ro` veut dire roman et `Doc` veut dire documentaire.
2. **Rechercher un livre** : tapez un mot du titre ou du nom de l'auteur.
3. **Ajouter un livre** : donnez le titre, l'auteur, le type (Ro ou Doc) et le nombre d'exemplaires.
4. **Inscrire un lecteur** : donnez le nom et le téléphone. Le lecteur reçoit un numéro de carte, par exemple LEC-0001.
5. **Voir les lecteurs** : affiche les lecteurs et le nombre de livres qu'ils ont empruntés.
6. **Emprunter un livre** : choisissez le lecteur puis le livre. Le programme donne la date de retour et baisse le stock.
7. **Rendre un livre** : choisissez l'emprunt. Le stock remonte, et la pénalité est calculée s'il y a du retard.
8. **Voir les emprunts en cours** : affiche les jours restants, ou le retard et la pénalité à payer.
0. **Quitter** : ferme le programme.

**Les règles :**
- Un prêt dure 14 jours.
- Un lecteur peut avoir 3 livres au maximum en même temps.
- Un emprunt est refusé si le lecteur a un livre en retard, s'il a déjà ce livre, ou s'il ne reste plus d'exemplaire.
- Pour changer ces valeurs, modifiez les premières lignes du fichier `bibliotheque_console.py`.

**Pour essayer une pénalité sans attendre 14 jours :** remplacez temporairement `DUREE_JOURS = 14` par `DUREE_JOURS = -3`. Un livre emprunté sera tout de suite en retard de 3 jours. Remettez 14 ensuite.
