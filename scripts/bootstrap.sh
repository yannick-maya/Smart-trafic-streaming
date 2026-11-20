#!/usr/bin/env sh
set -eu

# Create the local topics only when absent; repeat runs are safe.
for topic in traffic.sensor.flow traffic.sensor.speed traffic.weather traffic.events traffic.dlq; do
  docker compose exec -T kafka /opt/kafka/bin/kafka-topics.sh \
    --bootstrap-server kafka:29092 \
    --create --if-not-exists \
    --topic "$topic" \
    --partitions "${KAFKA_TOPIC_PARTITIONS:-3}" \
    --replication-factor 1 \
    --config "retention.ms=${KAFKA_TOPIC_RETENTION_MS:-604800000}"
done

mc_service() {
  docker compose --profile bootstrap run --rm minio-bootstrap "$@"
}

mc_service alias set local http://minio:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc_service mb --ignore-existing "local/${MINIO_RAW_BUCKET:-traffic-raw}"
mc_service mb --ignore-existing "local/${MINIO_QUARANTINE_BUCKET:-traffic-quarantine}"

# Confirm that PostGIS is installed and responds in the configured database.
docker compose exec -T postgres psql \
  --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --command 'SELECT postgis_version();'
