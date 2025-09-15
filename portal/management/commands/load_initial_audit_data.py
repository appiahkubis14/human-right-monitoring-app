# management/commands/load_initial_audit_data.py
from django.core.management.base import BaseCommand
from portal.models import AuditStatus, AuditType

class Command(BaseCommand):
    help = 'Load initial audit data'

    def handle(self, *args, **options):
        # Create audit statuses
        statuses = [
            {'name': 'Pending', 'color': '#6c757d', 'description': 'Audit is pending'},
            {'name': 'In Progress', 'color': '#007bff', 'description': 'Audit is in progress'},
            {'name': 'Completed', 'color': '#28a745', 'description': 'Audit completed successfully'},
            {'name': 'Failed', 'color': '#dc3545', 'description': 'Audit failed'},
            {'name': 'Cancelled', 'color': '#6c757d', 'description': 'Audit was cancelled'},
        ]
        
        for status_data in statuses:
            AuditStatus.objects.get_or_create(**status_data)
        
        # Create audit types
        types = [
            {'name': 'Data Validation', 'description': 'Validation of submitted data'},
            {'name': 'Field Verification', 'description': 'Physical verification in the field'},
            {'name': 'Photo Verification', 'description': 'Verification of uploaded photos'},
            {'name': 'GPS Verification', 'description': 'Verification of GPS coordinates'},
            {'name': 'Phone Verification', 'description': 'Verification via phone call'},
            {'name': 'Random Check', 'description': 'Random quality check'},
        ]
        
        for type_data in types:
            AuditType.objects.get_or_create(**type_data)
        
        self.stdout.write(self.style.SUCCESS('Successfully loaded initial audit data'))