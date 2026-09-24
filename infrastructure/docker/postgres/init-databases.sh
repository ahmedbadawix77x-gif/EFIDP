#!/bin/sh
set -e

# ==============================================================================
# EFIDP - PostgreSQL Multi-Database Initialization Script
# Executed automatically by the official postgres entrypoint on initial startup.
# ==============================================================================

echo ">>> [EFIDP-POSTGRES] Initializing databases and users..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Ensure UTF-8 collation and standard schema
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

    -- Create Airflow metastore user and database
    CREATE USER airflow WITH PASSWORD 'airflow_dev_password';
    CREATE DATABASE airflow_db OWNER airflow ENCODING 'UTF8';
    GRANT ALL PRIVILEGES ON DATABASE airflow_db TO airflow;

    -- Create Read-Only and Application roles for EFIDP
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'efidp_readonly') THEN
            CREATE ROLE efidp_readonly;
        END IF;
    END
    \$\$;

    -- Grant basic usage to default schema
    GRANT ALL ON SCHEMA public TO $POSTGRES_USER;
    GRANT USAGE ON SCHEMA public TO efidp_readonly;
EOSQL

echo ">>> [EFIDP-POSTGRES] Initialization completed successfully."
