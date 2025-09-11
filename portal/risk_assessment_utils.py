# risk_assessment_utils.py
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from .models import (
    RiskAssessment, HeavyTaskRisk, LightTaskRisk, RiskAssessmentHistory,
    ChildInHouseholdTbl, childHeavyTaskTbl, childLightTaskTbl,
    childHeavyTask12MonthsTbl, childLightTask12MonthsTbl
)

class RiskAssessmentCalculator:
    """
    Utility class for calculating child labor risks
    """
    
    @staticmethod
    def calculate_child_age(child):
        """Calculate child's age based on year of birth"""
        current_year = datetime.now().year
        return current_year - child.child_year_birth
    
    @staticmethod
    def is_child_labour_light_task(age, total_hours, is_supervised, is_paid):
        """
        Determine if light task constitutes child labor based on criteria
        """
        # Normalize inputs
        total_hours = float(total_hours) if total_hours else 0
        is_supervised = str(is_supervised).lower() == 'yes' if isinstance(is_supervised, str) else bool(is_supervised)
        is_paid = str(is_paid).lower() == 'yes' if isinstance(is_paid, str) else bool(is_paid)
        
        if age < 10 and total_hours > 0:
            return True, f"Age {age} < 10 and worked {total_hours} hours"
        
        elif 10 <= age <= 14:
            if total_hours > 14:
                return True, f"Age {age} and worked {total_hours} hours (>14 limit)"
            elif total_hours > 10 and not is_supervised:
                return True, f"Age {age}, worked {total_hours} hours (>10 limit) without supervision"
        
        elif 15 <= age <= 17:
            if total_hours > 43:
                return True, f"Age {age} and worked {total_hours} hours (>43 limit)"
            elif total_hours > 30 and not is_supervised and is_paid:
                return True, f"Age {age}, worked {total_hours} hours (>30 limit) without supervision and paid"
        
        return False, "Does not meet child labor criteria"
    
    @staticmethod
    def assess_heavy_task_risk(child, heavy_tasks):
        """Assess heavy task risks for a child"""
        heavy_risks = []
        
        for task in heavy_tasks:
            # Check if child performed any heavy task (any heavy task constitutes risk)
            if hasattr(task, 'total_hours_school_days') and getattr(task, 'total_hours_school_days', 0) > 0:
                heavy_risks.append({
                    'task': task.task,
                    'task_name': task.task.name if task.task else 'Unknown Task',
                    'hours_worked': float(task.total_hours_school_days or 0)
                })
        
        return heavy_risks
    
    @staticmethod
    def assess_light_task_risk(child, light_tasks):
        """Assess light task risks for a child"""
        light_risks = []
        child_age = RiskAssessmentCalculator.calculate_child_age(child)
        
        for task in light_tasks:
            total_hours = 0
            is_supervised = False
            is_paid = False
            
            # Get task details from different possible sources
            if hasattr(task, 'total_hours_light_work_school'):
                total_hours = float(task.total_hours_light_work_school or 0)
            elif hasattr(task, 'total_hours_light_work_school_12'):
                total_hours = float(task.total_hours_light_work_school_12 or 0)
            
            if hasattr(task, 'under_supervision'):
                is_supervised = task.under_supermission.lower() == 'yes' if hasattr(task, 'under_supervision') else False
            elif hasattr(task, 'under_supervision_12'):
                is_supervised = task.under_supervision_12.lower() == 'yes' if hasattr(task, 'under_supervision_12') else False
            
            if hasattr(task, 'remuneration_received'):
                is_paid = task.remuneration_received.lower() == 'yes' if hasattr(task, 'remuneration_received') else False
            elif hasattr(task, 'remuneration_received_12months'):
                is_paid = task.remuneration_received_12months.lower() == 'yes' if hasattr(task, 'remuneration_received_12months') else False
            
            # Check if this constitutes child labor
            is_child_labor, criteria_details = RiskAssessmentCalculator.is_child_labour_light_task(
                child_age, total_hours, is_supervised, is_paid
            )
            
            if is_child_labor:
                light_risks.append({
                    'task': task.task,
                    'task_name': task.task.name if task.task else 'Unknown Task',
                    'total_hours': total_hours,
                    'is_supervised': is_supervised,
                    'is_paid': is_paid,
                    'child_age': child_age,
                    'meets_criteria': is_child_labor,
                    'criteria_details': criteria_details
                })
        
        return light_risks
    
    @staticmethod
    def perform_risk_assessment(child):
        """Perform comprehensive risk assessment for a child"""
        with transaction.atomic():
            # Get all task records for the child
            heavy_tasks_7days = childHeavyTaskTbl.objects.filter(child=child)
            light_tasks_7days = childLightTaskTbl.objects.filter(child=child)
            heavy_tasks_12months = childHeavyTask12MonthsTbl.objects.filter(child=child)
            light_tasks_12months = childLightTask12MonthsTbl.objects.filter(child=child)
            
            # Combine all tasks
            all_heavy_tasks = list(heavy_tasks_7days) + list(heavy_tasks_12months)
            all_light_tasks = list(light_tasks_7days) + list(light_tasks_12months)
            
            # Assess risks
            heavy_risks = RiskAssessmentCalculator.assess_heavy_task_risk(child, all_heavy_tasks)
            light_risks = RiskAssessmentCalculator.assess_light_task_risk(child, all_light_tasks)
            
            # Determine overall risk level
            has_heavy_risk = len(heavy_risks) > 0
            has_light_risk = len(light_risks) > 0
            
            if has_heavy_risk and has_light_risk:
                risk_level = 'both_risk'
            elif has_heavy_risk:
                risk_level = 'heavy_risk'
            elif has_light_risk:
                risk_level = 'light_risk'
            else:
                risk_level = 'no_risk'
            
            # Get or create risk assessment
            risk_assessment, created = RiskAssessment.objects.get_or_create(
                child=child,
                defaults={'risk_level': risk_level}
            )
            
            # Update if existing
            if not created:
                previous_risk_level = risk_assessment.risk_level
                risk_assessment.risk_level = risk_level
                risk_assessment.save()
                
                # Record history if risk level changed
                if previous_risk_level != risk_level:
                    RiskAssessmentHistory.objects.create(
                        risk_assessment=risk_assessment,
                        previous_risk_level=previous_risk_level,
                        new_risk_level=risk_level,
                        change_reason=f"Automated risk reassessment on {datetime.now()}"
                    )
            
            # Clear existing risks
            risk_assessment.heavy_task_risks.all().delete()
            risk_assessment.light_task_risks.all().delete()
            
            # Save heavy task risks
            for risk_data in heavy_risks:
                HeavyTaskRisk.objects.create(
                    risk_assessment=risk_assessment,
                    task=risk_data['task'],
                    task_name=risk_data['task_name'],
                    hours_worked=risk_data['hours_worked']
                )
            
            # Save light task risks
            for risk_data in light_risks:
                LightTaskRisk.objects.create(
                    risk_assessment=risk_assessment,
                    task=risk_data['task'],
                    task_name=risk_data['task_name'],
                    total_hours=risk_data['total_hours'],
                    is_supervised=risk_data['is_supervised'],
                    is_paid=risk_data['is_paid'],
                    child_age=risk_data['child_age'],
                    meets_criteria=risk_data['meets_criteria'],
                    criteria_details=risk_data['criteria_details']
                )
            
            return risk_assessment
    
    @staticmethod
    def assess_all_children():
        """Perform risk assessment for all children"""
        children = ChildInHouseholdTbl.objects.all()
        results = {
            'total_children': children.count(),
            'assessed_children': 0,
            'heavy_risk': 0,
            'light_risk': 0,
            'both_risk': 0,
            'no_risk': 0,
            'errors': []
        }
        
        for child in children:
            try:
                risk_assessment = RiskAssessmentCalculator.perform_risk_assessment(child)
                results['assessed_children'] += 1
                
                if risk_assessment.risk_level == 'heavy_risk':
                    results['heavy_risk'] += 1
                elif risk_assessment.risk_level == 'light_risk':
                    results['light_risk'] += 1
                elif risk_assessment.risk_level == 'both_risk':
                    results['both_risk'] += 1
                else:
                    results['no_risk'] += 1
                    
            except Exception as e:
                results['errors'].append(f"Error assessing child {child.id}: {str(e)}")
        
        return results