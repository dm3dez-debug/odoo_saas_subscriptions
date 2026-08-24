from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaasPlan(models.Model):
    _name = 'saas.plan'
    _description = 'Plan ou Formule SaaS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    name = fields.Char('Nom du Plan', required=True, translate=True, tracking=True)
    code = fields.Char('Code', unique=True, required=True, tracking=True)
    description = fields.Text('Description', translate=True)
    sequence = fields.Integer('Séquence', default=10)
    active = fields.Boolean('Actif', default=True, tracking=True)
    
    # Tarification
    monthly_price = fields.Float('Prix Mensuel', required=True, tracking=True)
    yearly_price = fields.Float('Prix Annuel', tracking=True)
    currency_id = fields.Many2one('res.currency', 'Devise', required=True, 
                                    default=lambda self: self.env.company.currency_id)
    
    # Limite de ressources
    max_storage_gb = fields.Float('Stockage Maximum (GB)', required=True, tracking=True)
    max_users = fields.Integer('Nombre Maximum d\'Utilisateurs', required=True, tracking=True)
    max_databases = fields.Integer('Nombre Maximum de Bases de Données', default=1, tracking=True)
    
    # Fonctionnalités
    included_modules = fields.Integer('Modules Inclus', default=0, tracking=True)
    api_access = fields.Boolean('Accès API', default=False, tracking=True)
    priority_support = fields.Boolean('Support Prioritaire', default=False, tracking=True)
    advanced_reports = fields.Boolean('Rapports Avancés', default=False, tracking=True)
    automation_workflows = fields.Boolean('Workflows d\'Automatisation', default=False, tracking=True)
    custom_domain = fields.Boolean('Domaine Personnalisé', default=False, tracking=True)
    sso_enabled = fields.Boolean('SSO Activé', default=False, tracking=True)
    two_factor_auth = fields.Boolean('Authentification 2FA', default=False, tracking=True)
    
    # Relations
    subscription_ids = fields.One2many('saas.subscription', 'plan_id', 'Souscriptions')
    subscription_count = fields.Integer('Nombre de Souscriptions', compute='_compute_subscription_count')
    
    # Métadonnées
    created_at = fields.Datetime('Créé le', default=fields.Datetime.now, readonly=True)
    updated_at = fields.Datetime('Mis à jour le', default=fields.Datetime.now)
    notes = fields.Text('Notes Internes')

    @api.constrains('max_storage_gb', 'max_users')
    def _check_resources(self):
        for record in self:
            if record.max_storage_gb <= 0:
                raise ValidationError('Le stockage maximum doit être supérieur à 0.')
            if record.max_users <= 0:
                raise ValidationError('Le nombre maximum d\'utilisateurs doit être supérieur à 0.')

    @api.constrains('monthly_price', 'yearly_price')
    def _check_prices(self):
        for record in self:
            if record.monthly_price < 0 or record.yearly_price < 0:
                raise ValidationError('Les prix ne peuvent pas être négatifs.')

    @api.depends('subscription_ids')
    def _compute_subscription_count(self):
        for plan in self:
            plan.subscription_count = len(plan.subscription_ids)

    @api.model
    def create(self, vals):
        vals['updated_at'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        vals['updated_at'] = fields.Datetime.now()
        return super().write(vals)

    def toggle_active(self):
        """Active/Désactive le plan"""
        for record in self:
            record.active = not record.active
            _logger.info(f'Plan {record.name} status changed to {record.active}')

    def get_features_list(self):
        """Retourne la liste des fonctionnalités du plan"""
        features = []
        if self.api_access:
            features.append('Accès API')
        if self.priority_support:
            features.append('Support Prioritaire')
        if self.advanced_reports:
            features.append('Rapports Avancés')
        if self.automation_workflows:
            features.append('Workflows d\'Automatisation')
        if self.custom_domain:
            features.append('Domaine Personnalisé')
        if self.sso_enabled:
            features.append('SSO')
        if self.two_factor_auth:
            features.append('Authentification 2FA')
        return features
