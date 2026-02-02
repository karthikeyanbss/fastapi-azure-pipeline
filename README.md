# FastAPI Azure Container Apps - Multi-Environment Pipeline

Professional-grade monorepo demonstrating CI/CD pipeline deployment to Azure Container Apps across Dev, QA, and Prod environments.

## 🏗️ Architecture

```
┌─────────────┐
│   GitHub    │
│  Repository │
└──────┬──────┘
       │
       │ Push to main
       ▼
┌─────────────────────────────┐
│   GitHub Actions Workflow   │
│  ┌───────────────────────┐  │
│  │  Build & Push Image   │  │
│  │  to ACR (once)        │  │
│  └───────────────────────┘  │
│            │                 │
│            ▼                 │
│  ┌─────────────────────┐    │
│  │  Deploy to 3 envs   │    │
│  │  (matrix strategy)  │    │
│  └─────────────────────┘    │
└─────────┬───────────────────┘
          │
    ┌─────┴─────┐
    │           │
    ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│  Dev   │ │   QA   │ │  Prod  │
│ Container│ Container│ Container│
│  App   │ │  App   │ │  App   │
└────────┘ └────────┘ └────────┘
```

## 📁 Project Structure

```
.
├── .github/
│   └── workflows/
│       └── deploy-pipeline.yml  # CI/CD pipeline
├── app/
│   └── main.py                  # FastAPI application
├── infra/
│   ├── dev.env                  # Dev environment config
│   ├── qa.env                   # QA environment config
│   └── prod.env                 # Prod environment config
├── Dockerfile                   # Container image definition
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## 🚀 Quick Start

### Prerequisites

- Azure subscription
- Azure CLI installed
- GitHub account

### 1. Azure Infrastructure Setup

```bash
# Set variables
RESOURCE_GROUP="ner-service-rg"
LOCATION="eastus"
ACR_NAME="nerfastapiacr"  # Must be globally unique
CONTAINERAPPS_ENV="ner-fastapi-env"

# Create Container Registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true

# Create Container Apps Environment
az containerapp env create \
  --name $CONTAINERAPPS_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION

# Create three container apps (Dev, QA, Prod)
for ENV in dev qa prod; do
  az containerapp create \
    --name fastapi-$ENV \
    --resource-group $RESOURCE_GROUP \
    --environment $CONTAINERAPPS_ENV \
    --image mcr.microsoft.com/azuredocs/containerapps-helloworld:latest \
    --target-port 8000 \
    --ingress external \
    --query properties.configuration.ingress.fqdn
done
```

### 2. GitHub Secrets Configuration

Create a Service Principal and add to GitHub Secrets:

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

az ad sp create-for-rbac \
  --name "github-actions-fastapi-pipeline" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --sdk-auth
```

Add the following secrets to your GitHub repository (`Settings > Secrets and variables > Actions`):

- `AZURE_CREDENTIALS`: The JSON output from the command above
- `ACR_NAME`: Your Azure Container Registry name (e.g., `nerfastapiacr`)

### 3. Deploy

Simply push to the `main` branch:

```bash
git add .
git commit -m "Initial commit"
git push origin main
```

## 🧪 Testing Endpoints

Once deployed, test your environments:

```bash
# Health check
curl https://fastapi-dev.<region>.azurecontainerapps.io/health

# Echo test
curl -X POST https://fastapi-qa.<region>.azurecontainerapps.io/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from QA!"}'

# App info
curl https://fastapi-prod.<region>.azurecontainerapps.io/info
```

## 📊 Features

- ✅ **Single Image Build**: Build once, deploy everywhere (immutable deployments)
- ✅ **Matrix Deployment**: Parallel deployment to Dev, QA, Prod
- ✅ **Environment Isolation**: Separate Azure resources per environment
- ✅ **Health Checks**: Automated health verification after deployment
- ✅ **Security**: Non-root container user, minimal base image
- ✅ **Monitoring**: Deployment summaries and health check results
- ✅ **FastAPI**: Modern, fast, production-ready Python framework

## 🔧 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
cd app
python main.py

# Access the API
open http://localhost:8000/docs
```

## 📝 License

MIT License - Feel free to use this template for your projects!