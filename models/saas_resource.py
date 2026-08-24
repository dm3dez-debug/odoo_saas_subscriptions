from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaasResource(models.Model):
    _name = 'saas.resource'
    _description = 'Ressource d\'Instance SaaS'
    _order = 'instance_id, resource_type'

    # Relations
    instance_id = fields.Many2one('saas.instance', 'Instance', required=True, ondelete='cascade')
    plan_id = fields.Many2one('saas.plan', 'Plan', related='instance_id.plan_id', store=True)
    
    # Type de ressource
    RESOURCE_TYPE_SELECTION = [
        ('storage', 'Stockage'),
        ('users', 'Utilisateurs'),
        ('modules', 'Modules'),
        ('databases', 'Bases de Données'),
        ('api_calls', 'Appels API'),
        ('emails', 'Emails'),
        ('webhooks', 'Webhooks'),
    ]
    resource_type = fields.Selection(RESOURCE_TYPE_SELECTION, 'Type de Ressource', required=True)
    
    # Limites
    limit_value = fields.Float('Limite', required=True, tracking=True)
    unit = fields.Char('Unité', default='', help='GB, MB, COUNT, etc.')
    
    # Utilisation
    current_usage = fields.Float('Utilisation Actuelle', default=0, tracking=True)
    usage_percentage = fields.Float('Pourcentage d\'Utilisation', compute='_compute_usage_percentage')
    
    # Alertes
    warning_threshold = fields.Float('Seuil d\'Avertissement (%)', default=80, help='Pourcentage déclenchant une alerte')
    alert_threshold = fields.Float('Seuil d\'Alerte (%)', default=95, help='Pourcentage déclenchant une alerte critique')
    is_warning = fields.Boolean('Avertissement', compute='_compute_alert_status')
    is_alert = fields.Boolean('Alerte Critique', compute='_compute_alert_status')
    
    # Métadonnées
    last_updated = fields.Datetime('Dernière Mise à Jour', default=fields.Datetime.now)
    notes = fields.Text('Notes')

    @api.constrains('limit_value', 'current_usage')
    def _check_values(self):
        for record in self:
            if record.limit_value <= 0:
                raise ValidationError('La limite doit être supérieure à 0.')
            if record.current_usage < 0:
                raise ValidationError('L\'utilisation actuelle ne peut pas être négative.')

    @api.constrains('warning_threshold', 'alert_threshold')
    def _check_thresholds(self):
        for record in self:
            if record.warning_threshold > record.alert_threshold:
                raise ValidationError('Le seuil d\'avertissement doit être inférieur au seuil d\'alerte.')
            if record.warning_threshold < 0 or record.alert_threshold < 0:
                raise ValidationError('Les seuils ne peuvent pas être négatifs.')
            if record.warning_threshold > 100 or record.alert_threshold > 100:
                raise ValidationError('Les seuils ne peuvent pas dépasser 100%.')

    @api.depends('current_usage', 'limit_value')
    def _compute_usage_percentage(self):
        for record in self:
            if record.limit_value > 0:
                record.usage_percentage = (record.current_usage / record.limit_value) * 100
            else:
                record.usage_percentage = 0

    @api.depends('usage_percentage', 'warning_threshold', 'alert_threshold')
    def _compute_alert_status(self):
        for record in self:
            record.is_warning = record.usage_percentage >= record.warning_threshold and record.usage_percentage < record.alert_threshold
            record.is_alert = record.usage_percentage >= record.alert_threshold

    def update_usage(self, usage_value):
        """Met à jour l'utilisation de la ressource"""
        self.write({
            'current_usage': usage_value,
            'last_updated': fields.Datetime.now()
        })
        _logger.info(f'Resource {self.resource_type} usage updated to {usage_value}')
        self._check_alert_status()

    def _check_alert_status(self):
        """Vérifie et traite les alertes"""
        for record in self:
            if record.is_alert:
                _logger.warning(f'ALERT: Resource {record.resource_type} for instance {record.instance_id.name} has reached {record.usage_percentage:.2f}%')
                record._notify_alert()
            elif record.is_warning:
                _logger.warning(f'WARNING: Resource {record.resource_type} for instance {record.instance_id.name} is at {record.usage_percentage:.2f}%')
                record._notify_warning()

    def _notify_alert(self):
        """Envoie une notification d'alerte critique"""
        message = f'ALERTE CRITIQUE: La ressource {self.resource_type} de l\'instance {self.instance_id.name} a atteint {self.usage_percentage:.2f}%'
        _logger.error(message)
        self.instance_id.message_post(body=message)

    def _notify_warning(self):
        """Envoie une notification d'avertissement"""
        message = f'AVERTISSEMENT: La ressource {self.resource_type} de l\'instance {self.instance_id.name} est à {self.usage_percentage:.2f}%'
        _logger.warning(message)
        self.instance_id.message_post(body=message)

    @api.model
    def create_default_resources(self, instance_id):
        """Crée les ressources par défaut pour une nouvelle instance"""
        instance = self.env['saas.instance'].browse(instance_id)
        plan = instance.plan_id
        
        resources_to_create = [
            {
                'resource_type': 'storage',
                'limit_value': plan.max_storage_gb,
                'unit': 'GB',
                'current_usage': 0,
            },
            {
                'resource_type': 'users',
                'limit_value': plan.max_users,
                'unit': 'COUNT',
                'current_usage': 0,
            },
            {
                'resource_type': 'modules',
                'limit_value': plan.included_modules,
                'unit': 'COUNT',
                'current_usage': 0,
            },
            {
                'resource_type': 'databases',
                'limit_value': plan.max_databases,
                'unit': 'COUNT',
                'current_usage': 1,
            },
        ]
        
        for resource_data in resources_to_create:
            resource_data['instance_id'] = instance_id
            self.create(resource_data)
        
        _logger.info(f'Default resources created for instance {instance.name}')
