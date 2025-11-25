#!/bin/bash
# Usage: ./run-sql.sh <sql_file> [--db-name DBNAME] [--db-user USER] [--db-host HOST] [--db-port PORT] [--db-pass PASSWORD]
# Runs the given SQL file and saves the output as CSV with the same base name.

set -e

# Default values
DB_NAME="nicdb"
DB_USER="nicuser"
DB_HOST="localhost"
DB_PORT="5432"
DB_PASS=""

# Parse arguments
SQL_FILE=""
while [[ $# -gt 0 ]]; do
	case $1 in
		--db-name)
			DB_NAME="$2"; shift 2;;
		--db-user)
			DB_USER="$2"; shift 2;;
		--db-host)
			DB_HOST="$2"; shift 2;;
		--db-port)
			DB_PORT="$2"; shift 2;;
		--db-pass)
			DB_PASS="$2"; shift 2;;
		*.sql)
			SQL_FILE="$1"; shift;;
		*)
			echo "Unknown option: $1" >&2; exit 1;;
	esac
done

if [[ -z "queries/$SQL_FILE" ]]; then
	echo "Usage: $0 <sql_file> [--db-name DBNAME] [--db-user USER] [--db-host HOST] [--db-port PORT] [--db-pass PASSWORD]" >&2
	exit 1
fi

CSV_FILE="data/${SQL_FILE%.sql}.csv"

# Export password if provided
if [[ -n "$DB_PASS" ]]; then
	export PGPASSWORD="$DB_PASS"
fi

# Run the SQL and save as CSV
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "queries/$SQL_FILE" --csv > "$CSV_FILE"

echo "CSV saved to $CSV_FILE"
