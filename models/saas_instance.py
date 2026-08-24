from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging
import random
import string

_logger = logging.getLogger(__name__)


class SaasInstance(models.Model):
    _name = 'saas.instance'
    _description = 'Instance Odoo SaaS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Informations de base
    name = fields.Char('Nom de l\'Instance', required=True, tracking=True)
    code = fields.Char('Code d\'Instance', unique=True, readonly=True, tracking=True)
    description = fields.Text('Description', translate=True)
    
    # Client et Abonnement
    partner_id = fields.Many2one('res.partner', 'Client', required=True, tracking=True)
    plan_id = fields.Many2one('saas.plan', 'Plan/Formule', required=True, tracking=True)
    subscription_id = fields.Many2one('saas.subscription', 'Souscription', readonly=True, tracking=True)
    
    # Accès et URL
    instance_url = fields.Char('URL de l\'Instance', required=True, tracking=True)
    database_name = fields.Char('Nom de la Base de Données', required=True, tracking=True)
    admin_login = fields.Char('Login Admin', default='admin', tracking=True)
    admin_password = fields.Char('Mot de passe Admin', tracking=True)
    master_password = fields.Char('Mot de passe Maître', tracking=True)
    
    # État et Statut
    STATE_SELECTION = [
        ('draft', 'Brouillon'),
        ('creating', 'En création'),
        ('active', 'Actif'),
        ('suspended', 'Suspendu'),
        ('disabled', 'Désactivé'),
        ('deleting', 'En suppression'),
        ('deleted', 'Supprimé'),
    ]
    state = fields.Selection(STATE_SELECTION, 'État', default='draft', required=True, tracking=True)
    
    # Ressources allouées
    allocated_storage_gb = fields.Float('Stockage Alloué (GB)', tracking=True)
    used_storage_gb = fields.Float('Stockage Utilisé (GB)', default=0, tracking=True)
    storage_percentage = fields.Float('Pourcentage de Stockage', compute='_compute_storage_percentage')
    
    allocated_users = fields.Integer('Utilisateurs Alloués', tracking=True)
    active_users = fields.Integer('Utilisateurs Actifs', default=0, tracking=True)
    users_percentage = fields.Float('Pourcentage d\'Utilisateurs', compute='_compute_users_percentage')
    
    # Dates
    creation_date = fields.Datetime('Date de Création', default=fields.Datetime.now, readonly=True)
    activation_date = fields.Datetime('Date d\'Activation', tracking=True)
    suspension_date = fields.Datetime('Date de Suspension', tracking=True)
    deletion_date = fields.Datetime('Date de Suppression', tracking=True)
    last_backup_date = fields.Datetime('Dernière Sauvegarde', tracking=True)
    
    # Monitoring
    cpu_usage_percent = fields.Float('Utilisation CPU (%)', default=0)
    memory_usage_percent = fields.Float('Utilisation Mémoire (%)', default=0)
    database_size_mb = fields.Float('Taille Base de Données (MB)', default=0)
    
    # Ressources
    resource_ids = fields.One2many('saas.resource', 'instance_id', 'Ressources')
    resource_count = fields.Integer('Nombre de Ressources', compute='_compute_resource_count')
    
    # Configuration
    is_production = fields.Boolean('Production', default=False, tracking=True)
    white_label = fields.Boolean('White Label', default=False, tracking=True)
    custom_domain_name = fields.Char('Domaine Personnalisé', tracking=True)
    
    # Métadonnées
    notes = fields.Text('Notes Internes')
    tags = fields.Many2many('res.partner.category', string='Étiquettes')

    @api.model
    def create(self, vals):
        if not vals.get('code'):
            vals['code'] = self._generate_instance_code()
        if vals.get('plan_id'):
            plan = self.env['saas.plan'].browse(vals['plan_id'])
            vals['allocated_storage_gb'] = plan.max_storage_gb
            vals['allocated_users'] = plan.max_users
        return super().create(vals)

    def _generate_instance_code(self):
        """Génère un code unique pour l'instance"""
        while True:
            code = 'INST-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not self.env['saas.instance'].search([('code', '=', code)]):
                return code

    @api.depends('used_storage_gb', 'allocated_storage_gb')
    def _compute_storage_percentage(self):
        for record in self:
            if record.allocated_storage_gb > 0:
                record.storage_percentage = (record.used_storage_gb / record.allocated_storage_gb) * 100
            else:
                record.storage_percentage = 0

    @api.depends('active_users', 'allocated_users')
    def _compute_users_percentage(self):
        for record in self:
            if record.allocated_users > 0:
                record.users_percentage = (record.active_users / record.allocated_users) * 100
            else:
                record.users_percentage = 0

    @api.depends('resource_ids')
    def _compute_resource_count(self):
        for record in self:
            record.resource_count = len(record.resource_ids)

    @api.constrains('allocated_storage_gb', 'allocated_users')
    def _check_allocated_resources(self):
        for record in self:
            if record.allocated_storage_gb and record.allocated_storage_gb <= 0:
                raise ValidationError('Le stockage alloué doit être supérieur à 0.')
            if record.allocated_users and record.allocated_users <= 0:
                raise ValidationError('Le nombre d\'utilisateurs alloué doit être supérieur à 0.')

    def action_activate(self):
        """Active l'instance"""
        for record in self:
            if record.state == 'draft':
                record.write({
                    'state': 'active',
                    'activation_date': fields.Datetime.now()
                })
                _logger.info(f'Instance {record.name} activated')
                record.message_post(body='Instance activée')
            else:
                raise UserError(f'Impossible d\'activer une instance en état {record.state}')

    def action_suspend(self):
        """Suspend l'instance"""
        for record in self:
            if record.state == 'active':
                record.write({
                    'state': 'suspended',
                    'suspension_date': fields.Datetime.now()
                })
                _logger.info(f'Instance {record.name} suspended')
                record.message_post(body='Instance suspendue')
            else:
                raise UserError(f'Impossible de suspendre une instance en état {record.state}')

    def action_enable(self):
        """Réactive une instance suspendue"""
        for record in self:
            if record.state == 'suspended':
                record.write({
                    'state': 'active',
                    'suspension_date': False
                })
                _logger.info(f'Instance {record.name} re-enabled')
                record.message_post(body='Instance réactivée')
            else:
                raise UserError('Seules les instances suspendues peuvent être réactivées')

    def action_delete(self):
        """Marque l'instance comme supprimée"""
        for record in self:
            record.write({
                'state': 'deleted',
                'deletion_date': fields.Datetime.now()
            })
            _logger.info(f'Instance {record.name} marked as deleted')
            record.message_post(body='Instance supprimée')

    def action_update_resources(self):
        """Met à jour les ressources allouées en fonction du plan"""
        for record in self:
            if record.plan_id:
                record.allocated_storage_gb = record.plan_id.max_storage_gb
                record.allocated_users = record.plan_id.max_users
                _logger.info(f'Resources updated for instance {record.name}')
                record.message_post(body='Ressources mises à jour selon le plan')

    def action_backup(self):
        """Crée une sauvegarde de l'instance"""
        for record in self:
            record.last_backup_date = fields.Datetime.now()
            _logger.info(f'Backup created for instance {record.name}')
            record.message_post(body='Sauvegarde créée')

    def get_resource_summary(self):
        """Retourne un résumé de l'utilisation des ressources"""
        return {
            'storage_used_percent': self.storage_percentage,
            'users_used_percent': self.users_percentage,
            'storage_gb': f'{self.used_storage_gb:.2f} / {self.allocated_storage_gb:.2f}',
            'users': f'{self.active_users} / {self.allocated_users}',
        }
