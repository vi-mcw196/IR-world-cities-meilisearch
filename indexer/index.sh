#!/bin/sh

MAX_ATTEMPTS=10
ATTEMPT=1
SLEEP_INTERVAL=5

until curl -s "$MEILISEARCH_HOST/health" > /dev/null; do
  if [ "$ATTEMPT" -ge "$MAX_ATTEMPTS" ]; then
    echo "Error: Meilisearch not available after $MAX_ATTEMPTS attempts"
    exit 1
  fi
  echo "Waiting for Meilisearch (attempt $ATTEMPT/$MAX_ATTEMPTS)..."
  sleep $SLEEP_INTERVAL
  ATTEMPT=$((ATTEMPT + 1))
done

echo "Meilisearch is up and running!"

curl -X POST "$MEILISEARCH_HOST/indexes/cities/documents" \
  -H "Content-Type: application/json" \
  --data-binary @/app/dataset/"$DATASET_NAME".json || {
  echo "Error: Failed to populate index"
  exit 1
}

curl -X PATCH "$MEILISEARCH_HOST/indexes/cities/settings" \
  -H "Content-Type: application/json" \
  --data-binary @/app/dataset/settings.json || {
  echo "Error: Failed to apply settings"
  exit 1
}

echo "Indexing and settings applied successfully!"