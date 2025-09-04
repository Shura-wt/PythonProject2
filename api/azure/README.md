# Introduction

Ce Readme vise à expliquer le déploiement du docker sur l'environnement Azure Container Apps.

# Installation et mise à jour des pré-requis

Installer Azure CLI :

``` winget install --exact --id Microsoft.AzureCLI ```

Il est ensuite nécessaire de se connecter à un compte ayant le bon niveau de permission :

``` az login ```

En cas de problème sur les permissions contacter Aurélien.

Mettre à jour Azure CLI et l'extension Container Apps :

```
az upgrade
az extension add --name containerapp --upgrade --allow-preview true
```

# Configuration

Enregistrer Microsoft.App et Microsoft.OperationalInsights :
```
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

Définir les variables d'environnement :
```
$RESOURCE_GROUP="baes-api"
$LOCATION="francecentral"
$ENVIRONMENT="env-baes-api"
$API_NAME="baes-api"
```

Créer le groupe de ressources pour l'App :
``` az group create --name $RESOURCE_GROUP --location $LOCATION ```

Créer le container :
```
az containerapp up `
    --name $API_NAME `
    --resource-group $RESOURCE_GROUP `
    --location $LOCATION `
    --environment $ENVIRONMENT `
    --source .
```
