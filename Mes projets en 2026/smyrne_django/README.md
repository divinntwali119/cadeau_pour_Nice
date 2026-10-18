# 5e CELPA SMYRNE — Site Web Dynamique Django & PostgreSQL

Bienvenue sur le projet officiel de la plateforme web de la **5e CELPA SMYRNE** (Bukavu, RDC).  
Ce projet transforme le site statique initial en une application web dynamique, robuste, sécurisée et évolutive propulsée par **Django 5** et **PostgreSQL**.

---

## 🏛️ Architecture du Projet

Le projet est structuré en **10 applications Django modulaires**, respectant les meilleures pratiques de développement :

| Application | Rôle & Fonctionnalités |
|---|---|
| **`apps.core`** | Page d'accueil, carrousels dynamiques, témoignages, statistiques, paramètres généraux du site (nom, contacts, réseaux sociaux, logo). |
| **`apps.cultes`** | Cultes dominicaux et de semaine, horaires, programmes hebdomadaires, gestion du direct (live streaming). |
| **`apps.predications`** | Enseignements et prédications (vidéo YouTube/MP4, audio MP3), pagination, lecteur multimédia. |
| **`apps.articles`** | Blog d'actualités paroissiales, catégorisation, compteur de vues, likes en temps réel (AJAX), espace commentaires avec modération. |
| **`apps.evenements`** | Agenda paroissial, événements à venir et passés, formulaires d'inscriptions en ligne avec confirmation. |
| **`apps.galerie`** | Galerie multimédia haute résolution, filtrage par catégories, affichage en lightbox modal. |
| **`apps.priere`** | Soumission de requêtes de prière (avec option confidentielle pour les pasteurs) et recueil des témoignages de foi. |
| **`apps.histoire`** | Récit historique de la paroisse et anciennes chorales marquantes. |
| **`apps.ministeres`** | Présentation des ministères, départements d'activités, chorales et équipes de louange. |
| **`apps.accounts`** | Système d'authentification unifié (membres et administrateurs) avec protection anti-brute force intégrée (**django-axes**). |

---

## 🚀 Démarrage Rapide

### 1. Prérequis
- Python 3.11+ (ou 3.12 / 3.14)
- PostgreSQL 14+
- `virtualenv`

### 2. Cloner ou naviguer dans le dossier
```bash
cd smyrne_django
```

### 3. Activer l'environnement virtuel
```bash
source .venv/bin/activate
```

### 4. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 5. Configuration de la base de données (`.env`)
Le fichier `.env` est déjà prêt à l'emploi :
```env
SECRET_KEY=django-insecure-smyrne-changez-cette-cle-en-production-2026!
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://divin:smyrne2026@localhost:5432/eglise_db
MEDIA_URL=/media/
STATIC_URL=/static/
```

### 6. Appliquer les migrations
```bash
python manage.py migrate
```

### 7. Lancer le serveur de développement
```bash
python manage.py runserver
```
Rendez-vous sur [http://127.0.0.1:8000/](http://127.0.0.1:8000/) !

---

## 🔑 Accès Administrateur

Un compte superutilisateur par défaut est configuré :
- **URL Admin :** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **Identifiant :** `admin`
- **Mot de passe :** `admin2026`

Depuis cet espace, vous pouvez gérer l'intégralité du contenu :
- Publier des articles avec l'éditeur riche **CKEditor**
- Ajouter des prédications audio ou vidéo
- Valider les commentaires et les témoignages de prière
- Modifier les horaires de culte et les coordonnées de l'église

---

## 🔒 Sécurité et Performance

- **Protection Anti-Brute Force :** `django-axes` bloque automatiquement les tentatives d'intrusion après 5 échecs consécutifs.
- **Éditeur WYSIWYG :** `django-ckeditor` pour une rédaction fluide et enrichie des articles et biographies.
- **Fichiers Statiques :** `WhiteNoise` avec compression et mise en cache optimale.
- **Thème Sombre / Clair :** Persistance automatique du choix d'affichage via `localStorage`.

---

© 2026 5e CELPA SMYRNE — Bukavu, République Démocratique du Congo.
