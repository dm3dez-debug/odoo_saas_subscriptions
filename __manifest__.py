{
    'name': 'Odoo SaaS Subscriptions',
    'version': '19.0.1.0.0',
    'category': 'SaaS',
    'summary': 'Module de gestion des souscriptions SaaS pour instances Odoo',
    'description': '''
Module complet pour gérer les souscriptions SaaS des clients aux instances Odoo.
Fonctionnalités principales:
- Gestion des instances Odoo (création, activation, désactivation, suppression)
- Gestion des formules et forfaits clients
- Allocation et gestion des espaces disques
- Suivi des ressources par instance
- Facturation automatique
    ''',
    'author': 'DM3DEZ Development',
    'website': 'https://github.com/dm3dez-debug/odoo_saas_subscriptions',
    'depends': ['base', 'sale', 'account', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/saas_plan_views.xml',
        'views/saas_instance_views.xml',
        'views/saas_subscription_views.xml',
        'views/saas_resources_views.xml',
        'views/menu_views.xml',
        'reports/subscription_report.xml',
        'data/saas_plan_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
