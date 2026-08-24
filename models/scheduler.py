from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaasSubscriptionScheduler(models.Model):
    """Tâche planifiée pour la gestion automatique des souscriptions"""
    _name = 'saas.subscription.scheduler'
    _description = 'Scheduleur SaaS'

    def check_subscriptions_expiration(self):
        """Vérifie les souscriptions expirées et renouvelle les automatiques"""
        _logger.info('Running subscription expiration check')
        subscription_model = self.env['saas.subscription']
        subscription_model.action_check_expiration()
        _logger.info('Subscription expiration check completed')

    def send_expiration_notifications(self):
        """Envoie les notifications d'expiration prochaine"""
        _logger.info('Sending expiration notifications')
        subscription_model = self.env['saas.subscription']
        subscription_model.send_expiration_notification()
        _logger.info('Expiration notifications sent')

    def cleanup_deleted_instances(self):
        """Nettoie les instances marquées comme supprimées"""
        _logger.info('Cleaning up deleted instances')
        deleted_cutoff = datetime.now() - timedelta(days=30)
        instances = self.env['saas.instance'].search([
            ('state', '=', 'deleted'),
            ('deletion_date', '<=', deleted_cutoff)
        ])
        _logger.info(f'Found {len(instances)} instances to cleanup')
        instances.unlink()
        _logger.info('Cleanup completed')
