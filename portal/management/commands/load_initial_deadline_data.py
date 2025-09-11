# management/commands/load_initial_deadline_data.py
from django.core.management.base import BaseCommand
from portal.models import PriorityLevel, DeadlineType
from portal.models import QueryCategory, QueryPriority, QueryStatus

class Command(BaseCommand):
    help = 'Load initial deadline and priority data'

    def handle(self, *args, **options):
        # Create priority levels
     

        # Create categories
        categories = [
            ('Data Quality', 'Issues related to data accuracy and completeness'),
            ('Follow-up Required', 'Cases that require additional follow-up'),
            ('Clarification Needed', 'Questions needing clarification'),
            ('Technical Issue', 'Technical problems with data collection'),
            ('Other', 'Other types of queries'),
        ]

        for name, description in categories:
            QueryCategory.objects.get_or_create(name=name, defaults={'description': description})

        # Create priorities
        priorities = [
            ('High', '#dc3545', 'Urgent issues requiring immediate attention'),
            ('Medium', '#ffc107', 'Important issues that should be addressed soon'),
            ('Low', '#28a745', 'Issues that can be addressed when convenient'),
        ]

        for name, color, description in priorities:
            QueryPriority.objects.get_or_create(name=name, defaults={'color': color, 'description': description})

        # Create statuses
        statuses = [
            ('Open', '#6c757d', 'Query is open and awaiting response'),
            ('In Progress', '#17a2b8', 'Query is being worked on'),
            ('Resolved', '#28a745', 'Query has been resolved'),
            ('Closed', '#6c757d', 'Query has been closed'),
        ]

        for name, color, description in statuses:
            QueryStatus.objects.get_or_create(name=name, defaults={'color': color, 'description': description})