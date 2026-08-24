# Installation Guide - Module Odoo SaaS Subscriptions

## Prérequis

- Odoo 19.0 ou supérieur
- Python 3.8+
- PostgreSQL 12+
- Accès administrateur à Odoo

## Installation Step by Step

### 1. Cloner le repository

```bash
cd /path/to/odoo/addons
git clone https://github.com/dm3dez-debug/odoo_saas_subscriptions.git
cd odoo_saas_subscriptions
```

### 2. Copier dans le répertoire addons d'Odoo

```bash
cp -r . /path/to/odoo/addons/odoo_saas_subscriptions
```

### 3. Redémarrer le serveur Odoo

```bash
cd /path/to/odoo
./odoo-bin -d votre_base_de_donnees -u all
```

Ou avec systemd:

```bash
sudo systemctl restart odoo
```

### 4. Activer le mode développement

Dans Odoo:
1. Aller à Settings > General Settings
2. Activer "Developer Mode"

### 5. Installer le module

1. Aller à Apps > Search Apps
2. Chercher "Odoo SaaS Subscriptions"
3. Cliquer sur "Install"

## Post-Installation

### 1. Créer les premières données

1. Aller à SaaS > Configuration > Plans
2. Vérifier que les plans par défaut sont créés
3. Personnaliser si nécessaire

### 2. Configurer les droits d'accès

1. Aller à Settings > Users & Companies > Users
2. Sélectionner l'utilisateur
3. Assigner les rues SaaS appropriés

### 3. Configurer les tâches planifiées

1. Aller à Settings > Technical > Scheduled Actions
2. Vérifier que les tâches SaaS sont activées:
   - Check Subscriptions Expiration
   - Send Expiration Notifications
   - Cleanup Deleted Instances

## Troubleshooting

### Erreur: Module not found

```bash
# Vérifier que le module est dans le bon répertoire
ls -la /path/to/odoo/addons/odoo_saas_subscriptions

# Redémarrer Odoo avec -u all
./odoo-bin -d database_name -u all
```

### Erreur: Access Denied

- Vérifier les droits de fichier
- Vérifier les permissions de l'utilisateur PostgreSQL
- Redemarrer le service

### Les plans par défaut ne sont pas créés

```bash
# Redémarrer le module
./odoo-bin -d database_name -u odoo_saas_subscriptions
```

## Mise à jour

```bash
cd /path/to/odoo/addons/odoo_saas_subscriptions
git pull origin main

# Redémarrer Odoo
sudo systemctl restart odoo
```

## Désinstallation

1. Aller à Apps
2. Chercher "Odoo SaaS Subscriptions"
3. Cliquer sur le module
4. Cliquer sur "Uninstall"

## Support

Pour toute question ou problème:
- Consulter la documentation: API_DOCUMENTATION.md
- Ouvrir une issue sur GitHub
- Contacter l'équipe de support
