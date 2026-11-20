import sqlite3
from datetime import date, timedelta

#  RÈGLES DE LA BIBLIOTHÈQUE 
DUREE_JOURS = 14          # durée d'un prêt, en jours
MAX_EMPRUNTS = 3          # nombre maximum de livres empruntés en même temps
PENALITE_PAR_JOUR = 100   # pénalité par jour de retard, en FCFA
CATEGORIES = ["Ro", "Doc"]   # Ro = roman, Doc = document

# Livres ajoutés au premier lancement : (titre, auteur, catégorie, nombre d'exemplaires)
LIVRES_DE_BASE = [
    ("Le Petit Prince", "Saint-Exupéry", "Ro", 6),
    ("Python pour débutants", "J. Martin", "Doc", 4),
    ("Bases de données", "C. Date", "Doc", 2),
    ("Les Soleils des indépendances", "Ahmadou Kourouma", "Ro", 3),
    ("En attendant le vote des bêtes sauvages", "Ahmadou Kourouma", "Ro", 3),
    ("Allah n'est pas obligé", "Ahmadou Kourouma", "Ro", 3),
    ("Monnè, outrages et défis", "Ahmadou Kourouma", "Ro", 3),
    ("Le Pagne noir", "Bernard Binlin Dadié", "Ro", 3),
    ("Climbié", "Bernard Binlin Dadié", "Ro", 3),
    ("Un Nègre à Paris", "Bernard Binlin Dadié", "Ro", 3),
    ("Le Royaume aveugle", "Véronique Tadjo", "Ro", 3),
    ("Reine Pokou", "Véronique Tadjo", "Ro", 3),
    ("Matins de couvre-feu", "Tanella Boni", "Ro", 3),
    ("La Carte d'identité", "Jean-Marie Adiaffi", "Ro", 3),
    ("Aya de Yopougon", "Marguerite Abouet", "Ro", 3),
]

# Connexion à la base de données 
base = sqlite3.connect("bibliotheque_iit.db")
base.row_factory = sqlite3.Row



# outils pour optimiser notre application

def lire_nombre(message):
    """Demande un nombre, et redemande tant que ce n'est pas un nombre."""
    while True:
        try:
            return int(input(message))
        except ValueError:
            print("  -> Tapez un nombre, par exemple 1.")

def format_date(texte_iso):
    """Transforme 2026-12-04 en 04/12/2026."""
    return date.fromisoformat(texte_iso).strftime("%d/%m/%Y")



#  BASE DE DONNÉES : 3 tableaux (livres, lecteurs, emprunts)
def creer_base():
    base.executescript("""
    CREATE TABLE IF NOT EXISTS livres(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        auteur TEXT NOT NULL,
        categorie TEXT NOT NULL,
        total INTEGER NOT NULL,
        disponibles INTEGER NOT NULL);

    CREATE TABLE IF NOT EXISTS lecteurs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_carte TEXT,
        nom TEXT NOT NULL,
        telephone TEXT,
        date_inscription TEXT NOT NULL);

    CREATE TABLE IF NOT EXISTS emprunts(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        livre_id INTEGER NOT NULL,
        lecteur_id INTEGER NOT NULL,
        date_emprunt TEXT NOT NULL,
        date_prevue TEXT NOT NULL,
        date_retour TEXT,
        penalite INTEGER DEFAULT 0);
    """)
    # Ajoute chaque livre de départ seulement s'il n'existe pas déjà
    for titre, auteur, categorie, exemplaires in LIVRES_DE_BASE:
        existe = base.execute("SELECT 1 FROM livres WHERE titre = ?", (titre,)).fetchone()
        if not existe:
            base.execute(
                "INSERT INTO livres(titre, auteur, categorie, total, disponibles) VALUES(?,?,?,?,?)",
                (titre, auteur, categorie, exemplaires, exemplaires))
    base.commit()



#  LES LIVRES

def afficher_livre(livre):
    """Une ligne par livre. Le stock s'écrit disponibles/total, par exemple 1/6."""
    epuise = "  (ÉPUISÉ)" if livre["disponibles"] == 0 else ""
    print(f"[{livre['id']}] {livre['titre']} - {livre['auteur']} "
          f"({livre['categorie']}) : {livre['disponibles']}/{livre['total']}{epuise}")

def voir_livres():
    print("\n--- LES LIVRES (Ro = roman, Doc = document) ---")
    print("Le stock s'écrit disponibles/total, par exemple 1/6.")
    for livre in base.execute("SELECT * FROM livres ORDER BY titre"):
        afficher_livre(livre)

def rechercher_livre():
    mot = input("Tapez un mot du titre ou de l'auteur : ").strip()
    modele = f"%{mot}%"
    resultats = base.execute(
        "SELECT * FROM livres WHERE titre LIKE ? OR auteur LIKE ? ORDER BY titre",
        (modele, modele)).fetchall()
    if not resultats:
        print(f"  -> Aucun livre trouvé pour « {mot} ».")
    for livre in resultats:
        afficher_livre(livre)

def ajouter_livre():
    print("\n--- AJOUTER UN LIVRE ---")
    titre = input("Titre : ").strip()
    auteur = input("Auteur : ").strip()
    print("Type de livre :")
    print("  1. Ro  (roman)")
    print("  2. Doc (document)")
    choix = lire_nombre("Numéro du type : ")
    exemplaires = lire_nombre("Nombre d'exemplaires : ")
    if not titre or not auteur or not 1 <= choix <= len(CATEGORIES) or exemplaires < 1:
        print("  -> Informations incorrectes, le livre n'a pas été ajouté.")
        return
    base.execute(
        "INSERT INTO livres(titre, auteur, categorie, total, disponibles) VALUES(?,?,?,?,?)",
        (titre, auteur, CATEGORIES[choix - 1], exemplaires, exemplaires))
    base.commit()
    print(f"  -> « {titre} » ajouté ({exemplaires}/{exemplaires}).")


#  LES LECTEURS
def voir_lecteurs():
    print("\n--- LES LECTEURS ---")
    if base.execute("SELECT COUNT(*) FROM lecteurs").fetchone()[0] == 0:
        print("Aucun lecteur inscrit. Utilisez l'option 4 pour en inscrire un.")
    for lecteur in base.execute("SELECT * FROM lecteurs ORDER BY id"):
        en_cours = base.execute(
            "SELECT date_prevue FROM emprunts WHERE lecteur_id = ? AND date_retour IS NULL",
            (lecteur["id"],)).fetchall()
        en_retard = any(date.fromisoformat(e["date_prevue"]) < date.today() for e in en_cours)
        alerte = "  (A UN LIVRE EN RETARD)" if en_retard else ""
        print(f"[{lecteur['id']}] {lecteur['numero_carte']} - {lecteur['nom']} "
              f"- {len(en_cours)}/{MAX_EMPRUNTS} livres empruntés{alerte}")

def inscrire_lecteur():
    print("\n--- INSCRIRE UN LECTEUR ---")
    nom = input("Nom complet : ").strip()
    telephone = input("Numéro de téléphone : ").strip()
    if not nom:
        print("  -> Le nom est obligatoire.")
        return
    curseur = base.execute(
        "INSERT INTO lecteurs(nom, telephone, date_inscription) VALUES(?,?,?)",
        (nom, telephone, date.today().isoformat()))
    carte = f"LEC-{curseur.lastrowid:04d}"       # ex : LEC-0002
    base.execute("UPDATE lecteurs SET numero_carte = ? WHERE id = ?", (carte, curseur.lastrowid))
    base.commit()
    print(f"  -> {nom} est inscrit. Numéro de carte : {carte}")


#  EMPRUNTER ET RENDRE
def emprunter():
    if base.execute("SELECT COUNT(*) FROM lecteurs").fetchone()[0] == 0:
        print("  -> Aucun lecteur inscrit. Inscrivez d'abord un lecteur (option 4).")
        return
    voir_lecteurs()
    lecteur_id = lire_nombre("\nNuméro (ID) du lecteur : ")
    voir_livres()
    livre_id = lire_nombre("\nNuméro (ID) du livre : ")

    lecteur = base.execute("SELECT * FROM lecteurs WHERE id = ?", (lecteur_id,)).fetchone()
    livre = base.execute("SELECT * FROM livres WHERE id = ?", (livre_id,)).fetchone()
    if not lecteur or not livre:
        print("  -> Lecteur ou livre introuvable.")
        return

    # Les livres que ce lecteur a déjà et n'a pas encore rendus
    en_cours = base.execute(
        "SELECT * FROM emprunts WHERE lecteur_id = ? AND date_retour IS NULL",
        (lecteur_id,)).fetchall()

    # Règle 1 : le lecteur ne doit pas avoir de livre en retard
    if any(date.fromisoformat(e["date_prevue"]) < date.today() for e in en_cours):
        print("  -> REFUSÉ : ce lecteur a un livre en retard. Il doit le rendre d'abord.")
    # Règle 2 : limite de livres par lecteur
    elif len(en_cours) >= MAX_EMPRUNTS:
        print(f"  -> REFUSÉ : {MAX_EMPRUNTS} livres maximum en même temps.")
    # Règle 3 : pas deux fois le même livre
    elif any(e["livre_id"] == livre_id for e in en_cours):
        print("  -> REFUSÉ : ce lecteur a déjà ce livre.")
    # Règle 4 : il faut un exemplaire disponible
    elif livre["disponibles"] < 1:
        print("  -> REFUSÉ : plus aucun exemplaire disponible (stock 0).")
    else:
        date_prevue = date.today() + timedelta(days=DUREE_JOURS)
        base.execute(
            "INSERT INTO emprunts(livre_id, lecteur_id, date_emprunt, date_prevue) VALUES(?,?,?,?)",
            (livre_id, lecteur_id, date.today().isoformat(), date_prevue.isoformat()))
        base.execute("UPDATE livres SET disponibles = disponibles - 1 WHERE id = ?", (livre_id,))
        base.commit()
        print(f"  -> OK : « {livre['titre']} » emprunté par {lecteur['nom']}.")
        print(f"     À rendre avant le {date_prevue.strftime('%d/%m/%Y')} ({DUREE_JOURS} jours).")
        print(f"     Il reste {livre['disponibles'] - 1}/{livre['total']} exemplaires.")

def emprunts_en_cours():
    print(f"\n--- EMPRUNTS EN COURS (aujourd'hui : {date.today().strftime('%d/%m/%Y')}) ---")
    lignes = base.execute("""
        SELECT emprunts.*, livres.titre, lecteurs.nom
        FROM emprunts
        JOIN livres ON livres.id = emprunts.livre_id
        JOIN lecteurs ON lecteurs.id = emprunts.lecteur_id
        WHERE emprunts.date_retour IS NULL
        ORDER BY emprunts.date_prevue""").fetchall()
    if not lignes:
        print("Aucun emprunt en cours.")
    for e in lignes:
        jours_restants = (date.fromisoformat(e["date_prevue"]) - date.today()).days
        if jours_restants >= 0:
            delai = f"{jours_restants} jour(s) restant(s)"
        else:
            retard = -jours_restants
            delai = f"EN RETARD de {retard} jour(s) - pénalité actuelle : {retard * PENALITE_PAR_JOUR} FCFA"
        print(f"[{e['id']}] {e['titre']} | {e['nom']} | à rendre le {format_date(e['date_prevue'])} | {delai}")
    return lignes

def rendre_livre():
    if not emprunts_en_cours():
        return
    emprunt_id = lire_nombre("\nNuméro (ID) de l'emprunt à rendre : ")
    emprunt = base.execute(
        "SELECT * FROM emprunts WHERE id = ? AND date_retour IS NULL", (emprunt_id,)).fetchone()
    if not emprunt:
        print("  -> Emprunt introuvable.")
        return

    # Calcul du retard et de la pénalité
    jours_de_retard = max(0, (date.today() - date.fromisoformat(emprunt["date_prevue"])).days)
    penalite = jours_de_retard * PENALITE_PAR_JOUR

    base.execute("UPDATE emprunts SET date_retour = ?, penalite = ? WHERE id = ?",
                 (date.today().isoformat(), penalite, emprunt_id))
    base.execute("UPDATE livres SET disponibles = disponibles + 1 WHERE id = ?", (emprunt["livre_id"],))
    base.commit()

    livre = base.execute("SELECT * FROM livres WHERE id = ?", (emprunt["livre_id"],)).fetchone()
    if penalite > 0:
        print(f"  -> Livre rendu avec {jours_de_retard} jour(s) de retard.")
        print(f"     PÉNALITÉ À PAYER : {penalite} FCFA.")
    else:
        print("  -> Livre rendu à temps. Aucune pénalité.")
    print(f"     Stock de « {livre['titre']} » : {livre['disponibles']}/{livre['total']}")

#  MENU PRINCIPAL

def menu():
    creer_base()
    actions = {
        "1": voir_livres,
        "2": rechercher_livre,
        "3": ajouter_livre,
        "4": inscrire_lecteur,
        "5": voir_lecteurs,
        "6": emprunter,
        "7": rendre_livre,
        "8": emprunts_en_cours,
    }
    while True:
        print("\n===== BIBLIOTHÈQUE IIT =====")
        print(f"Règles : prêt de {DUREE_JOURS} jours | {MAX_EMPRUNTS} livres maximum | "
              f"pénalité {PENALITE_PAR_JOUR} FCFA par jour de retard")
        print("1. Voir les livres et le stock")
        print("2. Rechercher un livre")
        print("3. Ajouter un livre")
        print("4. Inscrire un lecteur")
        print("5. Voir les lecteurs")
        print("6. Emprunter un livre")
        print("7. Rendre un livre")
        print("8. Voir les emprunts en cours")
        print("0. Quitter")
        choix = input("Votre choix : ").strip()
        if choix == "0":
            print("Au revoir !")
            break
        elif choix in actions:
            actions[choix]()
        else:
            print("Choix invalide : tapez un numéro du menu.")

menu()
