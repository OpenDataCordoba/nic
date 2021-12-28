# Dump DB
pg_dump \
    --format=p \
    --no-acl \
    --no-owner \
    nicdb \
    --exclude-table=spatial_ref_sys \
    -h localhost \
    -U nicuser > nicdb.sql

# Avoid extensions
sed -E 's/(DROP|CREATE|COMMENT ON) EXTENSION/-- \1 EXTENSION/g' nicdb.sql > nicdb2.sql

# Create new DB in the new server
sudo su - postgres
psql
CREATE USER nicuser WITH PASSWORD 'XXXXX';
ALTER ROLE nicuser SUPERUSER;
CREATE EXTENSION postgis;
CREATE DATABASE nicdb OWNER nicuser;

# import raw data
psql -d nicdb -U nicuser -f nicdb2.sql
