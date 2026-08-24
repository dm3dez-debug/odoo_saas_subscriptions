# -*- coding: utf-8 -*-
"""
Utilitaires pour le module SaaS
"""

import re
from datetime import datetime, timedelta


class SaasUtils:
    """Classe utilitaire pour les fonctions SaaS communes"""

    @staticmethod
    def validate_domain_name(domain):
        """
        Valide un nom de domaine
        """
        pattern = r'^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$'
        return re.match(pattern, domain.lower()) is not None

    @staticmethod
    def validate_database_name(db_name):
        """
        Valide un nom de base de données
        """
        pattern = r'^[a-z0-9_-]+$'
        return re.match(pattern, db_name.lower()) is not None and len(db_name) >= 3

    @staticmethod
    def calculate_renewal_date(start_date, billing_period):
        """
        Calcule la date de renouvellement en fonction de la période de facturation
        """
        if billing_period == 'monthly':
            return start_date + timedelta(days=30)
        elif billing_period == 'quarterly':
            return start_date + timedelta(days=90)
        elif billing_period == 'yearly':
            return start_date + timedelta(days=365)
        return start_date

    @staticmethod
    def calculate_prorated_amount(original_amount, start_date, end_date):
        """
        Calcule le montant au pro rata pour les périodes partielles
        """
        total_days = (end_date - start_date).days
        if total_days == 0:
            return original_amount
        daily_rate = original_amount / 30  # Suppose un mois de 30 jours
        return daily_rate * total_days

    @staticmethod
    def format_storage_size(size_gb):
        """
        Formate la taille de stockage de manière lisible
        """
        if size_gb < 1:
            return f"{size_gb * 1024:.2f} MB"
        elif size_gb < 1024:
            return f"{size_gb:.2f} GB"
        else:
            return f"{size_gb / 1024:.2f} TB"

    @staticmethod
    def get_alert_level(usage_percentage):
        """
        Retourne le niveau d'alerte en fonction du pourcentage d'utilisation
        """
        if usage_percentage >= 95:
            return 'critical'
        elif usage_percentage >= 80:
            return 'warning'
        else:
            return 'normal'

    @staticmethod
    def generate_support_ticket_data(subscription):
        """
        Génère les données pour un ticket de support lié à une souscription
        """
        return {
            'subject': f'Support: {subscription.name}',
            'partner_id': subscription.partner_id.id,
            'subscription_id': subscription.id,
            'instance_id': subscription.instance_id.id,
            'plan_id': subscription.plan_id.id,
        }
