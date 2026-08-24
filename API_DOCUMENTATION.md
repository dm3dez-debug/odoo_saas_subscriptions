# Odoo SaaS Subscriptions - API Documentation

## Vue d'ensemble

Ce module offre une suite complète pour gérer les souscriptions SaaS des instances Odoo. Il comprend la gestion des plans, des instances, des souscriptions et du monitoring des ressources.

## Endpoints API

### Plans

#### GET /saas/plans
Récupère la liste de tous les plans disponibles.

**Réponse:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "name": "Plan Starter",
      "code": "STARTER",
      "monthly_price": 29.99,
      "max_storage_gb": 10,
      "max_users": 5,
      "features": ["API Access", "Priority Support"]
    }
  ]
}
```

#### GET /saas/plan/<plan_id>
Récupère les détails d'un plan spécifique.

### Instances

#### GET /saas/instances
Récupère les instances de l'utilisateur connecté.

#### GET /saas/instance/<instance_id>
Récupère les détails d'une instance spécifique.

#### GET /saas/instance/<instance_id>/resources
Récupère les ressources allouées pour une instance.

#### POST /saas/instance/<instance_id>/backup
Crée une sauvegarde de l'instance.

### Souscriptions

#### GET /saas/subscriptions
Récupère les souscriptions de l'utilisateur connecté.

#### GET /saas/subscription/<subscription_id>
Récupère les détails d'une souscription spécifique.

#### POST /saas/subscription/<subscription_id>/renew
Renouvelle une souscription.

### Santé

#### GET /saas/health
Vérifie que le service SaaS est opérationnel.

**Réponse:**
```json
{
  "status": "ok",
  "message": "Odoo SaaS Service is running"
}
```

## Modèles de Données

### saas.plan
Représente un plan ou une formule SaaS.

**Champs principaux:**
- `name`: Nom du plan
- `code`: Code unique
- `monthly_price`: Prix mensuel
- `yearly_price`: Prix annuel
- `max_storage_gb`: Stockage maximum
- `max_users`: Nombre maximum d'utilisateurs
- `features`: Liste des fonctionnalités

### saas.instance
Représente une instance Odoo déployée.

**Champs principaux:**
- `name`: Nom de l'instance
- `code`: Code unique d'instance
- `partner_id`: Client propriétaire
- `plan_id`: Plan associé
- `state`: État (draft, active, suspended, deleted)
- `instance_url`: URL d'accès
- `allocated_storage_gb`: Stockage alloué
- `used_storage_gb`: Stockage utilisé

### saas.subscription
Représente une souscription client.

**Champs principaux:**
- `name`: Référence
- `partner_id`: Client
- `plan_id`: Plan choisi
- `instance_id`: Instance associée
- `state`: État (draft, active, paused, expired, cancelled)
- `start_date`: Date de début
- `billing_period`: Période (monthly, quarterly, yearly)
- `amount`: Montant
- `auto_renewal`: Renouvellement automatique

### saas.resource
Représente une ressource d'instance.

**Types de ressources:**
- `storage`: Espace disque
- `users`: Nombre d'utilisateurs
- `modules`: Modules installés
- `databases`: Bases de données
- `api_calls`: Appels API
- `emails`: Emails
- `webhooks`: Webhooks
