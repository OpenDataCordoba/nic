#!/bin/bash
# Backup script for NIC app
# Stops the app, creates a DB dump, and restarts the app

set -e

# Stop the nic app via supervisor
sudo supervisorctl stop nic


# Default backup directory
BACKUP_DIR="$HOME/nic_backups"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --backup-dir)
            BACKUP_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

DB_NAME="nicdb"
DB_USER="nicuser"
DATE=$(date +"%Y-%m-%d")
DUMP_FILE="$BACKUP_DIR/nicdb_$DATE.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Dump the database
pg_dump --format=p --no-acl --no-owner \
    "$DB_NAME" -h localhost \
    -U "$DB_USER" > "$DUMP_FILE"

# Restart the nic app
sudo supervisorctl start nic

echo "Backup completed: $DUMP_FILE"