#!/bin/sh
set -e

# ==============================================================================
# EFIDP - Kafka Topic Initialization Script
# Executed by an ephemeral Kafka CLI container to ensure core topics exist.
# ==============================================================================

BOOTSTRAP_SERVER="${KAFKA_BOOTSTRAP_SERVERS:-efidp-kafka:29092}"

echo ">>> [EFIDP-KAFKA-INIT] Waiting for Kafka broker at $BOOTSTRAP_SERVER..."

kafka-topics --bootstrap-server "$BOOTSTRAP_SERVER" --list > /dev/null 2>&1 || {
    echo ">>> Waiting for broker to accept connections..."
    sleep 5
}

echo ">>> [EFIDP-KAFKA-INIT] Broker available. Creating required topics..."

# 1. Primary Raw Transactions Topic (3 partitions for parallel consumer workers)
kafka-topics --bootstrap-server "$BOOTSTRAP_SERVER" \
    --create --if-not-exists \
    --topic efidp.transactions.raw \
    --partitions 3 \
    --replication-factor 1 \
    --config retention.ms=604800000 \
    --config cleanup.policy=delete

# 2. Dead-letter Queue for malformed / schema-violating events
kafka-topics --bootstrap-server "$BOOTSTRAP_SERVER" \
    --create --if-not-exists \
    --topic efidp.transactions.deadletter \
    --partitions 1 \
    --replication-factor 1 \
    --config retention.ms=2592000000 \
    --config cleanup.policy=delete

echo ">>> [EFIDP-KAFKA-INIT] Active Kafka topics:"
kafka-topics --bootstrap-server "$BOOTSTRAP_SERVER" --list
