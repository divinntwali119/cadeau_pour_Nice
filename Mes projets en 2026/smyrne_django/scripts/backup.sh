#!/bin/bash
# =============================================================
# SCRIPT DE SAUVEGARDE — Église Smyrne (5e CELPA)
# =============================================================
# Sauvegarde la base de données (SQLite ou PostgreSQL)
# et l'ensemble des fichiers médias (images, vidéos, audios).
#
# Utilisation :
#   bash scripts/backup.sh
#
# Automatisation (cron quotidien à 2h du matin) :
#   0 2 * * * cd "/chemin/vers/smyrne_django" && bash scripts/backup.sh >> backups/backup.log 2>&1
# =============================================================

set -e

# Répertoire du projet
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BASE_DIR}/backups"
TIMESTAMP="$(date +"%Y%m%d_%H%M%S")"
CURRENT_BACKUP="${BACKUP_DIR}/smyrne_backup_${TIMESTAMP}"
RETENTION_DAYS=14

mkdir -p "${CURRENT_BACKUP}"

echo "=========================================="
echo "📦 Début de la sauvegarde Smyrne : $(date)"
echo "Destination : ${CURRENT_BACKUP}"
echo "=========================================="

# 1. Sauvegarde de la Base de Données
if [ -f "${BASE_DIR}/db.sqlite3" ]; then
    echo "▶ Sauvegarde SQLite..."
    if command -v sqlite3 >/dev/null 2>&1; then
        # Sauvegarde atomique sécurisée sans verrouillage gênant
        sqlite3 "${BASE_DIR}/db.sqlite3" ".backup '${CURRENT_BACKUP}/db.sqlite3'"
    else
        cp "${BASE_DIR}/db.sqlite3" "${CURRENT_BACKUP}/db.sqlite3"
    fi
    gzip -c "${CURRENT_BACKUP}/db.sqlite3" > "${CURRENT_BACKUP}/db.sqlite3.gz"
    rm -f "${CURRENT_BACKUP}/db.sqlite3"
    echo "✔ Base SQLite sauvegardée et compressée (db.sqlite3.gz)"
elif [ -n "${DATABASE_URL}" ] && [[ "${DATABASE_URL}" == postgres* ]]; then
    echo "▶ Sauvegarde PostgreSQL..."
    pg_dump "${DATABASE_URL}" | gzip > "${CURRENT_BACKUP}/postgres_dump.sql.gz"
    echo "✔ Base PostgreSQL sauvegardée (postgres_dump.sql.gz)"
fi

# 2. Sauvegarde des fichiers médias (uploads)
if [ -d "${BASE_DIR}/media" ]; then
    echo "▶ Sauvegarde des médias..."
    tar -czf "${CURRENT_BACKUP}/media_${TIMESTAMP}.tar.gz" -C "${BASE_DIR}" media
    echo "✔ Fichiers médias compressés (media_${TIMESTAMP}.tar.gz)"
fi

# 3. Métadonnées de la sauvegarde
cat <<EOF > "${CURRENT_BACKUP}/metadata.json"
{
  "project": "Eglise Smyrne 5e CELPA",
  "timestamp": "$(date -Iseconds)",
  "sqlite_backup": $([ -f "${CURRENT_BACKUP}/db.sqlite3.gz" ] && echo "true" || echo "false"),
  "media_backup": $([ -f "${CURRENT_BACKUP}/media_${TIMESTAMP}.tar.gz" ] && echo "true" || echo "false")
}
EOF

# 4. Nettoyage des anciennes sauvegardes (+ de RETENTION_DAYS jours)
echo "▶ Nettoyage des sauvegardes datant de plus de ${RETENTION_DAYS} jours..."
find "${BACKUP_DIR}" -mindepth 1 -maxdepth 1 -type d -name "smyrne_backup_*" -mtime +${RETENTION_DAYS} -exec rm -rf {} + 2>/dev/null || true

echo "=========================================="
echo "✅ Sauvegarde terminée avec succès !"
echo "Emplacement : ${CURRENT_BACKUP}"
echo "Taille totale : $(du -sh "${CURRENT_BACKUP}" | cut -f1)"
echo "=========================================="
