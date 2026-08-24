# Odoo SaaS Subscriptions Module

Module Odoo 19 pour la gestion complète des souscriptions SaaS aux instances Odoo.

## Fonctionnalités

### Gestion des Instances
- ✅ Création d'instances Odoo
- ✅ Activation/Désactivation d'instances
- ✅ Suppression d'instances
- ✅ Allocation des espaces disques
- ✅ Suivi des ressources utilisées

### Gestion des Formules
- ✅ Création de plans/formules personnalisés
- ✅ Configuration des limites de ressources
- ✅ Gestion des prix et tarification
- ✅ Historique des modifications

### Gestion des Souscriptions
- ✅ Association client/instance/plan
- ✅ Suivi de l'état des souscriptions
- ✅ Dates d'activation et renouvellement
- ✅ Gestion des renouvellements automatiques

### Monitoring des Ressources
- ✅ Suivi de l'utilisation disque
- ✅ Suivi des utilisateurs actifs
- ✅ Limites de stockage par plan
- ✅ Alertes de dépassement

## Installation

```bash
git clone https://github.com/dm3dez-debug/odoo_saas_subscriptions.git
cd odoo_saas_subscriptions
```

1. Placer le module dans le répertoire `addons` d'Odoo
2. Redémarrer le serveur Odoo
3. Accéder à Applications > Odoo SaaS Subscriptions
4. Cliquer sur Installer

## Architecture

```
odoo_saas_subscriptions/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── saas_plan.py
│   ├── saas_instance.py
│   ├── saas_subscription.py
│   └── saas_resource.py
├── controllers/
│   ├── __init__.py
│   └── main.py
├── views/
│   ├── saas_plan_views.xml
│   ├── saas_instance_views.xml
│   ├── saas_subscription_views.xml
│   ├── saas_resources_views.xml
│   └── menu_views.xml
├── security/
│   └── ir.model.access.csv
├── data/
│   └── saas_plan_data.xml
└── reports/
    └── subscription_report.xml
```

## Utilisation

### Créer un Plan
1. Aller à SaaS > Configuration > Plans
2. Cliquer sur Créer
3. Remplir les détails (nom, prix, limites de ressources)
4. Sauvegarder

### Créer une Instance
1. Aller à SaaS > Instances
2. Cliquer sur Créer
3. Sélectionner le client et le plan
4. Les ressources sont allouées automatiquement
5. Activer l'instance

### Créer une Souscription
1. Aller à SaaS > Souscriptions
2. Cliquer sur Créer
3. Lier le client, l'instance et le plan
4. Définir les dates de début et renouvellement
5. Sauvegarder

## Modèles de Données

### SaaS Plan
- Nom du plan
- Description
- Prix mensuel/annuel
- Limite de stockage
- Limite d'utilisateurs
- Nombre de modules inclus
- Support prioritaire

### SaaS Instance
- Nom de l'instance
- Client assigné
- Plan sélectionné
- URL d'accès
- Statut (création, actif, suspendu, supprimé)
- Date de création
- Espace disque alloué/utilisé

### SaaS Subscription
- Client
- Instance
- Plan
- Date de début
- Date de renouvellement
- Statut (active, suspendue, expirée)
- Prix
- Remarques

### SaaS Resource
- Instance
- Type de ressource (disque, utilisateurs, modules)
- Limite
- Utilisation actuelle
- Pourcentage d'utilisation
- Date de dernière mise à jour

## Contributions

Les contributions sont bienvenues! Veuillez:
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Licence

LGPL-3.0 - voir le fichier LICENSE pour plus de détails.

## Support

Pour toute question ou problème, ouvrir une issue sur GitHub.
