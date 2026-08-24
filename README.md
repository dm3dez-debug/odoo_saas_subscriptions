# Odoo SaaS Subscriptions Module

## Description

Module complet de gestion des souscriptions SaaS pour instances Odoo. Ce module fournit une solution d'entreprise pour gérer les plans, les instances, les souscriptions et le monitoring des ressources.

## Caractéristiques principales

✅ **Gestion complète des plans** - Créez et gérez des plans SaaS flexibles
✅ **Instances Odoo** - Déployez et gérez des instances pour vos clients
✅ **Souscriptions clients** - Suivez les souscriptions avec facturation flexible
✅ **Monitoring des ressources** - Suivi en temps réel avec alertes
✅ **API REST** - Endpoints complets pour intégration tierce
✅ **Automatisation** - Renouvellement automatique, notifications, nettoyage
✅ **Rapports PDF** - Génération de rapports personnalisés
✅ **Interface web** - Vues conviviales avec formulaires et listes
✅ **Sécurité** - Contrôle d'accès par rôle
✅ **Traçabilité** - Historique complet des modifications

## Structure du projet

```
odoo_saas_subscriptions/
├── models/                          # Modèles de données
│   ├── __init__.py
│   ├── saas_plan.py                # Formules SaaS
│   ├── saas_instance.py            # Instances Odoo
│   ├── saas_subscription.py        # Souscriptions
│   ├── saas_resource.py            # Ressources
│   └── scheduler.py                # Tâches planifiées
├── controllers/                     # API REST
│   ├── __init__.py
│   └── main.py                     # Endpoints
├── views/                           # Interfaces Web
│   ├── saas_plan_views.xml
│   ├── saas_instance_views.xml
│   ├── saas_subscription_views.xml
│   ├── saas_resources_views.xml
│   └── menu_views.xml
├── security/                        # Sécurité
│   └── ir.model.access.csv         # Contrôles d'accès
├── data/                            # Données initiales
│   └── saas_plan_data.xml          # Plans par défaut
├── reports/                         # Rapports
│   └── subscription_report.xml     # Rapport PDF
├── utils/                           # Utilitaires
│   └── saas_utils.py               # Fonctions communes
├── static/                          # Assets statiques
├── __manifest__.py                  # Manifest du module
├── API_DOCUMENTATION.md             # Documentation API
├── INSTALLATION.md                  # Guide d'installation
├── CHANGELOG.md                     # Historique des versions
├── CONTRIBUTING.md                  # Guide de contribution
└── README.md                        # Ce fichier
```

## Installation rapide

### 1. Cloner le repository

```bash
cd /path/to/odoo/addons
git clone https://github.com/dm3dez-debug/odoo_saas_subscriptions.git
```

### 2. Redémarrer Odoo

```bash
sudo systemctl restart odoo
# ou
./odoo-bin -d database_name -u all
```

### 3. Installer le module

1. Aller à **Apps** > **Search Apps**
2. Chercher **"Odoo SaaS Subscriptions"**
3. Cliquer sur **"Install"**

Pour plus de détails, voir [INSTALLATION.md](INSTALLATION.md)

## Utilisation

### Créer un plan

1. Aller à **SaaS** > **Configuration** > **Plans**
2. Cliquer sur **"Créer"**
3. Remplir les informations du plan
4. Enregistrer

### Créer une instance

1. Aller à **SaaS** > **Gestion** > **Instances**
2. Cliquer sur **"Créer"**
3. Sélectionner le client et le plan
4. Configurer l'accès
5. Enregistrer et activer

### Gérer les souscriptions

1. Aller à **SaaS** > **Gestion** > **Souscriptions**
2. Créer ou modifier une souscription
3. Activer la souscription
4. Le système gère automatiquement les renouvellements

## API REST

### Exemples d'utilisation

#### Récupérer les plans disponibles

```bash
curl -X GET http://localhost:8069/saas/plans \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Récupérer les instances de l'utilisateur

```bash
curl -X GET http://localhost:8069/saas/instances \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Créer une sauvegarde

```bash
curl -X POST http://localhost:8069/saas/instance/1/backup \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Voir [API_DOCUMENTATION.md](API_DOCUMENTATION.md) pour la documentation complète.

## Modèles de données

### saas.plan
Définit une formule SaaS avec:
- Tarification (mensuelle/annuelle)
- Limites de ressources
- Fonctionnalités incluses
- Support et add-ons

### saas.instance
Représente une instance Odoo avec:
- Informations de base et d'accès
- État du cycle de vie
- Ressources allouées
- Monitoring (CPU, mémoire, stockage)
- Sauvegardes

### saas.subscription
Gère une souscription client avec:
- Lien au client, plan et instance
- État de la souscription
- Tarification flexible
- Renouvellement automatique
- Historique des factures

### saas.resource
Suit l'utilisation des ressources avec:
- Types de ressources (stockage, utilisateurs, etc.)
- Limites et utilisation actuelle
- Alertes configurables
- Historique des modifications

## Automatisations

Le module inclut des tâches planifiées (cron) pour:

- **Vérifier les expirations** - Vérifie et renouvelle les souscriptions
- **Envoyer les notifications** - Alerte les clients avant expiration
- **Nettoyer les instances** - Supprime les instances marquées anciennement

## Sécurité

- Contrôle d'accès granulaire par rôle
- Vérification des permissions sur chaque endpoint
- Isolation des données par client
- Chiffrement des mots de passe
- Audit trail complet

## Dépendances

- Odoo 19.0+
- mail module (pour les notifications)
- web module (pour les vues)

## Contribution

Les contributions sont bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les directives.

## Licence

LGPL-3.0 - Voir LICENSE pour plus de détails

## Support

- Documentation: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- Installation: [INSTALLATION.md](INSTALLATION.md)
- Changelog: [CHANGELOG.md](CHANGELOG.md)
- Ouvrir une issue sur GitHub

## Auteur

DM3DEZ Development - dm3dez@gmail.com

## Remerciements

Merci à la communauté Odoo pour l'inspiration et le support.
