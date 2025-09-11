# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import childHeavyTaskTbl, childLightTaskTbl, childHeavyTask12MonthsTbl, childLightTask12MonthsTbl
from .risk_assessment_utils import RiskAssessmentCalculator

@receiver(post_save, sender=childHeavyTaskTbl)
@receiver(post_save, sender=childLightTaskTbl)
@receiver(post_save, sender=childHeavyTask12MonthsTbl)
@receiver(post_save, sender=childLightTask12MonthsTbl)
@receiver(post_delete, sender=childHeavyTaskTbl)
@receiver(post_delete, sender=childLightTaskTbl)
@receiver(post_delete, sender=childHeavyTask12MonthsTbl)
@receiver(post_delete, sender=childLightTask12MonthsTbl)
def trigger_risk_assessment(sender, instance, **kwargs):
    """
    Trigger risk assessment when child task data changes
    """
    try:
        child = instance.child
        RiskAssessmentCalculator.perform_risk_assessment(child)
    except Exception as e:
        # Log error but don't break the application
        print(f"Error in risk assessment for child {instance.child_id}: {str(e)}")

# Connect the signal when the app is ready
def ready():
    import django
    if django.apps.apps.ready:
        from django.apps import AppConfig
        class YourAppConfig(AppConfig):
            name = 'your_app_name'
            def ready(self):
                import portal.signals