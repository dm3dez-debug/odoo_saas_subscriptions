from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaasSubscription(models.Model):
    _name = 'saas.subscription'
    _description = 'Souscription SaaS Client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    # Informations de base
    name = fields.Char('Référence', required=True, readonly=True, tracking=True)
    partner_id = fields.Many2one('res.partner', 'Client', required=True, tracking=True, ondelete='restrict')
    
    # Liaisons
    plan_id = fields.Many2one('saas.plan', 'Plan/Formule', required=True, tracking=True, ondelete='restrict')
    instance_id = fields.Many2one('saas.instance', 'Instance Odoo', required=True, tracking=True, ondelete='restrict')
    sale_order_id = fields.Many2one('sale.order', 'Commande de Vente', tracking=True)
    invoice_ids = fields.Many2many('account.move', string='Factures')
    
    # Statut
    STATE_SELECTION = [
        ('draft', 'Brouillon'),
        ('pending', 'En attente d\'activation'),
        ('active', 'Active'),
        ('paused', 'Mise en pause'),
        ('expired', 'Expirée'),
        ('cancelled', 'Annulée'),
    ]
    state = fields.Selection(STATE_SELECTION, 'État', default='draft', required=True, tracking=True)
    
    # Dates
    start_date = fields.Date('Date de Début', required=True, tracking=True)
    end_date = fields.Date('Date de Fin', tracking=True)
    next_renewal_date = fields.Date('Date de Renouvellement', compute='_compute_next_renewal_date', tracking=True)
    last_renewal_date = fields.Date('Dernière Date de Renouvellement', readonly=True, tracking=True)
    trial_end_date = fields.Date('Fin de la Période d\'Essai', tracking=True)
    
    # Tarification
    BILLING_PERIOD_SELECTION = [
        ('monthly', 'Mensuel'),
        ('quarterly', 'Trimestriel'),
        ('yearly', 'Annuel'),
    ]
    billing_period = fields.Selection(BILLING_PERIOD_SELECTION, 'Période de Facturation', 
                                      default='monthly', required=True, tracking=True)
    amount = fields.Float('Montant', compute='_compute_amount', tracking=True)
    currency_id = fields.Many2one('res.currency', 'Devise', required=True,
                                   default=lambda self: self.env.company.currency_id)
    discount_percent = fields.Float('Remise (%)', default=0, tracking=True)
    discount_amount = fields.Float('Montant Remise', compute='_compute_discount_amount')
    net_amount = fields.Float('Montant Net', compute='_compute_net_amount')
    
    # Configuration
    is_trial = fields.Boolean('Période d\'Essai', default=False, tracking=True)
    auto_renewal = fields.Boolean('Renouvellement Automatique', default=True, tracking=True)
    auto_upgrade = fields.Boolean('Montée en Gamme Automatique', default=False, tracking=True)
    notification_sent = fields.Boolean('Notification d\'Expiration Envoyée', default=False)
    
    # Personnalisation
    custom_config = fields.Json('Configuration Personnalisée', default={})
    notes = fields.Text('Notes Internes')
    
    # Métadonnées
    created_at = fields.Datetime('Créé le', default=fields.Datetime.now, readonly=True)
    updated_at = fields.Datetime('Mis à jour le', default=fields.Datetime.now)

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = self.env['ir.sequence'].next_by_code('saas.subscription') or 'NEW'
        vals['updated_at'] = fields.Datetime.now()
        return super().create(vals)

    def write(self, vals):
        vals['updated_at'] = fields.Datetime.now()
        return super().write(vals)

    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        for record in self:
            if record.end_date and record.start_date > record.end_date:
                raise ValidationError('La date de début doit être antérieure à la date de fin.')

    @api.constrains('discount_percent')
    def _check_discount(self):
        for record in self:
            if record.discount_percent < 0 or record.discount_percent > 100:
                raise ValidationError('Le pourcentage de remise doit être entre 0 et 100.')

    @api.depends('billing_period', 'plan_id')
    def _compute_amount(self):
        for record in self:
            if record.plan_id:
                if record.billing_period == 'monthly':
                    record.amount = record.plan_id.monthly_price
                elif record.billing_period == 'quarterly':
                    record.amount = record.plan_id.monthly_price * 3
                elif record.billing_period == 'yearly':
                    record.amount = record.plan_id.yearly_price or record.plan_id.monthly_price * 12
            else:
                record.amount = 0

    @api.depends('amount', 'discount_percent')
    def _compute_discount_amount(self):
        for record in self:
            record.discount_amount = record.amount * (record.discount_percent / 100)

    @api.depends('amount', 'discount_amount')
    def _compute_net_amount(self):
        for record in self:
            record.net_amount = record.amount - record.discount_amount

    @api.depends('start_date', 'billing_period')
    def _compute_next_renewal_date(self):
        for record in self:
            if record.start_date:
                start = datetime.strptime(str(record.start_date), '%Y-%m-%d')
                if record.billing_period == 'monthly':
                    delta = timedelta(days=30)
                elif record.billing_period == 'quarterly':
                    delta = timedelta(days=90)
                else:  # yearly
                    delta = timedelta(days=365)
                record.next_renewal_date = (start + delta).date()
            else:
                record.next_renewal_date = False

    @api.onchange('plan_id')
    def _onchange_plan(self):
        """Met à jour l'instance quand le plan change"""
        if self.plan_id and self.instance_id:
            self.instance_id.plan_id = self.plan_id
            self.instance_id.action_update_resources()

    def action_activate(self):
        """Active la souscription"""
        for record in self:
            if record.state == 'draft':
                record.write({
                    'state': 'active',
                })
                if record.instance_id.state == 'draft':
                    record.instance_id.action_activate()
                _logger.info(f'Subscription {record.name} activated')
                record.message_post(body='Souscription activée')
            else:
                raise UserError(f'Impossible d\'activer une souscription en état {record.state}')

    def action_pause(self):
        """Met la souscription en pause"""
        for record in self:
            if record.state == 'active':
                record.write({'state': 'paused'})
                if record.instance_id.state == 'active':
                    record.instance_id.action_suspend()
                _logger.info(f'Subscription {record.name} paused')
                record.message_post(body='Souscription mise en pause')
            else:
                raise UserError('Seules les souscriptions actives peuvent être mises en pause')

    def action_resume(self):
        """Reprend une souscription en pause"""
        for record in self:
            if record.state == 'paused':
                record.write({'state': 'active'})
                if record.instance_id.state == 'suspended':
                    record.instance_id.action_enable()
                _logger.info(f'Subscription {record.name} resumed')
                record.message_post(body='Souscription reprise')
            else:
                raise UserError('Seules les souscriptions en pause peuvent être reprises')

    def action_cancel(self):
        """Annule la souscription"""
        for record in self:
            if record.state != 'cancelled':
                record.write({'state': 'cancelled'})
                if record.instance_id.state != 'deleted':
                    record.instance_id.action_delete()
                _logger.info(f'Subscription {record.name} cancelled')
                record.message_post(body='Souscription annulée')
            else:
                raise UserError('Cette souscription est déjà annulée')

    def action_renew(self):
        """Renouvelle la souscription"""
        for record in self:
            old_start = record.start_date
            if record.billing_period == 'monthly':
                new_start = old_start + timedelta(days=30)
            elif record.billing_period == 'quarterly':
                new_start = old_start + timedelta(days=90)
            else:  # yearly
                new_start = old_start + timedelta(days=365)
            
            record.write({
                'start_date': new_start,
                'last_renewal_date': fields.Date.today(),
                'notification_sent': False,
            })
            _logger.info(f'Subscription {record.name} renewed')
            record.message_post(body='Souscription renouvelée')

    def action_upgrade_plan(self, new_plan_id):
        """Upgrade vers un nouveau plan"""
        new_plan = self.env['saas.plan'].browse(new_plan_id)
        for record in self:
            record.write({
                'plan_id': new_plan_id,
            })
            if record.instance_id:
                record.instance_id.write({
                    'plan_id': new_plan_id,
                    'allocated_storage_gb': new_plan.max_storage_gb,
                    'allocated_users': new_plan.max_users,
                })
            _logger.info(f'Subscription {record.name} upgraded to plan {new_plan.name}')
            record.message_post(body=f'Plan upgradé à {new_plan.name}')

    def action_check_expiration(self):
        """Vérifie et gère les souscriptions expirées"""
        today = fields.Date.today()
        expired = self.search([('end_date', '<=', today), ('state', '=', 'active')])
        for record in expired:
            if record.auto_renewal and record.next_renewal_date <= today:
                record.action_renew()
            else:
                record.write({'state': 'expired'})
                _logger.info(f'Subscription {record.name} marked as expired')

    def send_expiration_notification(self, days_before=7):
        """Envoie une notification d'expiration prochaine"""
        today = fields.Date.today()
        expiring_soon = self.search([
            ('next_renewal_date', '<=', today + timedelta(days=days_before)),
            ('next_renewal_date', '>', today),
            ('notification_sent', '=', False),
        ])
        for record in expiring_soon:
            record.notification_sent = True
            _logger.info(f'Expiration notification sent for {record.name}')
