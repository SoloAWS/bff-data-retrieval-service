#!/bin/bash
# Configure environment variables
export PROJECT_ID="sologcp"
export APP_NAME="bff-retrieval-app"
export PORT=8080
export REGION="us-central1"
export IMAGE_TAG="gcr.io/$PROJECT_ID/$APP_NAME"

# Read environment variables from .env file
if [ -f .env ]; then
  source .env
else
  echo "Error: .env file not found"
  exit 1
fi

# Set default project
gcloud config set project $PROJECT_ID

# Enable necessary services
gcloud services enable cloudbuild.googleapis.com \
    containerregistry.googleapis.com \
    run.googleapis.com

# Build Docker image and push to Google Container Registry
gcloud builds submit --tag $IMAGE_TAG

# Deploy application to Google Cloud Run with environment variables
gcloud run deploy $APP_NAME \
    --image $IMAGE_TAG \
    --platform managed \
    --region $REGION \
    --port $PORT \
    --set-env-vars="AUTH_SERVICE_URL=${AUTH_SERVICE_URL},DATA_RETRIEVAL_SERVICE_URL=${DATA_RETRIEVAL_SERVICE_URL},AUTH_TOKEN=${AUTH_TOKEN},PULSAR_SERVICE_URL=${PULSAR_SERVICE_URL},PULSAR_TOKEN=${PULSAR_TOKEN}" \
    --allow-unauthenticated

echo "Deployment complete!"