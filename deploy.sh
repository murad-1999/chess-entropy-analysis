#!/bin/bash
set -e

export GOOGLE_CLOUD_PROJECT="infra2026-494820"
gcloud config set project $GOOGLE_CLOUD_PROJECT
echo "Cleaning up Artifact Registry for project $GOOGLE_CLOUD_PROJECT..."
IMAGES=$(gcloud artifacts docker images list us-central1-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/cloud-run-source-deploy --format="value(package)") || true
for IMAGE in $IMAGES; do
  echo "Deleting image $IMAGE..."
  gcloud artifacts docker images delete "$IMAGE" --quiet --delete-tags || true
done

echo "Deploying Tier 1 (Compute): engine-service"
gcloud run deploy engine-service \
  --source services/engine-service \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --port 8080 \
  --format="value(status.url)" > engine_url.txt

ENGINE_URL=$(cat engine_url.txt)
echo "Engine Service deployed at: $ENGINE_URL"

echo "Deploying Tier 2 (Gateway): analysis-service"
gcloud run deploy analysis-service \
  --source services/analysis-service \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --port 8080 \
  --set-env-vars ENGINE_API_URL="$ENGINE_URL/analyze" \
  --format="value(status.url)" > gateway_url.txt

GATEWAY_URL=$(cat gateway_url.txt)
echo "Gateway Service deployed at: $GATEWAY_URL"

echo "Deploying Tier 3 (UI): chess-vision-ui"
gcloud run deploy chess-vision-ui \
  --source services/chess-vision-ui \
  --region us-central1 \
  --allow-unauthenticated \
  --min-instances 0 \
  --max-instances 1 \
  --port 8080 \
  --set-env-vars GATEWAY_URL="$GATEWAY_URL" \
  --format="value(status.url)" > ui_url.txt

UI_URL=$(cat ui_url.txt)
echo "UI Frontend deployed at: $UI_URL"
