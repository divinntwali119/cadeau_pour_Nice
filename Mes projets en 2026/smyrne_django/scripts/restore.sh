#!/bin/bash
# =============================================================
# SCRIPT DE RESTAURATION — Église Smyrne (5e CELPA)
# =============================================================
# Restaure la base de données et les médias depuis un dossier de backup.
#
# Utilisation :
#   bash scripts/restore.sh backups/smyrne_backup_YYYYMMDD_HHMMSS
# =============================================================

set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_PATH="$1"

if [ -z "${BACKUP_PATH}" ] || [ ! -d "${BACKUP_PATH}" ]; then
    echo "❌ Erreur : veuillez spécifier un dossier de sauvegarde valide."
    echo "Usage: bash scripts/restore.sh <chemin_dossier_backup>"
    exit 1
fi

echo "⚠️ ATTENTION : Cette opération va écraser les données actuelles par la sauvegarde !"
echo "Dossier source : ${BACKUP_PATH}"
read -p "Voulez-vous continuer ? (o/N) : " confirm
if [[ ! "$confirm" =~ ^[oOyY]$ ]]; then
    echo "Restauration annulée."
    exit 0
fi

# 1. Restauration SQLite
if [ -f "${BACKUP_PATH}/db.sqlite3.gz" ]; then
    echo "▶ Restauration de la base de données SQLite..."
    gunzip -c "${BACKUP_PATH}/db.sqlite3.gz" > "${BASE_DIR}/db.sqlite3"
    echo "✔ Base SQLite restaurée."
fi

# 2. Restauration Médias
MEDIA_ARCHIVE=$(find "${BACKUP_PATH}" -name "media_*.tar.gz" | head -n 1)
if [ -n "${MEDIA_ARCHIVE}" ] && [ -f "${MEDIA_ARCHIVE}" ]; then
    echo "▶ Restauration des fichiers médias..."
    tar -xzf "${MEDIA_ARCHIVE}" -C "${BASE_DIR}"
    echo "✔ Médias restaurés."
fi

echo "=========================================="
echo "✅ Restauration effectuée avec succès !"
echo "=========================================="
