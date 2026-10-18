# Audit de sécurité avant mise en ligne – Smyrne Django

## 1) Fichiers et éléments à sécuriser avant mise en ligne

### Fichiers sensibles à protéger
- [.env](.env) : contient les variables d’environnement sensibles (SECRET_KEY, DATABASE_URL, etc.)
- `db.sqlite3` : base locale, à ne pas exposer en production si non utilisé
- `media/` : fichiers uploadés (images, vidéos, documents)
- `staticfiles/` : fichiers statiques compilés, à ne pas exposer comme source de développement
- fichiers de logs, dumps, backups, fichiers temporaires

### Fichiers recommandés dans le .gitignore
- `.env`
- `.env.*`
- `db.sqlite3`
- `media/`
- `staticfiles/`
- `__pycache__/`
- `*.pyc`
- `*.log`

### Bonnes pratiques de sécurité
- ne jamais committer le fichier `.env`
- ne jamais partager le mot de passe PostgreSQL ou la clé secrète
- utiliser des variables d’environnement côté serveur ou un secret manager
- activer HTTPS en production
- limiter les adresses autorisées via `ALLOWED_HOSTS`
- mettre DEBUG à `False` avant mise en ligne

---

## 2) Ce qui a été vérifié dans le projet

### Configuration Django
Le fichier principal de configuration est [smyrne/settings.py](smyrne/settings.py).

Points vérifiés :
- `DEBUG = True` actuellement
- `ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']`
- `TIME_ZONE = 'Africa/Kinshasa'`
- `LANGUAGE_CODE = 'fr-fr'`
- `STATIC_URL = '/static/'`
- `MEDIA_URL = '/media/'`
- `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`
- `LOGIN_URL = '/connexion/'`
- `LOGIN_REDIRECT_URL = '/'`
- `LOGOUT_REDIRECT_URL = '/'`

### Base de données
Le projet utilise PostgreSQL via `DATABASE_URL` dans [.env](.env).

Informations détectées :
- type : PostgreSQL
- host : localhost
- port : 5432
- base : eglise_db
- utilisateur : divin

> Les identifiants exacts ont été vérifiés localement, mais ils ne sont pas réécrits ici pour éviter toute fuite de credentials.

### Migrations détectées
Les migrations présentes dans le projet sont les suivantes :
- [apps/accounts/migrations/0001_initial.py](apps/accounts/migrations/0001_initial.py)
- [apps/articles/migrations/0001_initial.py](apps/articles/migrations/0001_initial.py)
- [apps/core/migrations/0001_initial.py](apps/core/migrations/0001_initial.py)
- [apps/cultes/migrations/0001_initial.py](apps/cultes/migrations/0001_initial.py)
- [apps/evenements/migrations/0001_initial.py](apps/evenements/migrations/0001_initial.py)
- [apps/galerie/migrations/0001_initial.py](apps/galerie/migrations/0001_initial.py)
- [apps/histoire/migrations/0001_initial.py](apps/histoire/migrations/0001_initial.py)
- [apps/ministeres/migrations/0001_initial.py](apps/ministeres/migrations/0001_initial.py)
- [apps/predications/migrations/0001_initial.py](apps/predications/migrations/0001_initial.py)
- [apps/priere/migrations/0001_initial.py](apps/priere/migrations/0001_initial.py)

### Sécurité Django activée
- `django-axes` installé et configuré
- `AXES_FAILURE_LIMIT = 5`
- `AXES_COOLOFF_TIME = 1`
- `AXES_RESET_ON_SUCCESS = True`
- `AUTHENTICATION_BACKENDS` configuré avec `Axes`

### Points à corriger avant mise en ligne
- mettre `DEBUG = False`
- sécuriser `.env`
- vérifier `ALLOWED_HOSTS` pour le vrai domaine de production
- utiliser HTTPS strict sur le serveur web
- activer la protection des cookies de session et CSRF en production
- ne pas garder les fichiers de développement, imports, backups ou dumps dans le dépôt

---

## 3) Recommandation finale

Avant la mise en ligne, je recommande :
1. passer `DEBUG` à `False`
2. compléter les variables d’environnement côté serveur
3. sécuriser `.env` et supprimer toute donnée sensible du dépôt
4. vérifier le domaine dans `ALLOWED_HOSTS`
5. mettre en place HTTPS et restriction des accès
6. sauvegarder les médias et les données de façon sécurisée

Ce document sert de checklist de sécurité pour la phase de mise en ligne.
