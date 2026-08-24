from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class SaasController(http.Controller):
    """Contrôleur pour les endpoints SaaS"""

    @http.route('/saas/plans', auth='user', methods=['GET'], type='json')
    def get_plans(self, **kwargs):
        """Retourne la liste des plans disponibles"""
        try:
            plans = request.env['saas.plan'].search([('active', '=', True)])
            plans_data = []
            for plan in plans:
                plans_data.append({
                    'id': plan.id,
                    'name': plan.name,
                    'code': plan.code,
                    'description': plan.description,
                    'monthly_price': plan.monthly_price,
                    'yearly_price': plan.yearly_price,
                    'max_storage_gb': plan.max_storage_gb,
                    'max_users': plan.max_users,
                    'features': plan.get_features_list(),
                })
            return {'status': 'success', 'data': plans_data}
        except Exception as e:
            _logger.error(f'Error fetching plans: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/plan/<int:plan_id>', auth='user', methods=['GET'], type='json')
    def get_plan_details(self, plan_id, **kwargs):
        """Retourne les détails d'un plan spécifique"""
        try:
            plan = request.env['saas.plan'].browse(plan_id)
            if not plan.exists():
                return {'status': 'error', 'message': 'Plan not found'}
            
            return {
                'status': 'success',
                'data': {
                    'id': plan.id,
                    'name': plan.name,
                    'code': plan.code,
                    'description': plan.description,
                    'monthly_price': plan.monthly_price,
                    'yearly_price': plan.yearly_price,
                    'max_storage_gb': plan.max_storage_gb,
                    'max_users': plan.max_users,
                    'included_modules': plan.included_modules,
                    'max_databases': plan.max_databases,
                    'features': plan.get_features_list(),
                    'subscription_count': plan.subscription_count,
                }
            }
        except Exception as e:
            _logger.error(f'Error fetching plan details: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/instances', auth='user', methods=['GET'], type='json')
    def get_instances(self, **kwargs):
        """Retourne la liste des instances de l'utilisateur"""
        try:
            user = request.env.user
            instances = request.env['saas.instance'].search([('partner_id', '=', user.partner_id.id)])
            
            instances_data = []
            for instance in instances:
                instances_data.append({
                    'id': instance.id,
                    'name': instance.name,
                    'code': instance.code,
                    'instance_url': instance.instance_url,
                    'state': instance.state,
                    'plan': instance.plan_id.name,
                    'storage_percentage': instance.storage_percentage,
                    'users_percentage': instance.users_percentage,
                    'allocated_storage_gb': instance.allocated_storage_gb,
                    'used_storage_gb': instance.used_storage_gb,
                    'allocated_users': instance.allocated_users,
                    'active_users': instance.active_users,
                })
            
            return {'status': 'success', 'data': instances_data}
        except Exception as e:
            _logger.error(f'Error fetching instances: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/instance/<int:instance_id>', auth='user', methods=['GET'], type='json')
    def get_instance_details(self, instance_id, **kwargs):
        """Retourne les détails d'une instance"""
        try:
            instance = request.env['saas.instance'].browse(instance_id)
            if not instance.exists():
                return {'status': 'error', 'message': 'Instance not found'}
            
            # Vérifier que l'utilisateur a accès à cette instance
            user = request.env.user
            if instance.partner_id.id != user.partner_id.id:
                return {'status': 'error', 'message': 'Access denied'}
            
            resource_summary = instance.get_resource_summary()
            
            return {
                'status': 'success',
                'data': {
                    'id': instance.id,
                    'name': instance.name,
                    'code': instance.code,
                    'instance_url': instance.instance_url,
                    'database_name': instance.database_name,
                    'state': instance.state,
                    'plan': instance.plan_id.name,
                    'partner': instance.partner_id.name,
                    'creation_date': instance.creation_date.isoformat() if instance.creation_date else None,
                    'activation_date': instance.activation_date.isoformat() if instance.activation_date else None,
                    'last_backup_date': instance.last_backup_date.isoformat() if instance.last_backup_date else None,
                    'resources': resource_summary,
                    'cpu_usage_percent': instance.cpu_usage_percent,
                    'memory_usage_percent': instance.memory_usage_percent,
                    'database_size_mb': instance.database_size_mb,
                    'is_production': instance.is_production,
                }
            }
        except Exception as e:
            _logger.error(f'Error fetching instance details: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/subscriptions', auth='user', methods=['GET'], type='json')
    def get_subscriptions(self, **kwargs):
        """Retourne la liste des souscriptions de l'utilisateur"""
        try:
            user = request.env.user
            subscriptions = request.env['saas.subscription'].search([('partner_id', '=', user.partner_id.id)])
            
            subscriptions_data = []
            for sub in subscriptions:
                subscriptions_data.append({
                    'id': sub.id,
                    'name': sub.name,
                    'state': sub.state,
                    'plan': sub.plan_id.name,
                    'instance': sub.instance_id.name,
                    'start_date': sub.start_date.isoformat() if sub.start_date else None,
                    'next_renewal_date': sub.next_renewal_date.isoformat() if sub.next_renewal_date else None,
                    'billing_period': sub.billing_period,
                    'amount': sub.amount,
                    'net_amount': sub.net_amount,
                    'auto_renewal': sub.auto_renewal,
                })
            
            return {'status': 'success', 'data': subscriptions_data}
        except Exception as e:
            _logger.error(f'Error fetching subscriptions: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/subscription/<int:subscription_id>', auth='user', methods=['GET'], type='json')
    def get_subscription_details(self, subscription_id, **kwargs):
        """Retourne les détails d'une souscription"""
        try:
            subscription = request.env['saas.subscription'].browse(subscription_id)
            if not subscription.exists():
                return {'status': 'error', 'message': 'Subscription not found'}
            
            # Vérifier que l'utilisateur a accès à cette souscription
            user = request.env.user
            if subscription.partner_id.id != user.partner_id.id:
                return {'status': 'error', 'message': 'Access denied'}
            
            return {
                'status': 'success',
                'data': {
                    'id': subscription.id,
                    'name': subscription.name,
                    'state': subscription.state,
                    'plan': subscription.plan_id.name,
                    'instance': subscription.instance_id.name,
                    'start_date': subscription.start_date.isoformat() if subscription.start_date else None,
                    'end_date': subscription.end_date.isoformat() if subscription.end_date else None,
                    'next_renewal_date': subscription.next_renewal_date.isoformat() if subscription.next_renewal_date else None,
                    'billing_period': subscription.billing_period,
                    'amount': subscription.amount,
                    'discount_percent': subscription.discount_percent,
                    'discount_amount': subscription.discount_amount,
                    'net_amount': subscription.net_amount,
                    'auto_renewal': subscription.auto_renewal,
                    'is_trial': subscription.is_trial,
                }
            }
        except Exception as e:
            _logger.error(f'Error fetching subscription details: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/instance/<int:instance_id>/resources', auth='user', methods=['GET'], type='json')
    def get_instance_resources(self, instance_id, **kwargs):
        """Retourne les ressources d'une instance"""
        try:
            instance = request.env['saas.instance'].browse(instance_id)
            if not instance.exists():
                return {'status': 'error', 'message': 'Instance not found'}
            
            # Vérifier l'accès
            user = request.env.user
            if instance.partner_id.id != user.partner_id.id:
                return {'status': 'error', 'message': 'Access denied'}
            
            resources_data = []
            for resource in instance.resource_ids:
                resources_data.append({
                    'id': resource.id,
                    'type': resource.resource_type,
                    'limit_value': resource.limit_value,
                    'unit': resource.unit,
                    'current_usage': resource.current_usage,
                    'usage_percentage': resource.usage_percentage,
                    'is_warning': resource.is_warning,
                    'is_alert': resource.is_alert,
                })
            
            return {'status': 'success', 'data': resources_data}
        except Exception as e:
            _logger.error(f'Error fetching resources: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/instance/<int:instance_id>/backup', auth='user', methods=['POST'], type='json')
    def create_instance_backup(self, instance_id, **kwargs):
        """Crée une sauvegarde d'une instance"""
        try:
            instance = request.env['saas.instance'].browse(instance_id)
            if not instance.exists():
                return {'status': 'error', 'message': 'Instance not found'}
            
            # Vérifier l'accès
            user = request.env.user
            if instance.partner_id.id != user.partner_id.id:
                return {'status': 'error', 'message': 'Access denied'}
            
            instance.action_backup()
            return {
                'status': 'success',
                'message': 'Backup created successfully',
                'last_backup': instance.last_backup_date.isoformat() if instance.last_backup_date else None
            }
        except Exception as e:
            _logger.error(f'Error creating backup: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/subscription/<int:subscription_id>/renew', auth='user', methods=['POST'], type='json')
    def renew_subscription(self, subscription_id, **kwargs):
        """Renouvelle une souscription"""
        try:
            subscription = request.env['saas.subscription'].browse(subscription_id)
            if not subscription.exists():
                return {'status': 'error', 'message': 'Subscription not found'}
            
            # Vérifier l'accès
            user = request.env.user
            if subscription.partner_id.id != user.partner_id.id:
                return {'status': 'error', 'message': 'Access denied'}
            
            subscription.action_renew()
            return {
                'status': 'success',
                'message': 'Subscription renewed successfully',
                'next_renewal_date': subscription.next_renewal_date.isoformat() if subscription.next_renewal_date else None
            }
        except Exception as e:
            _logger.error(f'Error renewing subscription: {str(e)}')
            return {'status': 'error', 'message': str(e)}

    @http.route('/saas/health', auth='public', methods=['GET'], type='json')
    def health_check(self, **kwargs):
        """Endpoint de santé pour vérifier que le service est actif"""
        return {'status': 'ok', 'message': 'Odoo SaaS Service is running'}
