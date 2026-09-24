#!/bin/sh
set -e

# ==============================================================================
# EFIDP - MinIO S3 Bucket Initialization Script
# Executed by the minio/mc client container during stack startup.
# ==============================================================================

echo ">>> [EFIDP-MINIO-INIT] Waiting for MinIO server at ${MINIO_ENDPOINT_URL:-http://efidp-minio:9000}..."

until /usr/bin/mc alias set myminio "${MINIO_ENDPOINT_URL:-http://efidp-minio:9000}" "${MINIO_ROOT_USER:-minioadmin}" "${MINIO_ROOT_PASSWORD:-minioadmin_secret_dev}"; do
    echo ">>> MinIO not ready yet, retrying in 2 seconds..."
    sleep 2
done

echo ">>> [EFIDP-MINIO-INIT] Connected to MinIO. Provisioning required Lakehouse buckets..."

for BUCKET in efidp-bronze efidp-silver efidp-gold efidp-quarantine; do
    if /usr/bin/mc ls myminio/"$BUCKET" > /dev/null 2>&1; then
        echo ">>> Bucket '$BUCKET' already exists."
    else
        echo ">>> Creating bucket '$BUCKET'..."
        /usr/bin/mc mb myminio/"$BUCKET"
    fi
done

echo ">>> [EFIDP-MINIO-INIT] Lakehouse buckets successfully verified:"
/usr/bin/mc ls myminio
