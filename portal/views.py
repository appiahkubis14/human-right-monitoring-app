from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import ChildInHouseholdTbl, districtStaffTbl, houseHoldTbl, staffTbl, districtTbl

from django.db import models

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.models import Group
import json
from .models import staffTbl





#######################################################################################################################################################




from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q, F, Case, When, IntegerField
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import (
    houseHoldTbl, ChildInHouseholdTbl, farmerTbl, districtTbl, regionTbl, societyTbl,
    childLightTaskTbl, childHeavyTaskTbl, childLightTask12MonthsTbl, childHeavyTask12MonthsTbl,
    RiskAssessment, HeavyTaskRisk, LightTaskRisk, PriorityLevel, DeadlineAssignment,
    Query, QueryStatus, QueryCategory, FlaggedIssue, Escalation
)

def child_labor_dashboard(request):
    # Date filters
    time_period = request.GET.get('timeFilter', '30')
    if time_period == 'custom':
        start_date = request.GET.get('startDate')
        end_date = request.GET.get('endDate')
        if start_date and end_date:
            start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
        else:
            time_period = '30'  # Fallback to 30 days if custom dates are invalid
            end_date = timezone.now()
            start_date = end_date - timedelta(days=int(time_period))
    else:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(time_period))
    
    # Region and Society filters
    region_filter = request.GET.get('regionFilter', '')
    society_filter = request.GET.get('societyFilter', '')
    
    # Apply filters to querysets
    filters = {'created_date__range': (start_date, end_date)}
    child_filters = {'houseHold__created_date__range': (start_date, end_date)}
    
    if region_filter:
        filters['farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey__region'] = region_filter
        child_filters['houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey__region'] = region_filter
    
    if society_filter:
        filters['farmer__society_name__society'] = society_filter
        child_filters['houseHold__farmer__society_name__society'] = society_filter
    
    # Basic counts
    children_monitored = ChildInHouseholdTbl.objects.filter(**child_filters).count()
    households_surveyed = houseHoldTbl.objects.filter(**filters).count()
    
    # School enrollment rate
    educated_children = ChildInHouseholdTbl.objects.filter(
        **child_filters, child_educated='1'
    ).count()
    school_enrollment_rate = round((educated_children / children_monitored * 100), 2) if children_monitored > 0 else 0
    
    # Risk cases
    risk_filters = {'assessment_date__range': (start_date, end_date)}
    if region_filter:
        risk_filters['child__houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey__region'] = region_filter
    if society_filter:
        risk_filters['child__houseHold__farmer__society_name__society'] = society_filter
    
    risk_cases = RiskAssessment.objects.filter(
        **risk_filters,
        risk_level__in=['heavy_risk', 'both_risk']
    ).count()
    
    # Interventions (using Query model as proxy)
    intervention_filters = {'created_date__range': (start_date, end_date)}
    if region_filter:
        intervention_filters['household__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey__region'] = region_filter
    if society_filter:
        intervention_filters['household__farmer__society_name__society'] = society_filter
    
    interventions = Query.objects.filter(
        **intervention_filters,
        category__name__icontains='intervention'
    ).count()
    
    # Birth certificate rate
    with_birth_cert = ChildInHouseholdTbl.objects.filter(
        **child_filters, child_birth_certificate='yes'
    ).count()
    birth_cert_rate = round((with_birth_cert / children_monitored * 100), 2) if children_monitored > 0 else 0
    
    # Light work engagement
    light_work_filters = {'created_date__range': (start_date, end_date)}
    if region_filter:
        light_work_filters['child__houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey__region'] = region_filter
    if society_filter:
        light_work_filters['child__houseHold__farmer__society_name__society'] = society_filter
    
    light_work = childLightTaskTbl.objects.filter(
        **light_work_filters
    ).values('child').distinct().count()
    light_work_rate = round((light_work / children_monitored * 100), 2) if children_monitored > 0 else 0
    
    # Heavy work engagement
    heavy_work_filters = {'created_date__range': (start_date, end_date)}
    if region_filter:
        heavy_work_filters['child__houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey__region'] = region_filter
    if society_filter:
        heavy_work_filters['child__houseHold__farmer__society_name__society'] = society_filter
    
    heavy_work = childHeavyTaskTbl.objects.filter(
        **heavy_work_filters
    ).values('child').distinct().count()
    heavy_work_rate = round((heavy_work / children_monitored * 100), 2) if children_monitored > 0 else 0
    
    # Agrochemical exposure
    agrochemical_exposure = childHeavyTaskTbl.objects.filter(
        **heavy_work_filters,
        agrochemicals_applied='yes'
    ).values('child').distinct().count()
    agrochemical_rate = round((agrochemical_exposure / children_monitored * 100), 2) if children_monitored > 0 else 0
    
    # Labor trends by region - FIXED
    monthly_trends = []
    regions = regionTbl.objects.all()
    
    for region in regions:
        region_data = {
            'name': region.region,
            'data': []
        }
        
        # Get data for each month
        current = start_date
        month_count = 0
        while current <= end_date:
            month_start = current.replace(day=1)
            if current.month == 12:
                month_end = current.replace(day=31)
            else:
                next_month = current.replace(month=current.month + 1, day=1)
                month_end = next_month - timedelta(days=1)
            
            # Apply region filter to monthly data
            month_filters = {
                'created_date__range': (month_start, month_end),
                'houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey': region
            }
            
            month_count = ChildInHouseholdTbl.objects.filter(**month_filters).count()
            region_data['data'].append(month_count)
            
            # Move to next month
            current = month_end + timedelta(days=1)
            if current > end_date:
                break
        
        monthly_trends.append(region_data)
    
    # Risk classification
    risk_classification = RiskAssessment.objects.filter(
        **risk_filters
    ).values('risk_level').annotate(count=Count('risk_level'))
    
    risk_data = {
        'no_risk': 0,
        'light_risk': 0,
        'heavy_risk': 0,
        'both_risk': 0
    }
    
    for item in risk_classification:
        risk_data[item['risk_level']] = item['count']
    
    # Work type distribution
    light_tasks = childLightTaskTbl.objects.filter(
        **light_work_filters
    ).values('task__name').annotate(count=Count('id'))
    
    heavy_tasks = childHeavyTaskTbl.objects.filter(
        **heavy_work_filters
    ).values('task__name').annotate(count=Count('id'))
    
    # Education status by age group
    age_groups = {
        '5-9': (5, 9),
        '10-12': (10, 12),
        '13-15': (13, 15),
        '16-17': (16, 17)
    }
    
    education_by_age = {}
    for group, (min_age, max_age) in age_groups.items():
        current_year = timezone.now().year
        min_birth_year = current_year - max_age
        max_birth_year = current_year - min_age
        
        total = ChildInHouseholdTbl.objects.filter(
            **child_filters,
            child_year_birth__gte=min_birth_year,
            child_year_birth__lte=max_birth_year
        ).count()
        
        enrolled = ChildInHouseholdTbl.objects.filter(
            **child_filters,
            child_year_birth__gte=min_birth_year,
            child_year_birth__lte=max_birth_year,
            child_educated='1'
        ).count()
        
        if total > 0:
            education_by_age[group] = {
                'enrolled': enrolled,
                'not_enrolled': total - enrolled,
                'rate': round((enrolled / total * 100), 2)
            }
        else:
            education_by_age[group] = {
                'enrolled': 0,
                'not_enrolled': 0,
                'rate': 0
            }
    
    # Recent monitoring activities
    recent_activities = houseHoldTbl.objects.filter(
        **filters
    ).select_related('farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey'
    ).order_by('-created_date')[:10]
    
    # Assessment status
    completed_surveys = households_surveyed
    
    # For pending review and requiring follow-up
    pending_review = Query.objects.filter(
        **intervention_filters,
        status__name='Open'
    ).count()
    
    requiring_follow_up = Query.objects.filter(
        **intervention_filters,
        requires_follow_up=True
    ).count()
    
    new_this_week = houseHoldTbl.objects.filter(
        created_date__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    # Regional distribution
    regional_distribution = {}
    total_households = households_surveyed
    
    for region in regions:
        region_count = houseHoldTbl.objects.filter(
            **filters,
            farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey=region
        ).count()
        
        if total_households > 0:
            percentage = round((region_count / total_households * 100), 2)
        else:
            percentage = 0
            
        regional_distribution[region.region] = percentage
    
    # Recent risk cases
    recent_risk_cases = RiskAssessment.objects.filter(
        **risk_filters,
        risk_level__in=['heavy_risk', 'both_risk']
    ).select_related('child__houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey'
    ).order_by('-assessment_date')[:6]
    
    # Upcoming interventions (using DeadlineAssignment as proxy)
    upcoming_interventions = DeadlineAssignment.objects.filter(
        end_date__gte=timezone.now(),
        status__in=['Pending', 'In Progress']
    ).order_by('end_date')[:3]
    
    # Child demographics
    child_demographics = ChildInHouseholdTbl.objects.filter(**child_filters).annotate(
        age=timezone.now().year - F('child_year_birth')
    ).values('age').annotate(count=Count('id')).order_by('age')
    
    # Education status
    education_status = ChildInHouseholdTbl.objects.filter(**child_filters).aggregate(
        enrolled=Count('id', filter=Q(child_educated='1')),
        not_enrolled=Count('id', filter=Q(child_educated='0')),
        dropout=Count('id', filter=Q(child_schl2='2')),
        never_attended=Count('id', filter=Q(child_schl2='0'))
    )
    
    # Work types analysis
    work_types = {
        'light_work': light_work,
        'heavy_work': heavy_work,
        'hazardous': childHeavyTaskTbl.objects.filter(
            **heavy_work_filters,
            task__name__in=['Spraying', 'Chemical Application']
        ).values('child').distinct().count(),
        'domestic': childLightTaskTbl.objects.filter(
            **light_work_filters,
            task__name__in=['Cleaning', 'Cooking', 'Childcare']
        ).values('child').distinct().count()
    }
    
    # Age distribution
    age_distribution = {}
    for age in range(5, 18):
        age_count = ChildInHouseholdTbl.objects.filter(
            **child_filters,
            child_year_birth=timezone.now().year - age
        ).count()
        age_distribution[age] = age_count
    
    # Gender distribution by region
    gender_region_data = {}
    for region in regions:
        male_count = ChildInHouseholdTbl.objects.filter(
            **child_filters,
            child_gender='Male',
            houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey=region
        ).count()
        
        female_count = ChildInHouseholdTbl.objects.filter(
            **child_filters,
            child_gender='Female',
            houseHold__farmer__society_name__districtTbl_foreignkey__regionTbl_foreignkey=region
        ).count()
        
        gender_region_data[region.region] = {
            'male': male_count,
            'female': female_count
        }
    
    # School attendance by age
    school_attendance = {}
    for group, (min_age, max_age) in age_groups.items():
        current_year = timezone.now().year
        min_birth_year = current_year - max_age
        max_birth_year = current_year - min_age
        
        enrolled_count = ChildInHouseholdTbl.objects.filter(
            **child_filters,
            child_year_birth__gte=min_birth_year,
            child_year_birth__lte=max_birth_year,
            child_educated='1'
        ).count()
        
        total_count = ChildInHouseholdTbl.objects.filter(
            **child_filters,
            child_year_birth__gte=min_birth_year,
            child_year_birth__lte=max_birth_year
        ).count()
        
        if total_count > 0:
            school_attendance[group] = round((enrolled_count / total_count * 100), 2)
        else:
            school_attendance[group] = 0
    
    # Literacy levels
    literacy_levels = ChildInHouseholdTbl.objects.filter(**child_filters).aggregate(
        basic=Count('id', filter=Q(reading_response='basic') | Q(writing_response='basic') | Q(calculation_response='basic')),
        intermediate=Count('id', filter=Q(reading_response='intermediate') | Q(writing_response='intermediate') | Q(calculation_response='intermediate')),
        advanced=Count('id', filter=Q(reading_response='advanced') | Q(writing_response='advanced') | Q(calculation_response='advanced')),
        illiterate=Count('id', filter=Q(reading_response='none') | Q(writing_response='none') | Q(calculation_response='none'))
    )
    
    # Work hours by age group
    work_hours_by_age = {}
    for group, (min_age, max_age) in age_groups.items():
        current_year = timezone.now().year
        min_birth_year = current_year - max_age
        max_birth_year = current_year - min_age
        
        # Calculate average work hours from light and heavy tasks
        light_hours = childLightTaskTbl.objects.filter(
            **light_work_filters,
            child__child_year_birth__gte=min_birth_year,
            child__child_year_birth__lte=max_birth_year
        ).aggregate(avg_hours=Avg(
            F('total_hours_light_work_school_12') + F('total_hours_light_work_non_school_12')
        ))['avg_hours'] or 0
        
        heavy_hours = childHeavyTaskTbl.objects.filter(
            **heavy_work_filters,
            child__child_year_birth__gte=min_birth_year,
            child__child_year_birth__lte=max_birth_year
        ).aggregate(avg_hours=Avg(
            F('total_hours_school_days') + F('total_hours_non_school_days')
        ))['avg_hours'] or 0
        
        work_hours_by_age[group] = round((light_hours + heavy_hours), 1)
    
    # Task types distribution
    task_types = {}
    light_task_types = childLightTaskTbl.objects.filter(**light_work_filters).values(
        'task__name'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    heavy_task_types = childHeavyTaskTbl.objects.filter(**heavy_work_filters).values(
        'task__name'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    for task in light_task_types:
        task_types[task['task__name']] = task['count']
    
    for task in heavy_task_types:
        if task['task__name'] in task_types:
            task_types[task['task__name']] += task['count']
        else:
            task_types[task['task__name']] = task['count']
    
    # Risk correlation (simplified - you would need to implement actual correlation calculations)
    risk_correlation = {
        'poverty': 75,
        'education': 85,
        'family_size': 65,
        'work_hours': 90,
        'region': 70
    }
    
    # Intervention effectiveness
    intervention_effectiveness = Query.objects.filter(
        **intervention_filters,
        category__name__icontains='intervention',
        status__name='Resolved'
    ).count()
    
    total_interventions = Query.objects.filter(
        **intervention_filters,
        category__name__icontains='intervention'
    ).count()
    
    if total_interventions > 0:
        effectiveness_rate = round((intervention_effectiveness / total_interventions * 100), 2)
    else:
        effectiveness_rate = 0
    
    # Child labor cases overview
    child_labor_cases = []
    for risk_case in recent_risk_cases:
        child = risk_case.child
        try:
            work_hours = (childLightTaskTbl.objects.filter(child=child).aggregate(
                total=Sum(F('total_hours_light_work_school_12') + F('total_hours_light_work_non_school_12'))
            )['total'] or 0) + (childHeavyTaskTbl.objects.filter(child=child).aggregate(
                total=Sum(F('total_hours_school_days') + F('total_hours_non_school_days'))
            )['total'] or 0)
        except:
            work_hours = 0
        
        child_labor_cases.append({
            'case_id': f"CL-{risk_case.assessment_date.strftime('%Y-%m-%d')}-{child.id}",
            'child_name': f"{child.child_first_name} {child.child_surname}",
            'age': timezone.now().year - child.child_year_birth,
            'region': child.houseHold.farmer.society_name.districtTbl_foreignkey.regionTbl_foreignkey.region,
            'risk_level': risk_case.get_risk_level_display(),
            'school_status': 'Enrolled' if child.child_educated == '1' else 'Not Enrolled',
            'work_hours': round(work_hours, 1),
            'last_assessment': risk_case.assessment_date.strftime('%Y-%m-%d')
        })
    
    # Get societies for the selected region
    societies = []
    if region_filter:
        societies = societyTbl.objects.filter(
            districtTbl_foreignkey__regionTbl_foreignkey__region=region_filter
        ).values_list('society', flat=True).distinct()
    else:
        societies = societyTbl.objects.all().values_list('society', flat=True).distinct()

    #Get Districts by region
    districts = []
    if region_filter:
        districts = districtTbl.objects.filter(
            regionTbl_foreignkey__region=region_filter
        ).values_list('district', flat=True).distinct()
    else:
        districts = districtTbl.objects.all().values_list('district', flat=True).distinct()

    print(school_attendance)

    
    # Prepare context
    context = {
        # Summary cards
        'children_monitored': children_monitored,
        'school_enrollment_rate': school_enrollment_rate,
        'risk_cases': risk_cases,
        'interventions': interventions,
        
        # Detailed metrics
        'birth_cert_rate': birth_cert_rate,
        'light_work_rate': light_work_rate,
        'heavy_work_rate': heavy_work_rate,
        'agrochemical_rate': agrochemical_rate,
        
        # Charts data
        'monthly_trends': monthly_trends,
        'risk_data': risk_data,
        'light_tasks': list(light_tasks),
        'heavy_tasks': list(heavy_tasks),
        'education_by_age': education_by_age,
        
        # Recent activities
        'recent_activities': recent_activities,
        
        # Assessment status
        'completed_surveys': completed_surveys,
        'pending_review': pending_review,
        'requiring_follow_up': requiring_follow_up,
        'new_this_week': new_this_week,
        
        # Regional distribution
        'regional_distribution': regional_distribution,
        'regions': regions,
        'districts': districts,
        'societies': societies,
        
        # Risk cases
        'recent_risk_cases': recent_risk_cases,
        
        # Upcoming interventions
        'upcoming_interventions': upcoming_interventions,
        
        # Child demographics
        'child_demographics': list(child_demographics),
        
        # Education status
        'education_status': education_status,
        
        # Work types analysis
        'work_types': work_types,
        
        # Age distribution
        'age_distribution': age_distribution,
        
        # Gender distribution by region
        'gender_region_data': gender_region_data,
        
        # School attendance by age
        'school_attendance': school_attendance,
        
        # Literacy levels
        'literacy_levels': literacy_levels,
        
        # Work hours by age group
        'work_hours_by_age': work_hours_by_age,
        
        # Task types distribution
        'task_types': task_types,
        
        # Risk correlation
        'risk_correlation': risk_correlation,
        
        # Intervention effectiveness
        'effectiveness_rate': effectiveness_rate,
        
        # Child labor cases overview
        'child_labor_cases': child_labor_cases,
        
        # Filters
        'selected_region': region_filter,
        'selected_society': society_filter,
        'selected_period': time_period,
        'start_date': start_date.strftime('%Y-%m-%d') if hasattr(start_date, 'strftime') else start_date,
        'end_date': end_date.strftime('%Y-%m-%d') if hasattr(end_date, 'strftime') else end_date,
    }

    # print(context)

    return render(request, 'core/index.html', context)



###################################################################################################################################################

@method_decorator(login_required, name='dispatch')
class StaffManagementView(View):
    def get(self, request):
        return render(request, 'core/staff_management.html')

@login_required
def get_staff_data(request):
    try:
        # Get all staff members
        staff_members = staffTbl.objects.all()
        
        data = []
        for staff in staff_members:
            data.append({
                'id': staff.id,
                'staffid': staff.staffid,
                'first_name': staff.first_name,
                'last_name': staff.last_name,
                'gender': staff.gender,
                'contact': staff.contact,
                'email_address': staff.email_address,
                'designation': staff.designation.name if staff.designation else '',
                'designation_id': staff.designation.id if staff.designation else None,
                'district': staff.district,
                'status': 'Active' if staff.delete_field == 'no' else 'Inactive'
            })
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading staff data: {str(e)}'})

@login_required
def get_staff_details(request):
    try:
        staff_id = request.GET.get('staff_id')
        if not staff_id:
            return JsonResponse({'success': False, 'message': 'Staff ID is required'})
        
        staff = get_object_or_404(staffTbl, id=staff_id)
        
        data = {
            'id': staff.id,
            'staffid': staff.staffid,
            'first_name': staff.first_name,
            'last_name': staff.last_name,
            'gender': staff.gender,
            'contact': staff.contact,
            'email_address': staff.email_address,
            'designation_id': staff.designation.id if staff.designation else None,
            'district': staff.district,
            'status': 'Active' if staff.delete_field == 'no' else 'Inactive'
        }
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading staff details: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_staff(request):
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'gender', 'contact', 'designation']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'})
        
        # Check if designation exists
        try:
            designation = Group.objects.get(id=data['designation'])
        except Group.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Designation not found'})
        
        # Check if email already exists (if provided)
        if data.get('email_address'):
            if staffTbl.objects.filter(email_address=data['email_address'], delete_field='no').exists():
                return JsonResponse({'success': False, 'message': 'Email address already exists'})
        
        # Create new staff member
        staff = staffTbl(
            first_name=data['first_name'],
            last_name=data['last_name'],
            gender=data['gender'],
            contact=data['contact'],
            email_address=data.get('email_address', ''),
            designation=designation,
            district=data.get('district', '')
        )
        staff.save()
        
        return JsonResponse({'success': True, 'message': 'Staff member created successfully', 'staff_id': staff.id})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating staff member: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_staff(request, staff_id):
    try:
        staff = get_object_or_404(staffTbl, id=staff_id)
        data = json.loads(request.body)
        
        # Update basic fields
        if 'first_name' in data:
            staff.first_name = data['first_name']
        if 'last_name' in data:
            staff.last_name = data['last_name']
        if 'gender' in data:
            staff.gender = data['gender']
        if 'contact' in data:
            staff.contact = data['contact']
        if 'email_address' in data:
            # Check if email already exists (excluding current staff)
            if staffTbl.objects.filter(email_address=data['email_address'], delete_field='no').exclude(id=staff_id).exists():
                return JsonResponse({'success': False, 'message': 'Email address already exists'})
            staff.email_address = data['email_address']
        if 'district' in data:
            staff.district = data['district']
        
        # Update designation if provided
        if 'designation' in data and data['designation']:
            try:
                designation = Group.objects.get(id=data['designation'])
                staff.designation = designation
            except Group.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Designation not found'})
        
        # Update status if provided
        if 'status' in data:
            staff.delete_field = 'yes' if data['status'] == 'Inactive' else 'no'
        
        staff.save()
        
        return JsonResponse({'success': True, 'message': 'Staff member updated successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating staff member: {str(e)}'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_staff(request, staff_id):
    try:
        staff = get_object_or_404(staffTbl, id=staff_id)
        staff.delete_field = 'yes'  # Soft delete
        staff.save()
        return JsonResponse({'success': True, 'message': 'Staff member deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting staff member: {str(e)}'})

@login_required
def get_designation_options(request):
    try:
        designations = Group.objects.all()
        options = [{'id': designation.id, 'name': designation.name} for designation in designations]
        return JsonResponse(options, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)




########################################################################################################################################################################


@method_decorator(login_required, name='dispatch')
class AssignmentsOverviewView(View):
    def get(self, request):
        return render(request, 'core/enumerator_assgnment.html')

@login_required
def get_assignments_data(request):
    try:
        # Get all district staff assignments
        assignments = districtStaffTbl.objects.select_related(
            'staffTbl_foreignkey', 'districtTbl_foreignkey', 'districtTbl_foreignkey__regionTbl_foreignkey'
        ).all()
        
        data = []
        for assignment in assignments:
            data.append({
                'id': assignment.id,
                'staff_name': f"{assignment.staffTbl_foreignkey.first_name} {assignment.staffTbl_foreignkey.last_name}",
                'staff_id': assignment.staffTbl_foreignkey.staffid,
                'district': assignment.districtTbl_foreignkey.district,
                'district_id': assignment.districtTbl_foreignkey.id,
                'region': assignment.districtTbl_foreignkey.regionTbl_foreignkey.region if assignment.districtTbl_foreignkey.regionTbl_foreignkey else '',
                'created_date': assignment.created_date.strftime('%Y-%m-%d %H:%M:%S') if assignment.created_date else '',
                'status': 'Active' if assignment.delete_field == 'no' else 'Inactive'
            })

            print(data)
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading assignments: {str(e)}'})

@login_required
def get_assignment_details(request):
    try:
        assignment_id = request.GET.get('assignment_id')
        if not assignment_id:
            return JsonResponse({'success': False, 'message': 'Assignment ID is required'})
        
        assignment = get_object_or_404(districtStaffTbl, id=assignment_id)
        
        data = {
            'id': assignment.id,
            'staff_id': assignment.staffTbl_foreignkey.id,
            'district_id': assignment.districtTbl_foreignkey.id,
            'status': 'Active' if assignment.delete_field == 'no' else 'Inactive'
        }
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading assignment details: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_assignment(request):
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['staff_id', 'district_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'})
        
        # Check if staff exists
        try:
            staff = staffTbl.objects.get(id=data['staff_id'])
        except staffTbl.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Staff member not found'})
        
        # Check if district exists
        try:
            district = districtTbl.objects.get(id=data['district_id'])
        except districtTbl.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'District not found'})
        
        # Check if assignment already exists
        if districtStaffTbl.objects.filter(
            staffTbl_foreignkey=staff, 
            districtTbl_foreignkey=district,
            delete_field='no'
        ).exists():
            return JsonResponse({'success': False, 'message': 'Assignment already exists for this staff and district'})
        
        # Create new assignment
        assignment = districtStaffTbl(
            staffTbl_foreignkey=staff,
            districtTbl_foreignkey=district
        )
        assignment.save()
        
        return JsonResponse({'success': True, 'message': 'Assignment created successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating assignment: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_assignment(request, assignment_id):
    try:
        assignment = get_object_or_404(districtStaffTbl, id=assignment_id)
        data = json.loads(request.body)
        
        # Update district if provided
        if 'district_id' in data and data['district_id']:
            try:
                district = districtTbl.objects.get(id=data['district_id'])
                assignment.districtTbl_foreignkey = district
            except districtTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'District not found'})
        
        # Update status if provided
        if 'status' in data:
            assignment.delete_field = 'yes' if data['status'] == 'Inactive' else 'no'
        
        assignment.save()
        
        return JsonResponse({'success': True, 'message': 'Assignment updated successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating assignment: {str(e)}'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_assignment(request, assignment_id):
    try:
        assignment = get_object_or_404(districtStaffTbl, id=assignment_id)
        assignment.delete_field = 'yes'  # Soft delete
        assignment.save()
        return JsonResponse({'success': True, 'message': 'Assignment deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting assignment: {str(e)}'})

@login_required
def get_staff_options(request):
    try:
        staff_members = staffTbl.objects.filter(delete_field='no')
        options = [{'id': staff.id, 'text': f"{staff.first_name} {staff.last_name} ({staff.staffid})"} for staff in staff_members]
        return JsonResponse(options, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)

@login_required
def get_district_options(request):
    try:
        districts = districtTbl.objects.filter(delete_field='no').select_related('regionTbl_foreignkey')
        options = [{'id': district.id, 'text': f"{district.district} ({district.regionTbl_foreignkey.region if district.regionTbl_foreignkey else 'No Region'})"} for district in districts]
        return JsonResponse(options, safe=False)
    except Exception as e:
        return JsonResponse([], safe=False)
    



###########################################################################################################################################################################################################


# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import json
from .models import DeadlineAssignment, PriorityLevel, DeadlineType, staffTbl

@method_decorator(login_required, name='dispatch')
class DeadlinesView(View):
    def get(self, request):
        return render(request, 'core/deadlines_priorities.html')

@login_required
def get_deadlines_data(request):
    try:
        # Get all deadline assignments
        deadlines = DeadlineAssignment.objects.select_related(
            'assigned_to', 'assigned_by', 'deadline_type', 'priority_level'
        ).all()
        
        data = []
        for deadline in deadlines:
            data.append({
                'id': deadline.id,
                'title': deadline.title,  # Ensure this field exists in your model
                'description': deadline.description,
                'deadline_type': deadline.deadline_type.name,
                'deadline_type_id': deadline.deadline_type.id,
                'priority_level': deadline.priority_level.name,
                'priority_level_id': deadline.priority_level.id,
                'priority_color': deadline.priority_level.color,
                'assigned_to': f"{deadline.assigned_to.first_name} {deadline.assigned_to.last_name}",
                'assigned_to_id': deadline.assigned_to.id,
                'assigned_by': f"{deadline.assigned_by.first_name} {deadline.assigned_by.last_name}",
                'staff_type': deadline.staff_type,
                'start_date': deadline.start_date.strftime('%Y-%m-%d %H:%M:%S') if deadline.start_date else None,
                'end_date': deadline.end_date.strftime('%Y-%m-%d %H:%M:%S') if deadline.end_date else None,
                'status': deadline.status,
                'completion_date': deadline.completion_date.strftime('%Y-%m-%d %H:%M:%S') if deadline.completion_date else None,
                'notes': deadline.notes,
                'is_recurring': deadline.is_recurring,
                'recurrence_pattern': deadline.recurrence_pattern,
                'days_remaining': deadline.days_remaining,
                'is_overdue': deadline.is_overdue
            })

            print(data)
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading deadlines: {str(e)}'})
@login_required
def get_deadline_details(request):
    try:
        deadline_id = request.GET.get('deadline_id')
        if not deadline_id:
            return JsonResponse({'success': False, 'message': 'Deadline ID is required'})
        
        deadline = get_object_or_404(DeadlineAssignment, id=deadline_id)
        
        data = {
            'id': deadline.id,
            'title': deadline.title,
            'description': deadline.description,
            'deadline_type_id': deadline.deadline_type.id,
            'priority_level_id': deadline.priority_level.id,
            'assigned_to_id': deadline.assigned_to.id,
            'staff_type': deadline.staff_type,
            'start_date': deadline.start_date.strftime('%Y-%m-%dT%H:%M'),
            'end_date': deadline.end_date.strftime('%Y-%m-%dT%H:%M'),
            'status': deadline.status,
            'completion_date': deadline.completion_date.strftime('%Y-%m-%dT%H:%M') if deadline.completion_date else None,
            'notes': deadline.notes,
            'is_recurring': deadline.is_recurring,
            'recurrence_pattern': deadline.recurrence_pattern
        }
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading deadline details: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_deadline(request):
    try:
        data = json.loads(request.body)
        print(data)
        
        # Validate required fields
        required_fields = ['title', 'deadline_type_id', 'priority_level_id', 'assigned_to_id', 'start_date', 'end_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'})
        
        # Get current user's staff record
        current_user = request.user
        try:
            assigned_by = staffTbl.objects.get(user=current_user)
        except staffTbl.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Current user does not have a staff record'})
        
        # Validate foreign keys
        try:
            deadline_type = DeadlineType.objects.get(id=data['deadline_type_id'])
            priority_level = PriorityLevel.objects.get(id=data['priority_level_id'])
            assigned_to = staffTbl.objects.get(id=data['assigned_to_id'])
        except (DeadlineType.DoesNotExist, PriorityLevel.DoesNotExist, staffTbl.DoesNotExist) as e:
            return JsonResponse({'success': False, 'message': 'Invalid reference data'})
        
        # Create new deadline
        deadline = DeadlineAssignment(
            title=data['title'],
            description=data.get('description', ''),
            deadline_type=deadline_type,
            priority_level=priority_level,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
            staff_type=data.get('staff_type', 'Staff'),
            start_date=timezone.make_aware(timezone.datetime.fromisoformat(data['start_date'].replace('Z', ''))),
            end_date=timezone.make_aware(timezone.datetime.fromisoformat(data['end_date'].replace('Z', ''))),
            notes=data.get('notes', ''),
            is_recurring=data.get('is_recurring', False),
            recurrence_pattern=data.get('recurrence_pattern', '')
        )
        deadline.save()
        
        return JsonResponse({'success': True, 'message': 'Deadline created successfully', 'deadline_id': deadline.id})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating deadline: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_deadline(request, deadline_id):
    try:
        deadline = get_object_or_404(DeadlineAssignment, id=deadline_id)
        data = json.loads(request.body)
        print(data)
        
        # Update basic fields
        if 'title' in data:
            deadline.title = data['title']
        if 'description' in data:
            deadline.description = data['description']
        if 'notes' in data:
            deadline.notes = data['notes']
        if 'staff_type' in data:
            deadline.staff_type = data['staff_type']
        if 'is_recurring' in data:
            deadline.is_recurring = data['is_recurring']
        if 'recurrence_pattern' in data:
            deadline.recurrence_pattern = data['recurrence_pattern']
        
        # Update foreign keys
        if 'deadline_type_id' in data and data['deadline_type_id']:
            try:
                deadline_type = DeadlineType.objects.get(id=data['deadline_type_id'])
                deadline.deadline_type = deadline_type
            except DeadlineType.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Deadline type not found'})
        
        if 'priority_level_id' in data and data['priority_level_id']:
            try:
                priority_level = PriorityLevel.objects.get(id=data['priority_level_id'])
                deadline.priority_level = priority_level
            except PriorityLevel.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Priority level not found'})
        
        if 'assigned_to_id' in data and data['assigned_to_id']:
            try:
                assigned_to = staffTbl.objects.get(id=data['assigned_to_id'])
                deadline.assigned_to = assigned_to
            except staffTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Assigned staff not found'})
        
        # Update dates
        if 'start_date' in data and data['start_date']:
            deadline.start_date = timezone.make_aware(timezone.datetime.fromisoformat(data['start_date'].replace('Z', '')))
        
        if 'end_date' in data and data['end_date']:
            deadline.end_date = timezone.make_aware(timezone.datetime.fromisoformat(data['end_date'].replace('Z', '')))
        
        # Update status
        if 'status_select' in data:
            deadline.status = data['status_select']
            if data['status_select'] == 'Completed' and not deadline.completion_date:
                deadline.completion_date = timezone.now()
            elif data['status_select'] != 'Completed':
                deadline.completion_date = None
        
        deadline.save()
        
        return JsonResponse({'success': True, 'message': 'Deadline updated successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating deadline: {str(e)}'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_deadline(request, deadline_id):
    try:
        deadline = get_object_or_404(DeadlineAssignment, id=deadline_id)
        deadline.delete()  # Soft delete
        return JsonResponse({'success': True, 'message': 'Deadline deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting deadline: {str(e)}'})

@login_required
def get_options_data(request):
    try:
        # Get priority levels
        priorities = PriorityLevel.objects.all()
        priority_options = [{'id': p.id, 'name': p.name, 'color': p.color} for p in priorities]
        
        # Get deadline types
        types = DeadlineType.objects.all()
        type_options = [{'id': t.id, 'name': t.name} for t in types]
        
        # Get staff options
        staff_members = staffTbl.objects.filter(delete_field='no')
        staff_options = [{'id': s.id, 'name': f"{s.first_name} {s.last_name} ({s.staffid})"} for s in staff_members]
        
        return JsonResponse({
            'success': True,
            'priorities': priority_options,
            'types': type_options,
            'staff': staff_options
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading options: {str(e)}'})
    

######################################################################################################################################

# views.py - Add these farmer views
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import json
from .models import farmerTbl, societyTbl, staffTbl

@method_decorator(login_required, name='dispatch')
class FarmersView(View):
    def get(self, request):
        return render(request, 'core/farmer-list.html')
    


@login_required
def get_farmers_data(request):
    try:
        # Get all farmers with related data
        farmers = farmerTbl.objects.select_related(
            'society_name', 'staffTbl_foreignkey'
        ).all()
        
        data = []
        for farmer in farmers:
            data.append({
                'id': farmer.id,
                'first_name': farmer.first_name,
                'last_name': farmer.last_name,
                'full_name': f"{farmer.first_name} {farmer.last_name}",
                'farmer_code': farmer.farmer_code,
                'society_name': farmer.society_name.society if farmer.society_name else 'N/A',
                'society_id': farmer.society_name.id if farmer.society_name else None,
                'national_id_no': farmer.national_id_no,
                'contact': farmer.contact,
                'id_type': farmer.id_type,
                'id_expiry_date': farmer.id_expiry_date,
                'no_of_cocoa_farms': farmer.no_of_cocoa_farms,
                'no_of_certified_crop': farmer.no_of_certified_crop,
                'total_cocoa_bags_harvested_previous_year': farmer.total_cocoa_bags_harvested_previous_year,
                'total_cocoa_bags_sold_group_previous_year': farmer.total_cocoa_bags_sold_group_previous_year,
                'current_year_yeild_estimate': farmer.current_year_yeild_estimate,
                'staff_name': f"{farmer.staffTbl_foreignkey.first_name} {farmer.staffTbl_foreignkey.last_name}" if farmer.staffTbl_foreignkey else 'N/A',
                'staff_id': farmer.staffTbl_foreignkey.id if farmer.staffTbl_foreignkey else None,
                'uuid': farmer.uuid,
                'mapped_status': farmer.mapped_status,
                'new_farmer_code': farmer.new_farmer_code,
                'created_date': farmer.created_date.strftime('%Y-%m-%d %H:%M:%S') if farmer.created_date else None,
                'updated_at': farmer.updated_at.strftime('%Y-%m-%d %H:%M:%S') if farmer.updated_at else None,
                'status': 'Active' if farmer.delete_field == 'no' else 'Inactive'
            })
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading farmers: {str(e)}'})

@login_required
def get_farmer_details(request):
    try:
        farmer_id = request.GET.get('farmer_id')
        if not farmer_id:
            return JsonResponse({'success': False, 'message': 'Farmer ID is required'})
        
        farmer = get_object_or_404(farmerTbl, id=farmer_id)
        
        data = {
            'id': farmer.id,
            'first_name': farmer.first_name,
            'last_name': farmer.last_name,
            'farmer_code': farmer.farmer_code,
            'society_name_id': farmer.society_name.id if farmer.society_name else None,
            'national_id_no': farmer.national_id_no,
            'contact': farmer.contact,
            'id_type': farmer.id_type,
            'id_expiry_date': farmer.id_expiry_date,
            'no_of_cocoa_farms': farmer.no_of_cocoa_farms,
            'no_of_certified_crop': farmer.no_of_certified_crop,
            'total_cocoa_bags_harvested_previous_year': farmer.total_cocoa_bags_harvested_previous_year,
            'total_cocoa_bags_sold_group_previous_year': farmer.total_cocoa_bags_sold_group_previous_year,
            'current_year_yeild_estimate': farmer.current_year_yeild_estimate,
            'staffTbl_foreignkey_id': farmer.staffTbl_foreignkey.id if farmer.staffTbl_foreignkey else None,
            'uuid': farmer.uuid,
            'mapped_status': farmer.mapped_status,
            'new_farmer_code': farmer.new_farmer_code,
            'status': 'Active' if farmer.delete_field == 'no' else 'Inactive'
        }
        print(data)
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading farmer details: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_farmer(request):
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'contact']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'})
        
        # Validate society if provided
        society = None
        if data.get('society_name_id'):
            try:
                society = societyTbl.objects.get(id=data['society_name_id'])
            except societyTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Society not found'})
        
        # Validate staff if provided
        staff = None
        if data.get('staffTbl_foreignkey_id'):
            try:
                staff = staffTbl.objects.get(id=data['staffTbl_foreignkey_id'])
            except staffTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Staff member not found'})
        
        # Check if farmer code already exists
        if data.get('farmer_code'):
            if farmerTbl.objects.filter(farmer_code=data['farmer_code'], delete_field='no').exists():
                return JsonResponse({'success': False, 'message': 'Farmer code already exists'})
        
        # Create new farmer
        farmer = farmerTbl(
            first_name=data['first_name'],
            last_name=data['last_name'],
            farmer_code=data.get('farmer_code'),
            society_name=society,
            national_id_no=data.get('national_id_no'),
            contact=data['contact'],
            id_type=data.get('id_type'),
            id_expiry_date=data.get('id_expiry_date'),
            no_of_cocoa_farms=data.get('no_of_cocoa_farms'),
            no_of_certified_crop=data.get('no_of_certified_crop'),
            total_cocoa_bags_harvested_previous_year=data.get('total_cocoa_bags_harvested_previous_year'),
            total_cocoa_bags_sold_group_previous_year=data.get('total_cocoa_bags_sold_group_previous_year'),
            current_year_yeild_estimate=data.get('current_year_yeild_estimate'),
            staffTbl_foreignkey=staff,
            uuid=data.get('uuid'),
            mapped_status=data.get('mapped_status', 'No'),
            new_farmer_code=data.get('new_farmer_code')
        )
        farmer.save()
        
        return JsonResponse({'success': True, 'message': 'Farmer created successfully', 'farmer_id': farmer.id})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating farmer: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_farmer(request, farmer_id):
    try:
        farmer = get_object_or_404(farmerTbl, id=farmer_id)
        data = json.loads(request.body)
        
        # Update basic fields
        if 'first_name' in data:
            farmer.first_name = data['first_name']
        if 'last_name' in data:
            farmer.last_name = data['last_name']
        if 'contact' in data:
            farmer.contact = data['contact']
        if 'national_id_no' in data:
            farmer.national_id_no = data['national_id_no']
        if 'id_type' in data:
            farmer.id_type = data['id_type']
        if 'id_expiry_date' in data:
            farmer.id_expiry_date = data['id_expiry_date']
        if 'farmer_code' in data:
            # Check if farmer code already exists (excluding current farmer)
            if farmerTbl.objects.filter(farmer_code=data['farmer_code'], delete_field='no').exclude(id=farmer_id).exists():
                return JsonResponse({'success': False, 'message': 'Farmer code already exists'})
            farmer.farmer_code = data['farmer_code']
        if 'uuid' in data:
            farmer.uuid = data['uuid']
        if 'mapped_status' in data:
            farmer.mapped_status = data['mapped_status']
        if 'new_farmer_code' in data:
            farmer.new_farmer_code = data['new_farmer_code']
        
        # Update numeric fields
        numeric_fields = [
            'no_of_cocoa_farms', 'no_of_certified_crop', 
            'total_cocoa_bags_harvested_previous_year',
            'total_cocoa_bags_sold_group_previous_year',
            'current_year_yeild_estimate'
        ]
        
        for field in numeric_fields:
            if field in data:
                setattr(farmer, field, data[field])
        
        # Update foreign keys
        if 'society_name_id' in data:
            if data['society_name_id']:
                try:
                    society = societyTbl.objects.get(id=data['society_name_id'])
                    farmer.society_name = society
                except societyTbl.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Society not found'})
            else:
                farmer.society_name = None
        
        if 'staffTbl_foreignkey_id' in data:
            if data['staffTbl_foreignkey_id']:
                try:
                    staff = staffTbl.objects.get(id=data['staffTbl_foreignkey_id'])
                    farmer.staffTbl_foreignkey = staff
                except staffTbl.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Staff member not found'})
            else:
                farmer.staffTbl_foreignkey = None
        
        # Update status
        if 'status' in data:
            farmer.delete_field = 'yes' if data['status'] == 'Inactive' else 'no'
        
        farmer.save()
        
        return JsonResponse({'success': True, 'message': 'Farmer updated successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating farmer: {str(e)}'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_farmer(request, farmer_id):
    try:
        farmer = get_object_or_404(farmerTbl, id=farmer_id)
        farmer.delete()  # Soft delete
        return JsonResponse({'success': True, 'message': 'Farmer deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting farmer: {str(e)}'})

@login_required
def get_farmer_options_data(request):
    try:
        # Get society options
        societies = societyTbl.objects.filter(delete_field='no')
        society_options = [{'id': s.id, 'name': s.society} for s in societies]
        
        # Get staff options
        staff_members = staffTbl.objects.filter(delete_field='no')
        staff_options = [{'id': s.id, 'name': f"{s.first_name} {s.last_name} ({s.staffid})"} for s in staff_members]
        
        return JsonResponse({
            'success': True,
            'societies': society_options,
            'staff': staff_options
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading options: {str(e)}'})
    
###############################################################################################################################

# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import regionTbl, districtTbl, societyTbl

def societies_list(request):
    return render(request, 'core/societies_list.html')

@csrf_exempt
def get_societies_data(request):
    try:
        societies = societyTbl.objects.select_related('districtTbl_foreignkey').all()
        
        data = []
        for society in societies:
            data.append({
                'id': society.id,
                'society': society.society,
                'society_code': society.society_code,
                'society_pre_code': society.society_pre_code,
                'new_society_pre_code': society.new_society_pre_code,
                'district': society.districtTbl_foreignkey.district if society.districtTbl_foreignkey else 'N/A',
                'region': society.districtTbl_foreignkey.regionTbl_foreignkey.region if society.districtTbl_foreignkey and society.districtTbl_foreignkey.regionTbl_foreignkey else 'N/A',
                'created_date': society.created_date.strftime('%Y-%m-%d %H:%M:%S') if society.created_date else 'N/A',
            })
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error loading societies: {str(e)}'
        })

@csrf_exempt
def get_society_options(request):
    try:
        regions = regionTbl.objects.all()
        districts = districtTbl.objects.all()
        
        regions_data = [{'id': region.id, 'name': region.region} for region in regions]
        districts_data = [{'id': district.id, 'name': district.district, 'region_id': district.regionTbl_foreignkey_id} for district in districts]
        
        return JsonResponse({
            'success': True,
            'regions': regions_data,
            'districts': districts_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error loading options: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def create_society(request):
    try:
        data = json.loads(request.body)
        
        society = societyTbl.objects.create(
            districtTbl_foreignkey_id=data.get('district_id'),
            society=data.get('society'),
            society_code=data.get('society_code'),
            society_pre_code=data.get('society_pre_code'),
            new_society_pre_code=data.get('new_society_pre_code')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Society created successfully',
            'id': society.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating society: {str(e)}'
        })

@csrf_exempt
def get_society_details(request):
    try:
        society_id = request.GET.get('society_id')
        society = get_object_or_404(societyTbl, id=society_id)
        
        data = {
            'id': society.id,
            'society': society.society,
            'society_code': society.society_code,
            'society_pre_code': society.society_pre_code,
            'new_society_pre_code': society.new_society_pre_code,
            'district_id': society.districtTbl_foreignkey_id,
            'region_id': society.districtTbl_foreignkey.regionTbl_foreignkey_id if society.districtTbl_foreignkey else None
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error loading society details: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["POST"])
def update_society(request, society_id):
    try:
        data = json.loads(request.body)
        society = get_object_or_404(societyTbl, id=society_id)
        
        society.districtTbl_foreignkey_id = data.get('district_id')
        society.society = data.get('society')
        society.society_code = data.get('society_code')
        society.society_pre_code = data.get('society_pre_code')
        society.new_society_pre_code = data.get('new_society_pre_code')
        society.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Society updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating society: {str(e)}'
        })

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_society(request, society_id):
    try:
        society = get_object_or_404(societyTbl, id=society_id)
        society.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Society deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting society: {str(e)}'
        })
    

####################################################################################
# queries/views.py
import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Query, QueryResponse, FlaggedIssue, Escalation, QueryCategory, QueryPriority, QueryStatus

@login_required
def send_query(request):
    """Send Query to Enumerator page"""
    return render(request, 'core/send_query.html')

@login_required
def review_responses(request):
    """Review Enumerator Responses page"""
    return render(request, 'core/review_responses.html')

@login_required
def flag_issues(request):
    """Flag Issues for Review page"""
    return render(request, 'core/flag_issues.html')

@login_required
def escalate_cases(request):
    """Escalate Cases to Supervisors page"""
    return render(request, 'core/escalate_cases.html')

# API Views
@login_required
@require_http_methods(["GET"])
def query_list_api(request):
    """Get list of queries with filtering and pagination"""
    try:
        # Get query parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        category_filter = request.GET.get('category', '')
        assigned_to_filter = request.GET.get('assigned_to', '')
        page = int(request.GET.get('page', 1))
        per_page = int(request.GET.get('per_page', 10))
        
        # Build filter conditions
        filters = Q()
        if status_filter:
            filters &= Q(status__name=status_filter)
        if priority_filter:
            filters &= Q(priority__name=priority_filter)
        if category_filter:
            filters &= Q(category__name=category_filter)
        if assigned_to_filter:
            filters &= Q(assigned_to__id=assigned_to_filter)
        
        # Get queries
        queries = Query.objects.filter(filters).select_related(
            'category', 'priority', 'status', 'assigned_to', 'created_by'
        ).order_by('-created_date')
        
        # Paginate
        paginator = Paginator(queries, per_page)
        page_obj = paginator.get_page(page)
        
        # Prepare response data
        queries_data = []
        for query in page_obj:
            queries_data.append({
                'id': query.id,
                'query_id': query.query_id,
                'title': query.title,
                'description': query.description,
                'category': query.category.name,
                'priority': query.priority.name,
                'priority_color': query.priority.color,
                'status': query.status.name,
                'status_color': query.status.color,
                'assigned_to': f"{query.assigned_to.first_name} {query.assigned_to.last_name}",
                "enumerator_id": query.assigned_to.staffid,
                'assigned_to_id': query.assigned_to.id,
                'created_by': f"{query.created_by.first_name} {query.created_by.last_name}",
                'created_date': query.created_date.strftime('%Y-%m-%d %H:%M'),
                'due_date': query.due_date.strftime('%Y-%m-%d %H:%M') if query.due_date else None,
                'is_overdue': query.is_overdue,
                'requires_follow_up': query.requires_follow_up,
                'is_escalated': query.is_escalated,
                'response_count': query.responses.count(),
                'flag_count': query.flags.count(),
            })
        
        return JsonResponse({
            'success': True,
            'data': queries_data,
            'pagination': {
                'total': paginator.count,
                'pages': paginator.num_pages,
                'current': page,
                'per_page': per_page,
                'has_next': page_obj.has_next(),
                'has_prev': page_obj.has_previous(),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching queries: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def create_query_api(request):
    """Create a new query"""
    try:
        data = json.loads(request.body)
        
        # Get current user (staff member)
        current_user = staffTbl.objects.get(user=request.user)
        
        # Create query
        query = Query.objects.create(
            title=data['title'],
            description=data['description'],
            category_id=data['category_id'],
            priority_id=data['priority_id'],
            status=QueryStatus.objects.get(name='Open'),
            assigned_to_id=data['assigned_to_id'],
            created_by=current_user,
            due_date=data.get('due_date'),
            requires_follow_up=data.get('requires_follow_up', False),
            household_id=data.get('household_id'),
            farmer_id=data.get('farmer_id'),
            child_id=data.get('child_id'),
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Query created successfully',
            'query_id': query.query_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating query: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def query_detail_api(request, query_id):
    """Get detailed information about a specific query"""
    try:
        query = get_object_or_404(Query, id=query_id)
        
        # Get responses
        responses = []
        for response in query.responses.select_related('responded_by').all():
            responses.append({
                'id': response.id,
                'response_text': response.response_text,
                'responded_by': f"{response.responded_by.first_name} {response.responded_by.last_name}",
                'responded_date': response.created_date.strftime('%Y-%m-%d %H:%M'),
                'attachment': response.attachment.url if response.attachment else None,
            })
        
        # Get flags
        flags = []
        for flag in query.flags.all():
            flags.append({
                'id': flag.id,
                'flag_id': flag.flag_id,
                'flag_type': flag.get_flag_type_display(),
                'description': flag.description,
                'severity': flag.severity,
                'flagged_by': f"{flag.flagged_by.first_name} {flag.flagged_by.last_name}",
                'flagged_date': flag.created_date.strftime('%Y-%m-%d %H:%M'),
                'reviewed': flag.reviewed,
                'reviewed_by': f"{flag.reviewed_by.first_name} {flag.reviewed_by.last_name}" if flag.reviewed_by else None,
                'review_notes': flag.review_notes,
                'review_date': flag.review_date.strftime('%Y-%m-%d %H:%M') if flag.review_date else None,
            })
        
        # Get escalations
        escalations = []
        for escalation in query.escalations.select_related('escalated_to').all():
            escalations.append({
                'id': escalation.id,
                'escalation_id': escalation.escalation_id,
                'escalation_type': escalation.get_escalation_type_display(),
                'reason': escalation.reason,
                'escalated_to': f"{escalation.escalated_to.first_name} {escalation.escalated_to.last_name}",
                'priority': escalation.priority.name,
                'due_date': escalation.due_date.strftime('%Y-%m-%d %H:%M'),
                'resolved': escalation.resolved,
                'resolution_notes': escalation.resolution_notes,
                'resolved_date': escalation.resolved_date.strftime('%Y-%m-%d %H:%M') if escalation.resolved_date else None,
                'is_overdue': escalation.is_overdue,
            })
        
        query_data = {
            'id': query.id,
            'query_id': query.query_id,
            'title': query.title,
            'description': query.description,
            'category': query.category.name,
            'priority': query.priority.name,
            'priority_color': query.priority.color,
            'status': query.status.name,
            'status_color': query.status.color,
            'assigned_to': f"{query.assigned_to.first_name} {query.assigned_to.last_name}",
            'assigned_to_id': query.assigned_to.id,
            'created_by': f"{query.created_by.first_name} {query.created_by.last_name}",
            'created_date': query.created_date.strftime('%Y-%m-%d %H:%M'),
            'due_date': query.due_date.strftime('%Y-%m-%d %H:%M') if query.due_date else None,
            'is_overdue': query.is_overdue,
            'requires_follow_up': query.requires_follow_up,
            'is_escalated': query.is_escalated,
            'household': str(query.household) if query.household else None,
            'farmer': str(query.farmer) if query.farmer else None,
            'child': str(query.child) if query.child else None,
            'responses': responses,
            'flags': flags,
            'escalations': escalations,
        }
        
        return JsonResponse({
            'success': True,
            'data': query_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching query details: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def respond_to_query_api(request, query_id):
    """Add response to a query"""
    try:
        data = json.loads(request.body)
        query = get_object_or_404(Query, id=query_id)
        current_user = staffTbl.objects.get(user=request.user)
        
        # Create response
        response = QueryResponse.objects.create(
            query=query,
            responded_by=current_user,
            response_text=data['response_text'],
        )
        
        # Update query status if needed
        if data.get('mark_as_resolved', False):
            resolved_status = QueryStatus.objects.get(name='Resolved')
            query.status = resolved_status
            query.resolved_date = timezone.now()
            query.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Response added successfully',
            'response_id': response.id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error adding response: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def flag_query_api(request, query_id):
    """Flag a query for review"""
    try:
        data = json.loads(request.body)
        query = get_object_or_404(Query, id=query_id)
        current_user = staffTbl.objects.get(user=request.user)
        
        # Create flag
        flag = FlaggedIssue.objects.create(
            query=query,
            flag_type=data['flag_type'],
            description=data['description'],
            severity=data['severity'],
            flagged_by=current_user,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Query flagged successfully',
            'flag_id': flag.flag_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error flagging query: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def escalate_query_api(request, query_id):
    """Escalate a query to supervisors"""
    try:
        data = json.loads(request.body)
        query = get_object_or_404(Query, id=query_id)
        current_user = staffTbl.objects.get(user=request.user)
        
        # Create escalation
        escalation = Escalation.objects.create(
            query=query,
            escalation_type=data['escalation_type'],
            reason=data['reason'],
            escalated_by=current_user,
            escalated_to_id=data['escalated_to_id'],
            priority_id=data['priority_id'],
            due_date=data['due_date'],
        )
        
        # Mark query as escalated
        query.is_escalated = True
        query.escalated_to_id = data['escalated_to_id']
        query.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Query escalated successfully',
            'escalation_id': escalation.escalation_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error escalating query: {str(e)}'
        }, status=500)

# @login_required
# @require_http_methods(["GET"])
# def get_enumerators_api(request):
#     """Get list of enumerators for dropdowns"""
#     try:
#         enumerators = staffTbl.objects.filter(
#             Q(designation__name__icontains='NSP') | Q(designation__name__icontains='field'),
#             delete_field='no'
#         ).values('id', 'first_name', 'last_name', 'staffid')
        
#         return JsonResponse({
#             'success': True,
#             'data': list(enumerators)
#         })
        
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'message': f'Error fetching enumerators: {str(e)}'
#         }, status=500)

@login_required
@require_http_methods(["GET"])
def get_supervisors_api(request):
    """Get list of supervisors for dropdowns"""
    try:
        supervisors = staffTbl.objects.filter(
            Q(designation__name__icontains='Supervisor') | Q(designation__name__icontains='manager'),
            delete_field='no'
        ).values('id', 'first_name', 'last_name', 'staffid')
        
        return JsonResponse({
            'success': True,
            'data': list(supervisors)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching supervisors: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_categories_api(request):
    """Get list of query categories"""
    try:
        categories = QueryCategory.objects.filter(delete_field='no').values('id', 'name', 'description')
        return JsonResponse(list(categories), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching categories: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_households_api(request):
    """Get list of households for dropdowns"""
    try:
        search = request.GET.get('search', '')
        households = houseHoldTbl.objects.filter(delete_field='no')
        
        if search:
            households = households.filter(
                Q(id__icontains=search) |
                Q(farmer__first_name__icontains=search) |
                Q(farmer__last_name__icontains=search)
            )
        
        households_data = []
        for household in households[:50]:  # Limit to 50 results
            households_data.append({
                'id': household.id,
                'display_name': f"{household.farmer.first_name} {household.farmer.last_name} - {household.id}",
                'farmer_name': f"{household.farmer.first_name} {household.farmer.last_name}",
                'farmer_id': household.farmer.id,
            })
        
        return JsonResponse({
            'success': True,
            'data': households_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching households: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_farmers_api(request):
    """Get list of farmers for dropdowns"""
    try:
        search = request.GET.get('search', '')
        farmers = farmerTbl.objects.filter(delete_field='no')
        
        if search:
            farmers = farmers.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(farmer_code__icontains=search)
            )
        
        farmers_data = []
        for farmer in farmers[:50]:  # Limit to 50 results
            farmers_data.append({
                'id': farmer.id,
                'display_name': f"{farmer.first_name} {farmer.last_name} ({farmer.farmer_code})",
                'first_name': farmer.first_name,
                'last_name': farmer.last_name,
                'farmer_code': farmer.farmer_code,
            })
        
        return JsonResponse({
            'success': True,
            'data': farmers_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching farmers: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_children_api(request):
    """Get list of children for dropdowns"""
    try:
        search = request.GET.get('search', '')
        children = ChildInHouseholdTbl.objects.filter(delete_field='no')
        
        if search:
            children = children.filter(
                Q(child_first_name__icontains=search) |
                Q(child_surname__icontains=search) |
                Q(houseHold__farmer__first_name__icontains=search) |
                Q(houseHold__farmer__last_name__icontains=search)
            )
        
        children_data = []
        for child in children[:50]:  # Limit to 50 results
            children_data.append({
                'id': child.id,
                'display_name': f"{child.child_first_name} {child.child_surname} - {child.houseHold.farmer.first_name} {child.houseHold.farmer.last_name}",
                'first_name': child.child_first_name,
                'last_name': child.child_surname,
                'household_id': child.houseHold.id,
                'farmer_name': f"{child.houseHold.farmer.first_name} {child.houseHold.farmer.last_name}",
            })
        
        return JsonResponse({
            'success': True,
            'data': children_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching children: {str(e)}'
        }, status=500)
    


########################################################################################################################################

@login_required
def review_responses(request):
    """Send Query to Enumerator page"""
    return render(request, 'core/review_responses.html')




# queries/views.py - Add these new endpoints

@login_required
@require_http_methods(["GET"])
def response_list_api(request):
    """Get list of responses with filtering"""
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        enumerator_filter = request.GET.get('enumerator', '')
        date_range = request.GET.get('date_range', '')
        search = request.GET.get('search', '')
        from_date = request.GET.get('from_date', '')
        to_date = request.GET.get('to_date', '')
        
        # Build filter conditions
        filters = Q(query__isnull=False)
        
        if status_filter:
            filters &= Q(query__status__name=status_filter)
        if priority_filter:
            filters &= Q(query__priority__name=priority_filter)
        if enumerator_filter:
            filters &= Q(responded_by__id=enumerator_filter)
        if search:
            filters &= (
                Q(query__title__icontains=search) |
                Q(response_text__icontains=search) |
                Q(responded_by__first_name__icontains=search) |
                Q(responded_by__last_name__icontains=search)
            )
        
        # Date range filtering
        if date_range:
            now = timezone.now()
            if date_range == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                filters &= Q(created_date__gte=start_date)
            elif date_range == 'week':
                start_date = now - timedelta(days=now.weekday())
                start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
                filters &= Q(created_date__gte=start_date)
            elif date_range == 'month':
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                filters &= Q(created_date__gte=start_date)
            elif date_range == 'custom' and from_date and to_date:
                start_date = datetime.strptime(from_date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                end_date = datetime.strptime(to_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                filters &= Q(created_date__range=(start_date, end_date))
        
        # Get responses with related data
        responses = QueryResponse.objects.filter(filters).select_related(
            'query', 'query__category', 'query__priority', 'query__status', 'responded_by'
        ).order_by('-created_date')
        
        # Prepare response data
        responses_data = []
        for response in responses:
            responses_data.append({
                'id': response.id,
                'query_id': response.query.query_id,
                'query_title': response.query.title,
                'enumerator_name': f"{response.responded_by.first_name} {response.responded_by.last_name}",
                'enumerator_id': response.responded_by.id,
                'response_date': response.created_date.strftime('%Y-%m-%d %H:%M'),
                'response_text': response.response_text,
                'response_preview': response.response_text[:200] + '...' if len(response.response_text) > 200 else response.response_text,
                'status': response.query.status.name,
                'status_color': response.query.status.color,
                'priority': response.query.priority.name,
                'priority_color': response.query.priority.color,
                'due_date': response.query.due_date.strftime('%Y-%m-%d %H:%M') if response.query.due_date else None,
                # 'is_overdue': response.query.is_overdue,
                'attachment': response.attachment.url if response.attachment else None,
            })
        

        print(responses_data)
        # Calculate statistics
        total_responses = responses.count()
        resolved_count = responses.filter(query__status__name='Resolved').count()
        pending_count = responses.filter(query__status__name__in=['Open', 'In Progress']).count()
        # overdue_count = responses.filter(query__is_overdue=True).count()
        
        return JsonResponse({
            'success': True,
            'data': responses_data,
            'statistics': {
                'total_responses': total_responses,
                'resolved_count': resolved_count,
                'pending_count': pending_count,
                # 'overdue_count': overdue_count,
            }
        })
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'success': False,
            'message': f'Error fetching responses: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def response_detail_api(request, response_id):
    """Get detailed information about a specific response"""
    try:
        response = get_object_or_404(QueryResponse, id=response_id)
        query = response.query
        
        # Get previous responses for this query
        previous_responses = QueryResponse.objects.filter(
            query=query,
            created_date__lt=response.created_date
        ).select_related('responded_by').order_by('-created_date')
        
        previous_responses_data = []
        for prev_response in previous_responses:
            previous_responses_data.append({
                'responded_by': f"{prev_response.responded_by.first_name} {prev_response.responded_by.last_name}",
                'responded_date': prev_response.created_date.strftime('%Y-%m-%d %H:%M'),
                'response_text': prev_response.response_text,
            })
        
        response_data = {
            'id': response.id,
            'query_id': query.query_id,
            'query_title': query.title,
            'query_description': query.description,
            'enumerator_name': f"{response.responded_by.first_name} {response.responded_by.last_name}",
            'response_date': response.created_date.strftime('%Y-%m-%d %H:%M'),
            'response_text': response.response_text,
            'status': query.status.name,
            'status_color': query.status.color,
            'priority': query.priority.name,
            'priority_color': query.priority.color,
            'due_date': query.due_date.strftime('%Y-%m-%d %H:%M') if query.due_date else None,
            'is_overdue': query.is_overdue,
            'attachment': response.attachment.url if response.attachment else None,
            'previous_responses': previous_responses_data,
        }
        
        return JsonResponse({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching response details: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def mark_query_resolved_api(request, query_id):
    """Mark a query as resolved"""
    try:
        query = get_object_or_404(Query, id=query_id)
        resolved_status = QueryStatus.objects.get(name='Resolved')
        
        query.status = resolved_status
        query.resolved_date = timezone.now()
        query.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Query marked as resolved successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error marking query as resolved: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def request_clarification_api(request, query_id):
    """Request clarification for a query"""
    try:
        data = json.loads(request.body)
        query = get_object_or_404(Query, id=query_id)
        current_user = staffTbl.objects.get(user=request.user)
        
        # Create a new query for clarification
        clarification_query = Query.objects.create(
            title=f"Clarification Request: {query.title}",
            description=data['clarification_text'],
            category=QueryCategory.objects.get(name='Clarification Needed'),
            priority_id=data['priority_id'],
            status=QueryStatus.objects.get(name='Open'),
            assigned_to=query.assigned_to,
            created_by=current_user,
            requires_follow_up=True,
            household=query.household,
            farmer=query.farmer,
            child=query.child,
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Clarification request sent successfully',
            'query_id': clarification_query.query_id
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error sending clarification request: {str(e)}'
        }, status=500)
    



##################################################################################################################

# pci/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.decorators import login_required

from .models import pciTbl, districtTbl, societyTbl, staffTbl, districtStaffTbl
from datetime import datetime

@login_required
def community_pci_view(request):
    """Render the main PCI management page"""
    return render(request, 'core/community_pci.html')

@login_required
@require_http_methods(["GET"])
def pci_list_api(request):
    """API endpoint to get filtered PCI assessments"""
    try:
        # Get filter parameters
        status = request.GET.get('status', '')
        district_id = request.GET.get('district', '')
        community_id = request.GET.get('community', '')
        enumerator_id = request.GET.get('enumerator', '')
        
        # Build query filters
        filters = {}
        if status:
            filters['status'] = status
        if community_id:
            filters['society_id'] = community_id
        if enumerator_id:
            filters['enumerator_id'] = enumerator_id
        
        # If district filter is applied, filter by communities in that district
        if district_id:
            communities_in_district = societyTbl.objects.filter(
                districtTbl_foreignkey_id=district_id
            ).values_list('id', flat=True)
            filters['society_id__in'] = list(communities_in_district)
        
        # Get PCI assessments
        pci_assessments = pciTbl.objects.filter(**filters).select_related(
            'society', 'society__districtTbl_foreignkey', 'enumerator'
        ).order_by('-created_at')
        
        # Prepare data for response
        data = []
        for pci in pci_assessments:
            data.append({
                'id': pci.id,
                'assessment_id': f"PCI-{pci.id:04d}",
                'community': str(pci.society) if pci.society else 'N/A',
                'district': str(pci.society.districtTbl_foreignkey.district) if pci.society and pci.society.districtTbl_foreignkey else 'N/A',
                'enumerator': f"{pci.enumerator.staffTbl_foreignkey.first_name} {pci.enumerator.staffTbl_foreignkey.last_name}" if pci.enumerator else 'N/A',
                'total_index': float(pci.total_index),
                'status': pci.status,
                'assessment_date': pci.created_at.strftime('%Y-%m-%d'),
                'water_access': pci.access_to_protected_water,
                'adult_labor': pci.hire_adult_labourers,
                'awareness': pci.awareness_raising_session,
                'women_leaders': pci.women_leaders,
                'pre_school': pci.pre_school,
                'primary_school': pci.primary_school,
                'separate_toilets': pci.separate_toilets,
                'provide_food': pci.provide_food,
                'scholarships': pci.scholarships,
                'corporal_punishment': pci.corporal_punishment
            })
        
        # Get statistics
        total_assessments = pciTbl.objects.count()
        low_risk_count = pciTbl.objects.filter(status='low_risk').count()
        medium_risk_count = pciTbl.objects.filter(status='medium_risk').count()
        high_risk_count = pciTbl.objects.filter(status='high_risk').count()
        
        statistics = {
            'total_assessments': total_assessments,
            'low_risk_count': low_risk_count,
            'medium_risk_count': medium_risk_count,
            'high_risk_count': high_risk_count
        }
        
        return JsonResponse({
            'success': True,
            'data': data,
            'statistics': statistics
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching PCI data: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_pci_api(request):
    """API endpoint to create a new PCI assessment"""
    try:
        data = json.loads(request.body)
        print(data)
        
        # Validate required fields
        required_fields = [
            'society_id', 'enumerator_id', 'assessment_date',
            'access_to_protected_water', 'hire_adult_labourers',
            'awareness_raising_session', 'women_leaders', 'pre_school',
            'primary_school', 'separate_toilets', 'provide_food',
            'scholarships', 'corporal_punishment'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return JsonResponse({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=400)
        
        # Check if society exists
        society = get_object_or_404(societyTbl, id=data['society_id'])
        
        # Check if enumerator exists
        enumerator = get_object_or_404(districtStaffTbl, id=data['enumerator_id'])
        
        # Parse assessment date
        try:
            assessment_date = datetime.strptime(data['assessment_date'], '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid date format. Use YYYY-MM-DD.'
            }, status=400)
        
        # Create PCI assessment
        with transaction.atomic():
            pci = pciTbl(
                society=society,
                enumerator=enumerator,
                access_to_protected_water=data['access_to_protected_water'],
                hire_adult_labourers=data['hire_adult_labourers'],
                awareness_raising_session=data['awareness_raising_session'],
                women_leaders=data['women_leaders'],
                pre_school=data['pre_school'],
                primary_school=data['primary_school'],
                separate_toilets=data['separate_toilets'],
                provide_food=data['provide_food'],
                scholarships=data['scholarships'],
                corporal_punishment=data['corporal_punishment']
            )
            
            # Calculate total index and status
            pci.calculate_total_index()
            pci.save()
        
        return JsonResponse({
            'success': True,
            'message': 'PCI assessment created successfully',
            'data': {
                'id': pci.id,
                'total_index': float(pci.total_index),
                'status': pci.status
            }
        })
        
    except societyTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Society not found'
        }, status=404)
        
    except staffTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Enumerator not found'
        }, status=404)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'message': f'Validation error: {str(e)}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating PCI assessment: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def pci_detail_api(request, pci_id):
    """API endpoint to get detailed PCI assessment information"""
    try:
        pci = get_object_or_404(pciTbl, id=pci_id)
        
        # Prepare indicators data
        indicators = [
            {
                'name': 'Access to Protected Water',
                'description': 'Do most households have access to protected water?',
                'score': pci.access_to_protected_water
            },
            {
                'name': 'Adult Labor Hiring',
                'description': 'Do households hire adult laborers?',
                'score': pci.hire_adult_labourers
            },
            {
                'name': 'Awareness Raising Sessions',
                'description': 'Child labor awareness sessions in past year?',
                'score': pci.awareness_raising_session
            },
            {
                'name': 'Women in Leadership',
                'description': 'Are there women among community leaders?',
                'score': pci.women_leaders
            },
            {
                'name': 'Pre-school Availability',
                'description': 'Is there at least one pre-school?',
                'score': pci.pre_school
            },
            {
                'name': 'Primary School Availability',
                'description': 'Is there at least one primary school?',
                'score': pci.primary_school
            },
            {
                'name': 'Separate Toilets in Schools',
                'description': 'Separate toilets for boys and girls?',
                'score': pci.separate_toilets
            },
            {
                'name': 'School Food Provision',
                'description': 'Do schools provide food?',
                'score': pci.provide_food
            },
            {
                'name': 'Scholarship Access',
                'description': 'Children access scholarships for high school?',
                'score': pci.scholarships
            },
            {
                'name': 'No Corporal Punishment',
                'description': 'Absence of corporal punishment in schools?',
                'score': pci.corporal_punishment
            }
        ]
        
        data = {
            'id': pci.id,
            'assessment_id': f"PCI-{pci.id:04d}",
            'community': str(pci.society) if pci.society else 'N/A',
            'district': str(pci.society.districtTbl_foreignkey.district) if pci.society and pci.society.districtTbl_foreignkey else 'N/A',
            'enumerator': f"{pci.enumerator.staffTbl_foreignkey.first_name} {pci.enumerator.staffTbl_foreignkey.last_name}" if pci.enumerator else 'N/A',
            'total_index': float(pci.total_index),
            'status': pci.status,
            'assessment_date': pci.created_at.strftime('%Y-%m-%d'),
            'indicators': indicators
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except pciTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'PCI assessment not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching PCI details: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_pci_api(request, pci_id):
    """API endpoint to delete a PCI assessment"""
    try:
        pci = get_object_or_404(pciTbl, id=pci_id)
        pci.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'PCI assessment deleted successfully'
        })
        
    except pciTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'PCI assessment not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting PCI assessment: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_districts_api(request):
    """API endpoint to get all districts"""
    try:
        districts = districtTbl.objects.all().values('id', 'district')
        return JsonResponse(list(districts), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching districts: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_communities_api(request):
    """API endpoint to get all communities"""
    try:
        communities = societyTbl.objects.all().values('id', 'society')
        return JsonResponse(list(communities), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching communities: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_enumerators_api(request):
    """API endpoint to get all enumerators (staff with appropriate roles)"""
    try:
        # You might want to filter staff by role (e.g., enumerators only)
        # In your view
        enumerators = districtStaffTbl.objects.values(
            'id',
            'staffTbl_foreignkey__first_name', 
            'staffTbl_foreignkey__last_name',
            'staffTbl_foreignkey__staffid'  # Add this line
        )
        print(enumerators)
        return JsonResponse({
            'success': True,
            'data': list(enumerators)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching enumerators: {str(e)}'
        }, status=500)
    

################################################################################################################################


# farmer_children/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.core.serializers.json import DjangoJSONEncoder

from .models import ChildInHouseholdTbl, houseHoldTbl, farmerTbl, societyTbl, districtTbl
from datetime import datetime

@login_required
def farmer_children_view(request):
    """Render the main Farmer Children management page"""
    return render(request, 'farmer_children/farmer_children.html')

@login_required
@require_http_methods(["GET"])
def farmer_children_list_api(request):
    """API endpoint to get filtered farmer children"""
    try:
        # Get filter parameters
        farmer_id = request.GET.get('farmer', '')
        community_id = request.GET.get('community', '')
        district_id = request.GET.get('district', '')
        gender = request.GET.get('gender', '')
        education_status = request.GET.get('education_status', '')
        work_status = request.GET.get('work_status', '')
        
        # Build query filters
        filters = {}
        if farmer_id:
            filters['houseHold__farmer_id'] = farmer_id
        if gender:
            filters['child_gender'] = gender
        if education_status:
            if education_status == 'enrolled':
                filters['child_educated'] = 1
            elif education_status == 'not_enrolled':
                filters['child_educated'] = 0
        
        # If community filter is applied
        if community_id:
            filters['houseHold__farmer__society_name_id'] = community_id
        
        # If district filter is applied, filter by communities in that district
        if district_id:
            communities_in_district = societyTbl.objects.filter(
                districtTbl_foreignkey_id=district_id
            ).values_list('id', flat=True)
            filters['houseHold__farmer__society_name_id__in'] = list(communities_in_district)
        
        # Work status filter
        work_filters = Q()
        if work_status == 'working':
            work_filters = Q(work_in_house='yes') | Q(work_on_cocoa='yes')
        elif work_status == 'not_working':
            work_filters = Q(work_in_house='no') & Q(work_on_cocoa='no')
        
        # Get farmer children with related data
        children = ChildInHouseholdTbl.objects.filter(
            **filters
        ).filter(work_filters).select_related(
            'houseHold',
            'houseHold__farmer',
            'houseHold__farmer__society_name',
            'houseHold__farmer__society_name__districtTbl_foreignkey'
        ).order_by('-created_at')
        
        # Prepare data for response
        data = []
        for child in children:
            farmer = child.houseHold.farmer if child.houseHold and child.houseHold.farmer else None
            society = farmer.society_name if farmer else None
            district = society.districtTbl_foreignkey if society else None
            
            # Determine work status
            work_status = 'Not Working'
            if child.work_in_house == 'yes' or child.work_on_cocoa == 'yes':
                work_status = 'Working'
            
            # Determine education status
            education_status = 'Not Enrolled'
            if child.child_educated == 1:
                education_status = 'Enrolled'
            
            data.append({
                'id': child.id,
                'child_id': f"CHD-{child.id:04d}",
                'first_name': child.child_first_name,
                'last_name': child.child_surname,
                'full_name': f"{child.child_first_name} {child.child_surname}",
                'gender': child.child_gender,
                'age': datetime.now().year - child.child_year_birth if child.child_year_birth else 'N/A',
                'year_of_birth': child.child_year_birth,
                'education_status': education_status,
                'work_status': work_status,
                'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'farmer_code': farmer.farmer_code if farmer else 'N/A',
                'community': society.society if society else 'N/A',
                'district': district.district if district else 'N/A',
                'created_at': child.created_at.strftime('%Y-%m-%d'),
                'has_birth_certificate': child.child_birth_certificate,
                'school_name': child.child_school_name,
                'grade': child.child_grade,
                'household_tasks': child.performed_tasks if child.performed_tasks else []
            })
        
        # Get statistics
        total_children = ChildInHouseholdTbl.objects.count()
        enrolled_count = ChildInHouseholdTbl.objects.filter(child_educated=1).count()
        not_enrolled_count = ChildInHouseholdTbl.objects.filter(child_educated=0).count()
        working_count = ChildInHouseholdTbl.objects.filter(
            Q(work_in_house='yes') | Q(work_on_cocoa='yes')
        ).count()
        not_working_count = total_children - working_count
        male_count = ChildInHouseholdTbl.objects.filter(child_gender='Male').count()
        female_count = ChildInHouseholdTbl.objects.filter(child_gender='Female').count()
        
        # Age distribution
        age_distribution = ChildInHouseholdTbl.objects.annotate(
            age=datetime.now().year - models.F('child_year_birth')
        ).values('age').annotate(
            count=Count('id')
        ).order_by('age')
        
        statistics = {
            'total_children': total_children,
            'enrolled_count': enrolled_count,
            'not_enrolled_count': not_enrolled_count,
            'working_count': working_count,
            'not_working_count': not_working_count,
            'male_count': male_count,
            'female_count': female_count,
            'age_distribution': list(age_distribution)
        }
        
        return JsonResponse({
            'success': True,
            'data': data,
            'statistics': statistics
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching farmer children data: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_farmer_child_api(request):
    """API endpoint to create a new farmer child record"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = [
            'household_id', 'child_first_name', 'child_surname',
            'child_gender', 'child_year_birth'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return JsonResponse({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=400)
        
        # Check if household exists
        household = get_object_or_404(houseHoldTbl, id=data['household_id'])
        
        # Validate year of birth (child must be between 5-17 years old)
        current_year = datetime.now().year
        child_age = current_year - data['child_year_birth']
        if not (5 <= child_age <= 17):
            return JsonResponse({
                'success': False,
                'message': 'Child must be between 5 and 17 years old'
            }, status=400)
        
        # Create child record
        with transaction.atomic():
            child = ChildInHouseholdTbl(
                houseHold=household,
                child_first_name=data['child_first_name'],
                child_surname=data['child_surname'],
                child_gender=data['child_gender'],
                child_year_birth=data['child_year_birth'],
                child_birth_certificate=data.get('child_birth_certificate', 'no'),
                child_educated=data.get('child_educated', 0),
                child_school_name=data.get('child_school_name', ''),
                child_grade=data.get('child_grade', ''),
                work_in_house=data.get('work_in_house', 'no'),
                work_on_cocoa=data.get('work_on_cocoa', 'no'),
                performed_tasks=data.get('performed_tasks', [])
            )
            
            child.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Child record created successfully',
            'data': {
                'id': child.id,
                'full_name': f"{child.child_first_name} {child.child_surname}"
            }
        })
        
    except houseHoldTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Household not found'
        }, status=404)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'message': f'Validation error: {str(e)}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating child record: {str(e)}'
        }, status=500)



@login_required
@require_http_methods(["GET"])
def farmer_child_detail_api(request, child_id):
    """API endpoint to get detailed child information"""
    try:
        child = get_object_or_404(ChildInHouseholdTbl, id=child_id)
        
        # Get related data
        farmer = child.houseHold.farmer if child.houseHold else None
        society = farmer.society_name if farmer else None
        district = society.districtTbl_foreignkey if society else None
        
        # Prepare education data - handle None values for non-enrolled children
        education_data = {
            'is_enrolled': child.child_educated == 1,
            'school_name': child.child_school_name if child.child_school_name else '',
            'school_type': child.school_type if child.school_type else '',
            'grade': child.child_grade if child.child_grade else '',
            'school_attendance': child.child_school_7days if child.child_school_7days else '',
            'basic_needs': child.basic_need_available if child.basic_need_available else [],
            'assessment': {
                'calculation': child.calculation_response if child.calculation_response else '',
                'reading': child.reading_response if child.reading_response else '',
                'writing': child.writing_response if child.writing_response else ''
            }
        }
        
        # Prepare work data - handle None values
        work_data = {
            'house_work': child.work_in_house == 'yes',
            'cocoa_work': child.work_on_cocoa == 'yes',
            'work_frequency': child.work_frequency if child.work_frequency else '',
            'tasks_performed': child.performed_tasks if child.performed_tasks else [],
            'supervision': child.under_supervision if hasattr(child, 'under_supervision') and child.under_supervision else 'no'
        }
        
        # Prepare health data - handle None values
        # health_data = {
        #     'injuries': child.suffered_injury == 'yes',
        #     'injury_cause': child.wound_cause if child.wound_cause else '',
        #     'injury_time': child.wound_time if child.wound_time else '',
        #     'frequent_pains': child.child_often_pains == 'yes',
        #     'health_help': child.help_child_health if child.help_child_health else []
        # }
        
        data = {
            'id': child.id,
            'child_id': f"CHD-{child.id:04d}",
            'first_name': child.child_first_name,
            'last_name': child.child_surname,
            'full_name': f"{child.child_first_name} {child.child_surname}",
            'gender': child.child_gender,
            'year_of_birth': child.child_year_birth,
            'age': datetime.now().year - child.child_year_birth,
            'birth_certificate': child.child_birth_certificate,
            'birth_certificate_reason': child.child_birth_certificate_reason if child.child_birth_certificate_reason else '',
            
            # Family information
            'farmer': {
                'id': farmer.id if farmer else None,
                'name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'code': farmer.farmer_code if farmer else 'N/A'
            },
            'community': society.society if society else 'N/A',
            'district': district.district if district else 'N/A',
            
            # Education information
            'education': education_data,
            
            # Work information
            'work': work_data,
            
            # Health information
            # 'health': health_data,
            
            # Additional information
            'created_at': child.created_at.strftime('%Y-%m-%d'),
            'updated_at': child.updated_at.strftime('%Y-%m-%d') if child.updated_at else 'N/A'
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except ChildInHouseholdTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Child record not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching child details: {str(e)}'
        }, status=500)



@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_farmer_child_api(request, child_id):
    """API endpoint to delete a child record"""
    try:
        child = get_object_or_404(ChildInHouseholdTbl, id=child_id)
        child.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Child record deleted successfully'
        })
        
    except ChildInHouseholdTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Child record not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting child record: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_farmers_api(request):
    """API endpoint to get all farmers"""
    try:
        farmers = farmerTbl.objects.all().values('id', 'first_name', 'last_name', 'farmer_code')
        return JsonResponse(list(farmers), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching farmers: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_communities_api(request):
    """API endpoint to get all communities"""
    try:
        communities = societyTbl.objects.all().values('id', 'society')
        return JsonResponse(list(communities), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching communities: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_districts_api(request):
    """API endpoint to get all districts"""
    try:
        districts = districtTbl.objects.all().values('id', 'district')
        return JsonResponse(list(districts), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching districts: {str(e)}'
        }, status=500)
    


#########################################################################################################

# views.py
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from .models import RiskAssessment, ChildInHouseholdTbl, houseHoldTbl, farmerTbl, societyTbl, districtTbl
from .risk_assessment_utils import RiskAssessmentCalculator

@login_required
def risk_assessment_view(request):
    """Render the main risk assessment page"""
    return render(request, 'core/risk-assessment.html')

@login_required
@require_http_methods(["GET"])
def risk_assessment_list_api(request):
    """API endpoint to get filtered risk assessments"""
    try:
        # Get filter parameters
        risk_level = request.GET.get('risk_level', '')
        farmer_id = request.GET.get('farmer', '')
        community_id = request.GET.get('community', '')
        district_id = request.GET.get('district', '')
        gender = request.GET.get('gender', '')
        
        # Build query filters
        filters = {}
        if risk_level:
            filters['risk_level'] = risk_level
        
        if gender:
            filters['child__child_gender'] = gender
        
        # If farmer filter is applied
        if farmer_id:
            filters['child__houseHold__farmer_id'] = farmer_id
        
        # If community filter is applied
        if community_id:
            filters['child__houseHold__farmer__society_name_id'] = community_id
        
        # If district filter is applied
        if district_id:
            communities_in_district = societyTbl.objects.filter(
                districtTbl_foreignkey_id=district_id
            ).values_list('id', flat=True)
            filters['child__houseHold__farmer__society_name_id__in'] = list(communities_in_district)
        
        # Get risk assessments with related data
        risk_assessments = RiskAssessment.objects.filter(
            **filters
        ).select_related(
            'child',
            'child__houseHold',
            'child__houseHold__farmer',
            'child__houseHold__farmer__society_name',
            'child__houseHold__farmer__society_name__districtTbl_foreignkey'
        ).prefetch_related(
            'heavy_task_risks',
            'light_task_risks'
        ).order_by('-assessment_date')
        
        # Prepare data for response
        data = []
        for assessment in risk_assessments:
            child = assessment.child
            household = child.houseHold if child.houseHold else None
            farmer = household.farmer if household else None
            society = farmer.society_name if farmer else None
            district = society.districtTbl_foreignkey if society else None
            
            data.append({
                'id': assessment.id,
                'child_id': child.id,
                'child_name': f"{child.child_first_name} {child.child_surname}",
                'child_age': RiskAssessmentCalculator.calculate_child_age(child),
                'child_gender': child.child_gender,
                'risk_level': assessment.risk_level,
                'risk_level_display': assessment.get_risk_level_display(),
                'assessment_date': assessment.assessment_date.strftime('%Y-%m-%d'),
                'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'farmer_code': farmer.farmer_code if farmer else 'N/A',
                'community': society.society if society else 'N/A',
                'district': district.district if district else 'N/A',
                'heavy_task_count': assessment.heavy_task_risks.count(),
                'light_task_count': assessment.light_task_risks.count(),
                'is_active': assessment.is_active
            })
        
        # Get statistics
        total_assessments = RiskAssessment.objects.count()
        no_risk_count = RiskAssessment.objects.filter(risk_level='no_risk').count()
        light_risk_count = RiskAssessment.objects.filter(risk_level='light_risk').count()
        heavy_risk_count = RiskAssessment.objects.filter(risk_level='heavy_risk').count()
        both_risk_count = RiskAssessment.objects.filter(risk_level='both_risk').count()
        
        statistics = {
            'total_assessments': total_assessments,
            'no_risk_count': no_risk_count,
            'light_risk_count': light_risk_count,
            'heavy_risk_count': heavy_risk_count,
            'both_risk_count': both_risk_count
        }
        
        return JsonResponse({
            'success': True,
            'data': data,
            'statistics': statistics
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching risk assessment data: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def risk_assessment_detail_api(request, assessment_id):
    """API endpoint to get detailed risk assessment information"""
    try:
        assessment = get_object_or_404(RiskAssessment, id=assessment_id)
        child = assessment.child
        household = child.houseHold
        farmer = household.farmer if household else None
        society = farmer.society_name if farmer else None
        district = society.districtTbl_foreignkey if society else None
        
        # Prepare heavy task risks
        heavy_risks = []
        for risk in assessment.heavy_task_risks.all():
            heavy_risks.append({
                'task_name': risk.task_name,
                'hours_worked': float(risk.hours_worked),
                'detected_date': risk.risk_detected_date.strftime('%Y-%m-%d')
            })
        
        # Prepare light task risks
        light_risks = []
        for risk in assessment.light_task_risks.all():
            light_risks.append({
                'task_name': risk.task_name,
                'total_hours': float(risk.total_hours),
                'is_supervised': risk.is_supervised,
                'is_paid': risk.is_paid,
                'child_age_at_assessment': risk.child_age,
                'criteria_details': risk.criteria_details,
                'detected_date': risk.risk_detected_date.strftime('%Y-%m-%d')
            })
        
        data = {
            'id': assessment.id,
            'child': {
                'id': child.id,
                'name': f"{child.child_first_name} {child.child_surname}",
                'age': RiskAssessmentCalculator.calculate_child_age(child),
                'gender': child.child_gender,
                'year_of_birth': child.child_year_birth
            },
            'household': {
                'id': household.id if household else None,
                'name': f"Household {household.id}" if household else 'N/A'
            },
            'farmer': {
                'id': farmer.id if farmer else None,
                'name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'code': farmer.farmer_code if farmer else 'N/A'
            },
            'community': society.society if society else 'N/A',
            'district': district.district if district else 'N/A',
            'risk_level': assessment.risk_level,
            'risk_level_display': assessment.get_risk_level_display(),
            'assessment_date': assessment.assessment_date.strftime('%Y-%m-%d'),
            'last_updated': assessment.last_updated.strftime('%Y-%m-%d'),
            'is_active': assessment.is_active,
            'notes': assessment.notes,
            'heavy_task_risks': heavy_risks,
            'light_task_risks': light_risks,
            'total_heavy_risks': len(heavy_risks),
            'total_light_risks': len(light_risks)
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except RiskAssessment.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Risk assessment not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching risk assessment details: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def reassess_all_risks_api(request):
    """API endpoint to trigger reassessment of all risks"""
    print("reassess_all_risks_api")
    try:
        results = RiskAssessmentCalculator.assess_all_children()
        
        return JsonResponse({
            'success': True,
            'message': 'Risk reassessment completed successfully',
            'data': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error during risk reassessment: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def reassess_child_risk_api(request, child_id):
    """API endpoint to reassess risk for a specific child"""
    try:
        child = get_object_or_404(ChildInHouseholdTbl, id=child_id)
        risk_assessment = RiskAssessmentCalculator.perform_risk_assessment(child)
        
        return JsonResponse({
            'success': True,
            'message': f'Risk assessment completed for {child.child_first_name} {child.child_surname}',
            'data': {
                'risk_level': risk_assessment.risk_level,
                'risk_level_display': risk_assessment.get_risk_level_display()
            }
        })
        
    except ChildInHouseholdTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Child not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error during risk assessment: {str(e)}'
        }, status=500)
    



################################################################################################################################################

# household/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.core.serializers.json import DjangoJSONEncoder

from .models import AdultHouseholdMember, houseHoldTbl, farmerTbl, societyTbl, districtTbl
from datetime import datetime

@login_required
def adult_members_view(request):
    """Render the main Adult Members management page"""
    return render(request, 'core/adult_members.html')

@login_required
@require_http_methods(["GET"])
def adult_members_list_api(request):
    """API endpoint to get filtered adult members"""
    try:
        # Get filter parameters
        household_id = request.GET.get('household', '')
        farmer_id = request.GET.get('farmer', '')
        gender = request.GET.get('gender', '')
        relationship = request.GET.get('relationship', '')
        
        # Build query filters
        filters = {}
        if household_id:
            filters['houseHold_id'] = household_id
        if gender:
            filters['gender'] = gender
        if relationship:
            filters['relationship'] = relationship
        
        # If farmer filter is applied, filter by households of that farmer
        if farmer_id:
            filters['houseHold__farmer_id'] = farmer_id
        
        # Get adult members with related data
        members = AdultHouseholdMember.objects.filter(
            **filters
        ).select_related(
            'houseHold',
            'houseHold__farmer',
            'houseHold__farmer__society_name',
            'houseHold__farmer__society_name__districtTbl_foreignkey'
        ).order_by('-created_at')
        
        # Prepare data for response
        data = []
        for member in members:
            household = member.houseHold
            farmer = household.farmer if household else None
            society = farmer.society_name if farmer else None
            district = society.districtTbl_foreignkey if society else None
            
            data.append({
                'id': member.id,
                'member_id': f"ADT-{member.id:04d}",
                'full_name': member.full_name,
                'relationship': member.relationship,
                'relationship_display': member.get_relationship_display(),
                'gender': member.gender,
                'age': datetime.now().year - member.year_birth if member.year_birth else 'N/A',
                'year_of_birth': member.year_birth,
                'nationality': member.nationality,
                'birth_certificate': member.birth_certificate,
                'main_work': member.main_work,
                'main_work_display': member.get_main_work_display() if member.main_work else 'N/A',
                'household_id': household.id if household else None,
                'household_name': f"Household {household.id}" if household else 'N/A',
                'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'farmer_code': farmer.farmer_code if farmer else 'N/A',
                'community': society.society if society else 'N/A',
                'district': district.district if district else 'N/A',
                'created_at': member.created_at.strftime('%Y-%m-%d'),
                'updated_at': member.updated_at.strftime('%Y-%m-%d') if member.updated_at else 'N/A'
            })
        
        # Get statistics
        total_members = AdultHouseholdMember.objects.count()
        male_count = AdultHouseholdMember.objects.filter(gender='Male').count()
        female_count = AdultHouseholdMember.objects.filter(gender='Female').count()
        
        # Relationship distribution
        relationship_distribution = AdultHouseholdMember.objects.values(
            'relationship'
        ).annotate(
            count=Count('id')
        ).order_by('relationship')
        
        # Work distribution
        work_distribution = AdultHouseholdMember.objects.values(
            'main_work'
        ).annotate(
            count=Count('id')
        ).order_by('main_work')
        
        statistics = {
            'total_members': total_members,
            'male_count': male_count,
            'female_count': female_count,
            'relationship_distribution': list(relationship_distribution),
            'work_distribution': list(work_distribution)
        }
        
        return JsonResponse({
            'success': True,
            'data': data,
            'statistics': statistics
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching adult members data: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_adult_member_api(request):
    """API endpoint to create a new adult member record"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = [
            'household_id', 'full_name', 'relationship',
            'gender', 'year_birth', 'nationality'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                return JsonResponse({
                    'success': False,
                    'message': f'Missing required field: {field}'
                }, status=400)
        
        # Check if household exists
        household = get_object_or_404(houseHoldTbl, id=data['household_id'])
        
        # Validate year of birth (reasonable age range)
        current_year = datetime.now().year
        member_age = current_year - data['year_birth']
        if not (18 <= member_age <= 100):
            return JsonResponse({
                'success': False,
                'message': 'Adult member must be between 18 and 100 years old'
            }, status=400)
        
        # Create member record
        with transaction.atomic():
            member = AdultHouseholdMember(
                houseHold=household,
                full_name=data['full_name'],
                relationship=data['relationship'],
                relationship_other=data.get('relationship_other', ''),
                gender=data['gender'],
                nationality=data['nationality'],
                country_origin=data.get('country_origin', ''),
                country_origin_other=data.get('country_origin_other', ''),
                year_birth=data['year_birth'],
                birth_certificate=data.get('birth_certificate', 'no'),
                main_work=data.get('main_work', ''),
                main_work_other=data.get('main_work_other', '')
            )
            
            member.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Adult member record created successfully',
            'data': {
                'id': member.id,
                'full_name': member.full_name
            }
        })
        
    except houseHoldTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Household not found'
        }, status=404)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'message': f'Validation error: {str(e)}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating adult member record: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def adult_member_detail_api(request, member_id):
    """API endpoint to get detailed adult member information"""
    try:
        member = get_object_or_404(AdultHouseholdMember, id=member_id)
        household = member.houseHold
        farmer = household.farmer if household else None
        society = farmer.society_name if farmer else None
        district = society.districtTbl_foreignkey if society else None
        
        data = {
            'id': member.id,
            'member_id': f"ADT-{member.id:04d}",
            'full_name': member.full_name,
            'relationship': member.relationship,
            'relationship_display': member.get_relationship_display(),
            'relationship_other': member.relationship_other,
            'gender': member.gender,
            'year_of_birth': member.year_birth,
            'age': datetime.now().year - member.year_birth,
            'nationality': member.nationality,
            'country_origin': member.country_origin,
            'country_origin_other': member.country_origin_other,
            'birth_certificate': member.birth_certificate,
            'main_work': member.main_work,
            'main_work_display': member.get_main_work_display(),
            'main_work_other': member.main_work_other,
            
            # Household information
            'household': {
                'id': household.id if household else None,
                'name': f"Household {household.id}" if household else 'N/A'
            },
            
            # Farmer information
            'farmer': {
                'id': farmer.id if farmer else None,
                'name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'code': farmer.farmer_code if farmer else 'N/A'
            },
            
            # Location information
            'community': society.society if society else 'N/A',
            'district': district.district if district else 'N/A',
            
            # Timestamps
            'created_at': member.created_at.strftime('%Y-%m-%d'),
            'updated_at': member.updated_at.strftime('%Y-%m-%d') if member.updated_at else 'N/A'
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except AdultHouseholdMember.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Adult member not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching adult member details: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def update_adult_member_api(request, member_id):
    """API endpoint to update an adult member record"""
    try:
        member = get_object_or_404(AdultHouseholdMember, id=member_id)
        data = json.loads(request.body)
        
        # Update fields
        update_fields = [
            'full_name', 'relationship', 'relationship_other', 'gender',
            'nationality', 'country_origin', 'country_origin_other',
            'year_birth', 'birth_certificate', 'main_work', 'main_work_other'
        ]
        
        with transaction.atomic():
            for field in update_fields:
                if field in data:
                    setattr(member, field, data[field])
            
            # Validate year of birth if updated
            if 'year_birth' in data:
                current_year = datetime.now().year
                member_age = current_year - data['year_birth']
                if not (18 <= member_age <= 100):
                    return JsonResponse({
                        'success': False,
                        'message': 'Adult member must be between 18 and 100 years old'
                    }, status=400)
            
            member.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Adult member record updated successfully',
            'data': {
                'id': member.id,
                'full_name': member.full_name
            }
        })
        
    except AdultHouseholdMember.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Adult member not found'
        }, status=404)
        
    except ValidationError as e:
        return JsonResponse({
            'success': False,
            'message': f'Validation error: {str(e)}'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating adult member record: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_adult_member_api(request, member_id):
    """API endpoint to delete an adult member record"""
    try:
        member = get_object_or_404(AdultHouseholdMember, id=member_id)
        member.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Adult member record deleted successfully'
        })
        
    except AdultHouseholdMember.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Adult member not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting adult member record: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_households_api(request):
    """API endpoint to get all households"""
    try:
        households = houseHoldTbl.objects.all().values('id', 'farmer__first_name', 'farmer__last_name')
        data = []
        for household in households:
            data.append({
                'id': household['id'],
                'name': f"Household {household['id']} - {household['farmer__first_name']} {household['farmer__last_name']}"
            })
        return JsonResponse(data, safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching households: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_farmers_api(request):
    """API endpoint to get all farmers"""
    try:
        farmers = farmerTbl.objects.all().values('id', 'first_name', 'last_name', 'farmer_code')
        return JsonResponse(list(farmers), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching farmers: {str(e)}'
        }, status=500)
    



###############################################################################################################################################


# views.py - Add these child member views
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import json
from .models import ChildInHouseholdTbl, houseHoldTbl

@method_decorator(login_required, name='dispatch')
class ChildMembersView(View):
    def get(self, request):
        return render(request, 'core/child_members.html')

@login_required
def get_child_members_data(request):
    try:
        # Get all child members with related data
        children = ChildInHouseholdTbl.objects.select_related(
            'houseHold'
        ).all()
        
        data = []
        for child in children:
            data.append({
                'id': child.id,
                'child_identifier': child.child_identifier,
                'child_first_name': child.child_first_name,
                'child_surname': child.child_surname,
                'full_name': f"{child.child_first_name} {child.child_surname}",
                'child_gender': child.child_gender,
                'child_year_birth': child.child_year_birth,
                'age': timezone.now().year - child.child_year_birth if child.child_year_birth else 'N/A',
                'household_id': child.houseHold.id if child.houseHold else None,
                'household_code': child.houseHold.farmer.farmer_code if child.houseHold and child.houseHold.farmer else 'N/A',
                'child_birth_certificate': child.child_birth_certificate,
                'child_educated': child.child_educated,
                'child_school_name': child.child_school_name,
                'child_grade': child.child_grade,
                'mapped_status': child.houseHold.farmer.mapped_status if child.houseHold and child.houseHold.farmer else 'N/A',
                'created_date': child.created_date.strftime('%Y-%m-%d %H:%M:%S') if child.created_date else None,
                'updated_at': child.updated_at.strftime('%Y-%m-%d %H:%M:%S') if child.updated_at else None,
                'status': 'Active' if child.delete_field == 'no' else 'Inactive'
            })
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading child members: {str(e)}'})

@login_required
def get_child_member_details(request):
    try:
        child_id = request.GET.get('child_id')
        if not child_id:
            return JsonResponse({'success': False, 'message': 'Child ID is required'})
        
        child = get_object_or_404(ChildInHouseholdTbl, id=child_id)
        
        data = {
            'id': child.id,
            'child_declared_in_cover': child.child_declared_in_cover,
            'child_identifier': child.child_identifier,
            'child_can_be_surveyed': child.child_can_be_surveyed,
            'child_unavailability_reason': child.child_unavailability_reason,
            'child_not_avail': child.child_not_avail,
            'who_answers_child_unavailable': child.who_answers_child_unavailable,
            'who_answers_child_unavailable_other': child.who_answers_child_unavailable_other,
            'child_first_name': child.child_first_name,
            'child_surname': child.child_surname,
            'child_gender': child.child_gender,
            'child_year_birth': child.child_year_birth,
            'child_birth_certificate': child.child_birth_certificate,
            'child_birth_certificate_reason': child.child_birth_certificate_reason,
            'child_born_in_community': child.child_born_in_community,
            'child_country_of_birth': child.child_country_of_birth,
            'child_country_of_birth_other': child.child_country_of_birth_other,
            'child_relationship_to_head': child.child_relationship_to_head,
            'child_relationship_to_head_other': child.child_relationship_to_head_other,
            'child_not_live_with_family_reason': child.child_not_live_with_family_reason,
            'child_not_live_with_family_reason_other': child.child_not_live_with_family_reason_other,
            'child_decision_maker': child.child_decision_maker,
            'child_decision_maker_other': child.child_decision_maker_other,
            'child_agree_with_decision': child.child_agree_with_decision,
            'child_seen_parents': child.child_seen_parents,
            'child_last_seen_parent': child.child_last_seen_parent,
            'child_living_duration': child.child_living_duration,
            'child_accompanied_by': child.child_accompanied_by,
            'child_accompanied_by_other': child.child_accompanied_by_other,
            'child_father_location': child.child_father_location,
            'child_father_country': child.child_father_country,
            'child_father_country_other': child.child_father_country_other,
            'child_mother_location': child.child_mother_location,
            'child_mother_country': child.child_mother_country,
            'child_mother_country_other': child.child_mother_country_other,
            'child_educated': child.child_educated,
            'child_school_name': child.child_school_name,
            'school_type': child.school_type,
            'child_grade': child.child_grade,
            'sch_going_times': child.sch_going_times,
            'basic_need_available': child.basic_need_available,
            'child_schl2': child.child_schl2,
            'child_schl_left_age': child.child_schl_left_age,
            'calculation_response': child.calculation_response,
            'reading_response': child.reading_response,
            'writing_response': child.writing_response,
            'education_level': child.education_level,
            'child_schl_left_why': child.child_schl_left_why,
            'child_schl_left_why_other': child.child_schl_left_why_other,
            'child_why_no_school': child.child_why_no_school,
            'child_why_no_school_other': child.child_why_no_school_other,
            'child_school_7days': child.child_school_7days,
            'child_school_absence_reason': child.child_school_absence_reason,
            'child_school_absence_reason_other': child.child_school_absence_reason_other,
            'missed_school': child.missed_school,
            'missed_school_reason': child.missed_school_reason,
            'missed_school_reason_other': child.missed_school_reason_other,
            'work_in_house': child.work_in_house,
            'work_on_cocoa': child.work_on_cocoa,
            'work_frequency': child.work_frequency,
            'observed_work': child.observed_work,
            'performed_tasks': child.performed_tasks,
            'household_id': child.houseHold.id if child.houseHold else None,
            'status': 'Active' if child.delete_field == 'no' else 'Inactive'
        }
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading child member details: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_child_member(request):
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['child_first_name', 'child_surname', 'child_gender', 'child_year_birth', 'household_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'})
        
        # Validate household
        try:
            household = houseHoldTbl.objects.get(id=data['household_id'])
        except houseHoldTbl.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Household not found'})
        
        # Validate year of birth
        current_year = timezone.now().year
        if data['child_year_birth'] and (data['child_year_birth'] < 2007 or data['child_year_birth'] > current_year):
            return JsonResponse({'success': False, 'message': 'Child year of birth must be between 2007 and current year'})
        
        # Create new child member
        child = ChildInHouseholdTbl(
            child_first_name=data['child_first_name'],
            child_surname=data['child_surname'],
            child_gender=data['child_gender'],
            child_year_birth=data['child_year_birth'],
            houseHold=household,
            child_declared_in_cover=data.get('child_declared_in_cover', 'No'),
            child_identifier=data.get('child_identifier'),
            child_can_be_surveyed=data.get('child_can_be_surveyed', 'No'),
            child_unavailability_reason=data.get('child_unavailability_reason'),
            child_not_avail=data.get('child_not_avail'),
            child_birth_certificate=data.get('child_birth_certificate', 'No'),
            child_birth_certificate_reason=data.get('child_birth_certificate_reason'),
            child_born_in_community=data.get('child_born_in_community'),
            child_country_of_birth=data.get('child_country_of_birth'),
            child_country_of_birth_other=data.get('child_country_of_birth_other'),
            child_relationship_to_head=data.get('child_relationship_to_head'),
            child_relationship_to_head_other=data.get('child_relationship_to_head_other'),
            child_educated=data.get('child_educated', 0),
            child_school_name=data.get('child_school_name'),
            school_type=data.get('school_type'),
            child_grade=data.get('child_grade')
        )
        child.save()
        
        return JsonResponse({'success': True, 'message': 'Child member created successfully', 'child_id': child.id})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating child member: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_child_member(request, child_id):
    try:
        child = get_object_or_404(ChildInHouseholdTbl, id=child_id)
        data = json.loads(request.body)
        
        # Update basic fields
        if 'child_first_name' in data:
            child.child_first_name = data['child_first_name']
        if 'child_surname' in data:
            child.child_surname = data['child_surname']
        if 'child_gender' in data:
            child.child_gender = data['child_gender']
        if 'child_year_birth' in data:
            # Validate year of birth
            current_year = timezone.now().year
            if data['child_year_birth'] < 2007 or data['child_year_birth'] > current_year:
                return JsonResponse({'success': False, 'message': 'Child year of birth must be between 2007 and current year'})
            child.child_year_birth = data['child_year_birth']
        
        # Update other fields
        fields_to_update = [
            'child_declared_in_cover', 'child_identifier', 'child_can_be_surveyed',
            'child_unavailability_reason', 'child_not_avail', 'child_birth_certificate',
            'child_birth_certificate_reason', 'child_born_in_community', 'child_country_of_birth',
            'child_country_of_birth_other', 'child_relationship_to_head', 'child_relationship_to_head_other',
            'child_educated', 'child_school_name', 'school_type', 'child_grade', 'sch_going_times',
            'basic_need_available', 'child_schl2', 'child_schl_left_age', 'calculation_response',
            'reading_response', 'writing_response', 'education_level', 'child_schl_left_why',
            'child_schl_left_why_other', 'child_why_no_school', 'child_why_no_school_other',
            'child_school_7days', 'child_school_absence_reason', 'child_school_absence_reason_other',
            'missed_school', 'missed_school_reason', 'missed_school_reason_other', 'work_in_house',
            'work_on_cocoa', 'work_frequency', 'observed_work', 'performed_tasks'
        ]
        
        for field in fields_to_update:
            if field in data:
                setattr(child, field, data[field])
        
        # Update household if provided
        if 'household_id' in data and data['household_id']:
            try:
                household = houseHoldTbl.objects.get(id=data['household_id'])
                child.houseHold = household
            except houseHoldTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Household not found'})
        
        # Update status
        if 'status' in data:
            child.delete_field = 'yes' if data['status'] == 'Inactive' else 'no'
        
        child.save()
        
        return JsonResponse({'success': True, 'message': 'Child member updated successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating child member: {str(e)}'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_child_member(request, child_id):
    try:
        child = get_object_or_404(ChildInHouseholdTbl, id=child_id)
        child.delete()  # Soft delete
        return JsonResponse({'success': True, 'message': 'Child member deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting child member: {str(e)}'})

@login_required
def get_child_options_data(request):
    try:
        # Get household options
        households = houseHoldTbl.objects.filter(delete_field='no').select_related('farmer')
        household_options = []
        for household in households:
            if household.farmer:
                household_options.append({
                    'id': household.id,
                    'name': f"{household.farmer.farmer_code} - {household.farmer.first_name} {household.farmer.last_name}"
                })
        
        # Gender choices
        gender_choices = [
            {'value': 'Male', 'label': 'Male'},
            {'value': 'Female', 'label': 'Female'}
        ]
        
        # Education choices
        education_choices = [
            {'value': 1, 'label': 'Yes'},
            {'value': 0, 'label': 'No'}
        ]
        
        # Birth certificate choices
        birth_certificate_choices = [
            {'value': 'Yes', 'label': 'Yes'},
            {'value': 'No', 'label': 'No'}
        ]
        
        return JsonResponse({
            'success': True,
            'households': household_options,
            'genders': gender_choices,
            'education_status': education_choices,
            'birth_certificate': birth_certificate_choices
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading options: {str(e)}'})
    




##############################################################################################################

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
import json
from .models import lightTaskTbl

def light_tasks_list(request):
    """Render the light tasks list page"""
    return render(request, 'core/light_tasks_list.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_light_tasks_data(request):
    """Get all light tasks data for DataTable"""
    # print(request.GET)
    try:
        # Get query parameters for filtering, sorting, pagination
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        
        # Build query
        tasks = lightTaskTbl.objects.all().order_by('name')
        print(tasks)

        
        # Apply search filter
        if search_value:
            tasks = tasks.filter(name__icontains=search_value)
        
        # Get total count
        total_records = tasks.count()
        
        # Apply pagination
        tasks = tasks[start:start + length]
        
        # Prepare data for response
        data = []
        for task in tasks:
            data.append({
                'id': task.id,
                'name': task.name,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M')
            })

            print(data)
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'error': f'Error fetching light tasks: {str(e)}'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def create_light_task(request):
    """Create a new light task"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Task name is required'
            }, status=400)
        
        # Check if task already exists
        if lightTaskTbl.objects.filter(name__iexact=name).exists():
            return JsonResponse({
                'success': False,
                'message': 'A task with this name already exists'
            }, status=400)
        
        # Create new task
        task = lightTaskTbl(name=name)
        task.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Light task created successfully!',
            'data': {
                'id': task.id,
                'name': task.name
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'Database integrity error'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating light task: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_light_task_details(request, task_id):
    """Get details of a specific light task"""
    try:
        task = get_object_or_404(lightTaskTbl, id=task_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': task.id,
                'name': task.name
            }
        })
        
    except lightTaskTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Light task not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching task details: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_light_task(request, task_id):
    """Update an existing light task"""
    try:
        task = get_object_or_404(lightTaskTbl, id=task_id)
        data = json.loads(request.body)
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Task name is required'
            }, status=400)
        
        # Check if another task already has this name
        if lightTaskTbl.objects.filter(name__iexact=name).exclude(id=task_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Another task with this name already exists'
            }, status=400)
        
        # Update task
        task.name = name
        task.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Light task updated successfully!',
            'data': {
                'id': task.id,
                'name': task.name
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except lightTaskTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Light task not found'
        }, status=404)
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'Database integrity error'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating light task: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_light_task(request, task_id):
    """Delete a light task"""
    try:
        task = get_object_or_404(lightTaskTbl, id=task_id)
        task.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Light task deleted successfully!'
        })
        
    except lightTaskTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Light task not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting light task: {str(e)}'
        }, status=500)
    




############################################################################################################################


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import IntegrityError
import json
from .models import heavyTaskTbl, childHeavyTaskTbl, ChildInHouseholdTbl

def heavy_tasks_list(request):
    """Render the heavy tasks list page"""
    return render(request, 'core/heavy_tasks_list.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_heavy_tasks_data(request):
    """Get all heavy tasks data for DataTable"""
    try:
        # Get query parameters for filtering, sorting, pagination
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        
        # Build query
        tasks = heavyTaskTbl.objects.all().order_by('name')
        
        # Apply search filter
        if search_value:
            tasks = tasks.filter(name__icontains=search_value)
        
        # Get total count
        total_records = tasks.count()
        
        # Apply pagination
        tasks = tasks[start:start + length]
        
        # Prepare data for response
        data = []
        for task in tasks:
            data.append({
                'id': task.id,
                'name': task.name,
                'created_at': task.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching heavy tasks: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def create_heavy_task(request):
    """Create a new heavy task"""
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Task name is required'
            }, status=400)
        
        # Check if task already exists
        if heavyTaskTbl.objects.filter(name__iexact=name).exists():
            return JsonResponse({
                'success': False,
                'message': 'A task with this name already exists'
            }, status=400)
        
        # Create new task
        task = heavyTaskTbl(name=name)
        task.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Heavy task created successfully!',
            'data': {
                'id': task.id,
                'name': task.name
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'Database integrity error'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error creating heavy task: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_heavy_task_details(request, task_id):
    """Get details of a specific heavy task"""
    try:
        task = get_object_or_404(heavyTaskTbl, id=task_id)
        
        return JsonResponse({
            'success': True,
            'data': {
                'id': task.id,
                'name': task.name
            }
        })
        
    except heavyTaskTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Heavy task not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching task details: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def update_heavy_task(request, task_id):
    """Update an existing heavy task"""
    try:
        task = get_object_or_404(heavyTaskTbl, id=task_id)
        data = json.loads(request.body)
        
        # Validate required fields
        name = data.get('name', '').strip()
        if not name:
            return JsonResponse({
                'success': False,
                'message': 'Task name is required'
            }, status=400)
        
        # Check if another task already has this name
        if heavyTaskTbl.objects.filter(name__iexact=name).exclude(id=task_id).exists():
            return JsonResponse({
                'success': False,
                'message': 'Another task with this name already exists'
            }, status=400)
        
        # Update task
        task.name = name
        task.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Heavy task updated successfully!',
            'data': {
                'id': task.id,
                'name': task.name
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except heavyTaskTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Heavy task not found'
        }, status=404)
    except IntegrityError:
        return JsonResponse({
            'success': False,
            'message': 'Database integrity error'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating heavy task: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_heavy_task(request, task_id):
    """Delete a heavy task"""
    try:
        task = get_object_or_404(heavyTaskTbl, id=task_id)
        task.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Heavy task deleted successfully!'
        })
        
    except heavyTaskTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Heavy task not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error deleting heavy task: {str(e)}'
        }, status=500)

# Child Heavy Tasks Views
@csrf_exempt
@require_http_methods(["GET"])
def get_child_heavy_tasks_data(request, child_id=None):
    """Get all child heavy tasks data for DataTable"""
    try:
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        
        # Build query
        if child_id:
            child = get_object_or_404(ChildInHouseholdTbl, id=child_id)
            child_tasks = childHeavyTaskTbl.objects.filter(child=child)
        else:
            child_tasks = childHeavyTaskTbl.objects.all()
        
        # Apply search filter
        if search_value:
            child_tasks = child_tasks.filter(
                task__name__icontains=search_value
            )
        
        # Get total count
        total_records = child_tasks.count()
        
        # Apply pagination
        child_tasks = child_tasks[start:start + length]
        
        # Prepare data for response
        data = []
        for child_task in child_tasks:
            data.append({
                'id': child_task.id,
                'child_name': f"{child_task.child.child_first_name} {child_task.child.child_surname}",
                'task_name': child_task.task.name,
                'salary_received': child_task.salary_received,
                'task_location': child_task.task_location,
                'created_at': child_task.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': child_task.updated_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching child heavy tasks: {str(e)}'
        }, status=500)
    


################################################################################################################################################################

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import models
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.core.paginator import Paginator
import json
from .models import houseHoldTbl, ChildInHouseholdTbl, AdultHouseholdMember, Query, QueryStatus

def validate_data_list(request):
    """Render the validate submitted data list page"""
    return render(request, 'core/validate_data_list.html')

@csrf_exempt
@require_http_methods(["GET"])
def get_validation_data(request):
    """Get household data for validation with filters"""
    try:
        # Get query parameters
        draw = int(request.GET.get('draw', 1))
        start = int(request.GET.get('start', 0))
        length = int(request.GET.get('length', 10))
        search_value = request.GET.get('search[value]', '')
        status_filter = request.GET.get('status', 'all')
        risk_filter = request.GET.get('risk', 'all')
        
        # Build base query
        households = houseHoldTbl.objects.all().select_related(
            'farmer', 'enumerator__staffTbl_foreignkey'
        ).prefetch_related(
            'children', 'members'
        ).annotate(
            total_children=Count('children'),
            total_adults=Count('members'),
            validation_status=Case(
                When(children__risk_assessment__risk_level='no_risk', then=Value('low_risk')),
                When(children__risk_assessment__risk_level='light_risk', then=Value('medium_risk')),
                When(children__risk_assessment__risk_level='heavy_risk', then=Value('high_risk')),
                When(children__risk_assessment__risk_level='both_risk', then=Value('critical_risk')),
                default=Value('unknown'),
                output_field=models.CharField()
            )
        ).distinct()
        
        # Apply filters
        if search_value:
            households = households.filter(
                Q(farmer__first_name__icontains=search_value) |
                Q(farmer__last_name__icontains=search_value) |
                Q(farmer__farmer_code__icontains=search_value) |
                Q(enumerator__staffTbl_foreignkey__first_name__icontains=search_value) |
                Q(enumerator__staffTbl_foreignkey__last_name__icontains=search_value)
            )
        
        if status_filter != 'all':
            households = households.filter(validation_status=status_filter)
        
        # Get total count
        total_records = households.count()
        
        # Apply pagination
        households = households[start:start + length]
        
        # Prepare data for response
        data = []
        for household in households:
            # Get risk level from children
            risk_level = 'no_risk'
            child_risks = []
            for child in household.children.all():
                if hasattr(child, 'risk_assessment'):
                    risk_level = child.risk_assessment.risk_level
                    child_risks.append({
                        'name': f"{child.child_first_name} {child.child_surname}",
                        'risk': child.risk_assessment.get_risk_level_display()
                    })
            
            data.append({
                'id': household.id,
                'farmer_name': f"{household.farmer.first_name} {household.farmer.last_name}",
                'farmer_code': household.farmer.farmer_code,
                'enumerator': f"{household.enumerator.staffTbl_foreignkey.first_name} {household.enumerator.staffTbl_foreignkey.last_name}",
                'interview_date': household.interview_start_time.strftime('%Y-%m-%d') if household.interview_start_time else 'N/A',
                'total_children': household.total_children,
                'total_adult': household.total_adults,
                'risk_level': risk_level,
                'risk_display': dict(houseHoldTbl.RISK_LEVELS).get(risk_level, 'Unknown'),
                'child_risks': child_risks,
                'validation_status': household.get_validation_status_display() if hasattr(household, 'validation_status') else 'Pending',
                'created_at': household.created_date.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'draw': draw,
            'recordsTotal': total_records,
            'recordsFiltered': total_records,
            'data': data
        })
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'error': f'Error fetching validation data: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_household_details(request, household_id):
    """Get detailed household data for validation"""
    try:
        household = get_object_or_404(houseHoldTbl, id=household_id)
        
        # Get household members
        adults = []
        for adult in household.members.all():
            adults.append({
                'name': adult.full_name,
                'relationship': adult.get_relationship_display(),
                'gender': adult.get_gender_display(),
                'age': datetime.now().year - adult.year_birth if adult.year_birth else 'N/A'
            })
        
        # Get children with risk assessments
        children = []
        for child in household.children.all():
            child_data = {
                'name': f"{child.child_first_name} {child.child_surname}",
                'gender': child.get_child_gender_display(),
                'age': datetime.now().year - child.child_year_birth,
                'education_status': 'Enrolled' if child.child_educated == 1 else 'Not Enrolled',
                'risk_level': 'No Risk'
            }
            
            if hasattr(child, 'risk_assessment'):
                child_data['risk_level'] = child.risk_assessment.get_risk_level_display()
                child_data['risk_details'] = f"Assessed on {child.risk_assessment.assessment_date.strftime('%Y-%m-%d')}"
            
            children.append(child_data)
        
        response_data = {
            'household': {
                'id': household.id,
                'farmer': f"{household.farmer.first_name} {household.farmer.last_name}",
                'farmer_code': household.farmer.farmer_code,
                'interview_date': household.interview_start_time.strftime('%Y-%m-%d %H:%M') if household.interview_start_time else 'N/A',
                'community': household.farmer_residing_community or 'N/A',
                'gps_coordinates': household.gps_point or 'N/A',
                'total_members': household.total_adults + household.children.count()
            },
            'adults': adults,
            'children': children,
            'validation_info': {
                'status': household.get_validation_status_display() if hasattr(household, 'validation_status') else 'Pending',
                'last_updated': household.updated_at.strftime('%Y-%m-%d %H:%M') if household.updated_at else 'N/A'
            }
        }
        
        return JsonResponse({
            'success': True,
            'data': response_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching household details: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def validate_household(request, household_id):
    """Validate or reject a household survey"""
    try:
        data = json.loads(request.body)
        household = get_object_or_404(houseHoldTbl, id=household_id)
        action = data.get('action')
        notes = data.get('notes', '')
        validator = request.user.stafftbl  # Assuming user is linked to staff
        
        if action == 'approve':
            household.validation_status = 'approved'
            household.validated_by = validator
            household.validation_date = timezone.now()
            message = 'Household survey approved successfully'
            
        elif action == 'reject':
            household.validation_status = 'rejected'
            household.validation_notes = notes
            household.validated_by = validator
            household.validation_date = timezone.now()
            message = 'Household survey rejected'
            
            # Create a query for the enumerator to address issues
            query = Query.objects.create(
                title=f"Data Quality Issues - Household {household.id}",
                description=f"Survey validation failed. Issues: {notes}",
                category=QueryCategory.objects.get(name='Data Quality'),
                priority=QueryPriority.objects.get(name='High'),
                status=QueryStatus.objects.get(name='Open'),
                assigned_to=household.enumerator.staffTbl_foreignkey,
                created_by=validator,
                household=household,
                due_date=timezone.now() + timedelta(days=2)
            )
            
        elif action == 'request_changes':
            household.validation_status = 'changes_requested'
            household.validation_notes = notes
            message = 'Changes requested for household survey'
            
            # Create a query for changes
            query = Query.objects.create(
                title=f"Data Correction Required - Household {household.id}",
                description=f"Survey requires corrections: {notes}",
                category=QueryCategory.objects.get(name='Data Quality'),
                priority=QueryPriority.objects.get(name='Medium'),
                status=QueryStatus.objects.get(name='Open'),
                assigned_to=household.enumerator.staffTbl_foreignkey,
                created_by=validator,
                household=household,
                due_date=timezone.now() + timedelta(days=3)
            )
            
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid action'
            }, status=400)
        
        household.save()
        
        return JsonResponse({
            'success': True,
            'message': message
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error validating household: {str(e)}'
        }, status=500)

@csrf_exempt
@require_http_methods(["GET"])
def get_validation_stats(request):
    """Get statistics for validation dashboard"""
    try:
        total_households = houseHoldTbl.objects.count()
        validated_households = houseHoldTbl.objects.filter(
            validation_status__in=['approved', 'rejected']
        ).count()
        
        status_counts = houseHoldTbl.objects.values('validation_status').annotate(
            count=Count('id')
        )
        
        risk_counts = houseHoldTbl.objects.annotate(
            max_risk=Case(
                When(children__risk_assessment__risk_level='no_risk', then=Value('no_risk')),
                When(children__risk_assessment__risk_level='light_risk', then=Value('light_risk')),
                When(children__risk_assessment__risk_level='heavy_risk', then=Value('heavy_risk')),
                When(children__risk_assessment__risk_level='both_risk', then=Value('both_risk')),
                default=Value('unknown'),
                output_field=models.CharField()
            )
        ).values('max_risk').annotate(count=Count('id'))
        
        return JsonResponse({
            'success': True,
            'data': {
                'total_households': total_households,
                'validated_households': validated_households,
                'validation_rate': (validated_households / total_households * 100) if total_households > 0 else 0,
                'status_counts': {item['validation_status']: item['count'] for item in status_counts},
                'risk_counts': {item['max_risk']: item['count'] for item in risk_counts}
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching validation stats: {str(e)}'
        }, status=500)
    



########################################################################################################################################



# views.py - Add these audit views
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone
import json
from .models import (
    AuditCheck, AuditStatus, AuditType, AuditFinding, 
    AuditAttachment, houseHoldTbl, farmerTbl, ChildInHouseholdTbl, staffTbl
)

@method_decorator(login_required, name='dispatch')
class AuditChecksView(View):
    def get(self, request):
        return render(request, 'core/audit_checks.html')

@login_required
def get_audit_checks_data(request):
    try:
        # Get all audit checks with related data
        audits = AuditCheck.objects.select_related(
            'audit_type', 'status', 'household', 'farmer', 
            'child', 'assigned_to', 'created_by'
        ).all()
        
        data = []
        for audit in audits:
            data.append({
                'id': audit.id,
                'audit_id': audit.audit_id,
                'title': audit.title,
                'description': audit.description,
                'audit_type': audit.audit_type.name,
                'audit_type_id': audit.audit_type.id,
                'status': audit.status.name,
                'status_id': audit.status.id,
                'status_color': audit.status.color,
                'audit_method': audit.audit_method,
                'household_id': audit.household.id if audit.household else None,
                'household_code': audit.household.farmer.farmer_code if audit.household and audit.household.farmer else 'N/A',
                'farmer_id': audit.farmer.id if audit.farmer else None,
                'farmer_name': f"{audit.farmer.first_name} {audit.farmer.last_name}" if audit.farmer else 'N/A',
                'child_id': audit.child.id if audit.child else None,
                'child_name': f"{audit.child.child_first_name} {audit.child.child_surname}" if audit.child else 'N/A',
                'assigned_to': f"{audit.assigned_to.first_name} {audit.assigned_to.last_name}",
                'assigned_to_id': audit.assigned_to.id,
                'created_by': f"{audit.created_by.first_name} {audit.created_by.last_name}",
                'scheduled_date': audit.scheduled_date.strftime('%Y-%m-%d %H:%M:%S') if audit.scheduled_date else None,
                'completed_date': audit.completed_date.strftime('%Y-%m-%d %H:%M:%S') if audit.completed_date else None,
                'due_date': audit.due_date.strftime('%Y-%m-%d %H:%M:%S') if audit.due_date else None,
                'is_passed': audit.is_passed,
                'score': float(audit.score),
                'findings': audit.findings,
                'recommendations': audit.recommendations,
                'requires_follow_up': audit.requires_follow_up,
                'is_high_priority': audit.is_high_priority,
                'is_random_selection': audit.is_random_selection,
                'is_overdue': audit.is_overdue,
                'days_remaining': audit.days_remaining,
                'created_date': audit.created_date.strftime('%Y-%m-%d %H:%M:%S') if audit.created_date else None,
                'status_text': 'Active' if audit.delete_field == 'no' else 'Inactive'
            })
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading audit checks: {str(e)}'})

@login_required
def get_audit_check_details(request):
    try:
        audit_id = request.GET.get('audit_id')
        if not audit_id:
            return JsonResponse({'success': False, 'message': 'Audit ID is required'})
        
        audit = get_object_or_404(AuditCheck, id=audit_id)
        
        data = {
            'id': audit.id,
            'audit_id': audit.audit_id,
            'title': audit.title,
            'description': audit.description,
            'audit_type_id': audit.audit_type.id,
            'status_id': audit.status.id,
            'audit_method': audit.audit_method,
            'household_id': audit.household.id if audit.household else None,
            'farmer_id': audit.farmer.id if audit.farmer else None,
            'child_id': audit.child.id if audit.child else None,
            'assigned_to_id': audit.assigned_to.id,
            'scheduled_date': audit.scheduled_date.strftime('%Y-%m-%dT%H:%M') if audit.scheduled_date else None,
            'due_date': audit.due_date.strftime('%Y-%m-%dT%H:%M') if audit.due_date else None,
            'is_passed': audit.is_passed,
            'score': float(audit.score),
            'findings': audit.findings,
            'recommendations': audit.recommendations,
            'requires_follow_up': audit.requires_follow_up,
            'is_high_priority': audit.is_high_priority,
            'is_random_selection': audit.is_random_selection,
            'status_text': 'Active' if audit.delete_field == 'no' else 'Inactive'
        }
        
        return JsonResponse({'success': True, 'data': data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading audit details: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_audit_check(request):
    try:
        data = json.loads(request.body)
        
        # Validate required fields
        required_fields = ['title', 'audit_type_id', 'assigned_to_id', 'scheduled_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'})
        
        # Get current user
        current_user = request.user
        try:
            created_by = staffTbl.objects.get(user=current_user)
        except staffTbl.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Current user does not have a staff record'})
        
        # Validate foreign keys
        try:
            audit_type = AuditType.objects.get(id=data['audit_type_id'])
            assigned_to = staffTbl.objects.get(id=data['assigned_to_id'])
            status = AuditStatus.objects.get(name='Pending')  # Default status
        except (AuditType.DoesNotExist, staffTbl.DoesNotExist, AuditStatus.DoesNotExist) as e:
            return JsonResponse({'success': False, 'message': 'Invalid reference data'})
        
        # Validate related objects if provided
        household = None
        if data.get('household_id'):
            try:
                household = houseHoldTbl.objects.get(id=data['household_id'])
            except houseHoldTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Household not found'})
        
        farmer = None
        if data.get('farmer_id'):
            try:
                farmer = farmerTbl.objects.get(id=data['farmer_id'])
            except farmerTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Farmer not found'})
        
        child = None
        if data.get('child_id'):
            try:
                child = ChildInHouseholdTbl.objects.get(id=data['child_id'])
            except ChildInHouseholdTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Child not found'})
        
        # Create new audit check
        audit = AuditCheck(
            title=data['title'],
            description=data.get('description', ''),
            audit_type=audit_type,
            status=status,
            audit_method=data.get('audit_method', 'data_review'),
            household=household,
            farmer=farmer,
            child=child,
            assigned_to=assigned_to,
            created_by=created_by,
            scheduled_date=timezone.make_aware(timezone.datetime.fromisoformat(data['scheduled_date'].replace('Z', ''))),
            due_date=timezone.make_aware(timezone.datetime.fromisoformat(data['due_date'].replace('Z', ''))) if data.get('due_date') else None,
            is_passed=data.get('is_passed', False),
            score=data.get('score', 0),
            findings=data.get('findings', ''),
            recommendations=data.get('recommendations', ''),
            requires_follow_up=data.get('requires_follow_up', False),
            is_high_priority=data.get('is_high_priority', False),
            is_random_selection=data.get('is_random_selection', True)
        )
        audit.save()
        
        return JsonResponse({'success': True, 'message': 'Audit check created successfully', 'audit_id': audit.id})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error creating audit check: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def update_audit_check(request, audit_id):
    try:
        audit = get_object_or_404(AuditCheck, id=audit_id)
        data = json.loads(request.body)
        
        # Update basic fields
        if 'title' in data:
            audit.title = data['title']
        if 'description' in data:
            audit.description = data['description']
        if 'audit_method' in data:
            audit.audit_method = data['audit_method']
        if 'findings' in data:
            audit.findings = data['findings']
        if 'recommendations' in data:
            audit.recommendations = data['recommendations']
        if 'is_passed' in data:
            audit.is_passed = data['is_passed']
        if 'score' in data:
            audit.score = data['score']
        if 'requires_follow_up' in data:
            audit.requires_follow_up = data['requires_follow_up']
        if 'is_high_priority' in data:
            audit.is_high_priority = data['is_high_priority']
        if 'is_random_selection' in data:
            audit.is_random_selection = data['is_random_selection']
        
        # Update foreign keys
        if 'audit_type_id' in data and data['audit_type_id']:
            try:
                audit_type = AuditType.objects.get(id=data['audit_type_id'])
                audit.audit_type = audit_type
            except AuditType.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Audit type not found'})
        
        if 'status_id' in data and data['status_id']:
            try:
                status = AuditStatus.objects.get(id=data['status_id'])
                audit.status = status
                # If status is completed, set completed date
                if status.name == 'Completed' and not audit.completed_date:
                    audit.completed_date = timezone.now()
            except AuditStatus.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Status not found'})
        
        if 'assigned_to_id' in data and data['assigned_to_id']:
            try:
                assigned_to = staffTbl.objects.get(id=data['assigned_to_id'])
                audit.assigned_to = assigned_to
            except staffTbl.DoesNotExist:
                return JsonResponse({'success': False, 'message': 'Assigned staff not found'})
        
        # Update related objects
        if 'household_id' in data:
            if data['household_id']:
                try:
                    household = houseHoldTbl.objects.get(id=data['household_id'])
                    audit.household = household
                except houseHoldTbl.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Household not found'})
            else:
                audit.household = None
        
        if 'farmer_id' in data:
            if data['farmer_id']:
                try:
                    farmer = farmerTbl.objects.get(id=data['farmer_id'])
                    audit.farmer = farmer
                except farmerTbl.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Farmer not found'})
            else:
                audit.farmer = None
        
        if 'child_id' in data:
            if data['child_id']:
                try:
                    child = ChildInHouseholdTbl.objects.get(id=data['child_id'])
                    audit.child = child
                except ChildInHouseholdTbl.DoesNotExist:
                    return JsonResponse({'success': False, 'message': 'Child not found'})
            else:
                audit.child = None
        
        # Update dates
        if 'scheduled_date' in data and data['scheduled_date']:
            audit.scheduled_date = timezone.make_aware(timezone.datetime.fromisoformat(data['scheduled_date'].replace('Z', '')))
        
        if 'due_date' in data and data['due_date']:
            audit.due_date = timezone.make_aware(timezone.datetime.fromisoformat(data['due_date'].replace('Z', '')))
        
        # Update status
        if 'status_text' in data:
            audit.delete_field = 'yes' if data['status_text'] == 'Inactive' else 'no'
        
        audit.save()
        
        return JsonResponse({'success': True, 'message': 'Audit check updated successfully'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating audit check: {str(e)}'})

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def delete_audit_check(request, audit_id):
    try:
        audit = get_object_or_404(AuditCheck, id=audit_id)
        audit.delete()  # Soft delete
        return JsonResponse({'success': True, 'message': 'Audit check deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error deleting audit check: {str(e)}'})

@login_required
def get_audit_options_data(request):
    try:
        # Get audit types
        audit_types = AuditType.objects.all()
        audit_type_options = [{'id': at.id, 'name': at.name} for at in audit_types]
        
        # Get audit statuses
        audit_statuses = AuditStatus.objects.all()
        audit_status_options = [{'id': as_.id, 'name': as_.name, 'color': as_.color} for as_ in audit_statuses]
        
        # Get staff options
        staff_members = staffTbl.objects.filter(delete_field='no')
        staff_options = [{'id': s.id, 'name': f"{s.first_name} {s.last_name} ({s.staffid})"} for s in staff_members]
        
        # Get household options
        households = houseHoldTbl.objects.filter(delete_field='no').select_related('farmer')
        household_options = []
        for household in households:
            if household.farmer:
                household_options.append({
                    'id': household.id,
                    'name': f"{household.farmer.farmer_code} - {household.farmer.first_name} {household.farmer.last_name}"
                })
        
        # Get farmer options
        farmers = farmerTbl.objects.filter(delete_field='no')
        farmer_options = [{'id': f.id, 'name': f"{f.farmer_code} - {f.first_name} {f.last_name}"} for f in farmers]
        
        # Get child options
        children = ChildInHouseholdTbl.objects.filter(delete_field='no').select_related('houseHold__farmer')
        child_options = []
        for child in children:
            child_options.append({
                'id': child.id,
                'name': f"{child.child_first_name} {child.child_surname} - {child.houseHold.farmer.farmer_code if child.houseHold and child.houseHold.farmer else 'N/A'}"
            })
        
        # Audit methods
        audit_methods = [
            {'value': 'phone', 'label': 'Phone Call'},
            {'value': 'field_visit', 'label': 'Field Visit'},
            {'value': 'data_review', 'label': 'Data Review'},
            {'value': 'photo_verification', 'label': 'Photo Verification'},
            {'value': 'gps_verification', 'label': 'GPS Verification'},
        ]
        
        return JsonResponse({
            'success': True,
            'audit_types': audit_type_options,
            'audit_statuses': audit_status_options,
            'staff': staff_options,
            'households': household_options,
            'farmers': farmer_options,
            'children': child_options,
            'audit_methods': audit_methods
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error loading options: {str(e)}'})
    


##################################################################################################################

# quality_control/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.core.serializers.json import DjangoJSONEncoder
from datetime import datetime, timedelta

from .models import (
    ValidationRule, SurveyValidationResult, SurveyApproval,
    AuditCheck, HighRiskCase, houseHoldTbl, staffTbl, societyTbl, districtTbl
)

@login_required
def validate_data_view(request):
    """Render the Validate Submitted Data page"""
    return render(request, 'core/household-survey.html')

@login_required
def approve_surveys_view(request):
    """Render the Approve Surveys page"""
    return render(request, 'quality_control/approve_surveys.html')

@login_required
def audit_checks_view(request):
    """Render the Audit Checks page"""
    return render(request, 'quality_control/audit_checks.html')

@login_required
def spot_checks_view(request):
    """Render the High-Risk Cases page"""
    return render(request, 'quality_control/spot_checks.html')

@login_required
@require_http_methods(["GET"])
def household_surveys_list_api(request):
    """API endpoint to get household surveys for validation"""
    try:
        # Get filter parameters
        status = request.GET.get('status', '')
        enumerator_id = request.GET.get('enumerator', '')
        community_id = request.GET.get('community', '')
        district_id = request.GET.get('district', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Build query filters
        filters = {}
        
        # Status filter based on approval status
        if status:
            if status == 'pending_validation':
                filters['approval__status'] = 'pending'
            elif status == 'approved':
                filters['approval__status'] = 'approved'
            elif status == 'rejected':
                filters['approval__status'] = 'rejected'
            elif status == 'requires_correction':
                filters['approval__status'] = 'requires_correction'
            elif status == 'not_validated':
                filters['approval__isnull'] = True
        
        # Enumerator filter
        if enumerator_id:
            filters['enumerator_id'] = enumerator_id
        
        # Community filter
        if community_id:
            filters['farmer__society_name_id'] = community_id
        
        # District filter
        if district_id:
            communities_in_district = societyTbl.objects.filter(
                districtTbl_foreignkey_id=district_id
            ).values_list('id', flat=True)
            filters['farmer__society_name_id__in'] = list(communities_in_district)
        
        # Date range filter
        date_filters = Q()
        if date_from:
            date_filters &= Q(created_at__date__gte=date_from)
        if date_to:
            date_filters &= Q(created_at__date__lte=date_to)
        
        # Get household surveys with related data
        surveys = houseHoldTbl.objects.filter(
            **filters
        ).filter(date_filters).select_related(
            'enumerator',
            'enumerator__staffTbl_foreignkey',
            'farmer',
            'farmer__society_name',
            'farmer__society_name__districtTbl_foreignkey',
            'approval'
        ).prefetch_related(
            'validation_results',
            'validation_results__validation_rule'
        ).order_by('-created_at')
        
        # Prepare data for response
        data = []
        for survey in surveys:
            farmer = survey.farmer
            society = farmer.society_name if farmer else None
            district = society.districtTbl_foreignkey if society else None
            enumerator = survey.enumerator.staffTbl_foreignkey if survey.enumerator else None
            
            # Get validation status
            validation_results = survey.validation_results.all()
            passed_count = validation_results.filter(status='passed').count()
            failed_count = validation_results.filter(status='failed').count()
            pending_count = validation_results.filter(status='pending').count()
            
            # Get approval status
            approval_status = survey.approval.status if hasattr(survey, 'approval') else 'not_validated'
            
            data.append({
                'id': survey.id,
                'survey_id': f"SUR-{survey.id:04d}",
                'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'farmer_code': farmer.farmer_code if farmer else 'N/A',
                'community': society.society if society else 'N/A',
                'district': district.district if district else 'N/A',
                'enumerator': f"{enumerator.first_name} {enumerator.last_name}" if enumerator else 'N/A',
                'interview_date': survey.created_at.strftime('%Y-%m-%d'),
                'validation_status': {
                    'passed': passed_count,
                    'failed': failed_count,
                    'pending': pending_count,
                    'total': validation_results.count()
                },
                'approval_status': approval_status,
                'requires_correction': survey.approval.correction_required if hasattr(survey, 'approval') else False,
                'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # Get statistics
        total_surveys = houseHoldTbl.objects.count()
        pending_validation = houseHoldTbl.objects.filter(approval__status='pending').count()
        approved = houseHoldTbl.objects.filter(approval__status='approved').count()
        rejected = houseHoldTbl.objects.filter(approval__status='rejected').count()
        requires_correction = houseHoldTbl.objects.filter(approval__status='requires_correction').count()
        not_validated = houseHoldTbl.objects.filter(approval__isnull=True).count()
        
        statistics = {
            'total_surveys': total_surveys,
            'pending_validation': pending_validation,
            'approved': approved,
            'rejected': rejected,
            'requires_correction': requires_correction,
            'not_validated': not_validated
        }
        
        return JsonResponse({
            'success': True,
            'data': data,
            'statistics': statistics
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching household surveys: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def household_survey_detail_api(request, survey_id):
    """API endpoint to get detailed household survey information"""
    try:
        survey = get_object_or_404(houseHoldTbl, id=survey_id)
        farmer = survey.farmer
        society = farmer.society_name if farmer else None
        district = society.districtTbl_foreignkey if society else None
        enumerator = survey.enumerator.staffTbl_foreignkey if survey.enumerator else None
        
        # Get validation results
        validation_results = []
        for result in survey.validation_results.select_related('validation_rule').all():
            validation_results.append({
                'rule_name': result.validation_rule.name,
                'rule_type': result.validation_rule.get_rule_type_display(),
                'severity': result.validation_rule.get_severity_display(),
                'status': result.get_status_display(),
                'error_details': result.error_details,
                'validated_at': result.validated_at.strftime('%Y-%m-%d %H:%M') if result.validated_at else 'N/A',
                'validated_by': f"{result.validated_by.first_name} {result.validated_by.last_name}" if result.validated_by else 'N/A'
            })
        
        # Get approval information
        approval_info = {}
        if hasattr(survey, 'approval'):
            approval = survey.approval
            approval_info = {
                'status': approval.get_status_display(),
                'approved_by': f"{approval.approved_by.first_name} {approval.approved_by.last_name}" if approval.approved_by else 'N/A',
                'approved_at': approval.approved_at.strftime('%Y-%m-%d %H:%M') if approval.approved_at else 'N/A',
                'rejected_by': f"{approval.rejected_by.first_name} {approval.rejected_by.last_name}" if approval.rejected_by else 'N/A',
                'rejected_at': approval.rejected_at.strftime('%Y-%m-%d %H:%M') if approval.rejected_at else 'N/A',
                'rejection_reason': approval.rejection_reason,
                'comments': approval.comments,
                'correction_required': approval.correction_required,
                'correction_details': approval.correction_details,
                'correction_deadline': approval.correction_deadline.strftime('%Y-%m-%d') if approval.correction_deadline else 'N/A'
            }
        
        data = {
            'id': survey.id,
            'survey_id': f"SUR-{survey.id:04d}",
            'farmer': {
                'name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'code': farmer.farmer_code if farmer else 'N/A',
                'contact': farmer.contact if farmer else 'N/A'
            },
            'location': {
                'community': society.society if society else 'N/A',
                'district': district.district if district else 'N/A',
                'gps_point': survey.gps_point,
                'community_type': survey.get_community_type_display() if survey.community_type else 'N/A'
            },
            'enumerator': {
                'name': f"{enumerator.first_name} {enumerator.last_name}" if enumerator else 'N/A',
                'staff_id': enumerator.staffid if enumerator else 'N/A'
            },
            'interview_info': {
                'start_time': survey.interview_start_time.strftime('%Y-%m-%d %H:%M') if survey.interview_start_time else 'N/A',
                'end_time': survey.end_time.strftime('%Y-%m-%d %H:%M') if survey.end_time else 'N/A',
                'farmer_available': survey.get_farmer_available_display() if survey.farmer_available else 'N/A',
                'reason_unavailable': survey.get_reason_unavailable_display() if survey.reason_unavailable else 'N/A'
            },
            'household_composition': {
                'total_adults': survey.total_adults,
                'num_children': survey.num_children_5_to_17,
                'children_present': survey.get_children_present_display() if survey.children_present else 'N/A'
            },
            'validation_results': validation_results,
            'approval_info': approval_info,
            'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M'),
            'updated_at': survey.updated_at.strftime('%Y-%m-%d %H:%M') if survey.updated_at else 'N/A'
        }
        
        return JsonResponse({
            'success': True,
            'data': data
        })
        
    except houseHoldTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Household survey not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching survey details: {str(e)}'
        }, status=500)

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def validate_household_survey_api(request, survey_id):
    """API endpoint to validate a household survey"""
    try:
        survey = get_object_or_404(houseHoldTbl, id=survey_id)
        data = json.loads(request.body)
        
        # Get current user
        current_user = request.user.stafftbl
        
        with transaction.atomic():
            # Run validation rules
            validation_rules = ValidationRule.objects.filter(is_active=True)
            results = []
            
            for rule in validation_rules:
                # Here you would implement the actual validation logic
                # For now, we'll simulate validation
                is_valid = simulate_validation(rule, survey)
                
                result, created = SurveyValidationResult.objects.get_or_create(
                    household_survey=survey,
                    validation_rule=rule,
                    defaults={
                        'status': 'passed' if is_valid else 'failed',
                        'error_details': '' if is_valid else f"Validation failed for rule: {rule.name}",
                        'validated_by': current_user,
                        'validated_at': timezone.now()
                    }
                )
                
                if not created:
                    result.status = 'passed' if is_valid else 'failed'
                    result.error_details = '' if is_valid else f"Validation failed for rule: {rule.name}"
                    result.validated_by = current_user
                    result.validated_at = timezone.now()
                    result.save()
                
                results.append({
                    'rule': rule.name,
                    'passed': is_valid,
                    'message': result.error_details
                })
            
            # Update approval status
            approval, created = SurveyApproval.objects.get_or_create(
                household_survey=survey,
                defaults={'status': 'pending'}
            )
            
            # Check if all validations passed
            all_passed = all(result['passed'] for result in results)
            if all_passed:
                approval.status = 'approved'
                approval.approved_by = current_user
                approval.approved_at = timezone.now()
                approval.comments = data.get('comments', '')
            else:
                approval.status = 'requires_correction'
                approval.correction_required = True
                approval.correction_details = "Some validation rules failed. Please review and correct."
                approval.correction_deadline = timezone.now() + timedelta(days=7)
            
            approval.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Survey validation completed successfully',
            'data': {
                'survey_id': survey.id,
                'all_passed': all_passed,
                'results': results,
                'approval_status': approval.status
            }
        })
        
    except houseHoldTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Household survey not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error validating survey: {str(e)}'
        }, status=500)

def simulate_validation(rule, survey):
    """
    Simulate validation logic - in a real implementation, this would evaluate
    the validation_expression against the survey data
    """
    # Simple simulation - 80% pass rate for demonstration
    import random
    return random.random() > 0.2

@login_required
@csrf_exempt
@require_http_methods(["POST"])
def reject_household_survey_api(request, survey_id):
    """API endpoint to reject a household survey"""
    try:
        survey = get_object_or_404(houseHoldTbl, id=survey_id)
        data = json.loads(request.body)
        
        # Get current user
        current_user = request.user.stafftbl
        
        with transaction.atomic():
            # Update approval status to rejected
            approval, created = SurveyApproval.objects.get_or_create(
                household_survey=survey,
                defaults={'status': 'rejected'}
            )
            
            if not created:
                approval.status = 'rejected'
            
            approval.rejected_by = current_user
            approval.rejected_at = timezone.now()
            approval.rejection_reason = data.get('rejection_reason', '')
            approval.comments = data.get('comments', '')
            approval.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Survey rejected successfully',
            'data': {
                'survey_id': survey.id,
                'status': approval.status
            }
        })
        
    except houseHoldTbl.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': 'Household survey not found'
        }, status=404)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error rejecting survey: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_validation_rules_api(request):
    """API endpoint to get all validation rules"""
    try:
        rules = ValidationRule.objects.filter(is_active=True).values(
            'id', 'name', 'description', 'rule_type', 'severity', 
            'field_name', 'error_message'
        )
        return JsonResponse(list(rules), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching validation rules: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_enumerators_api(request):
    """API endpoint to get all enumerators"""
    try:
        enumerators = staffTbl.objects.filter(
            designation__name__icontains='enumerator'
        ).values('id', 'first_name', 'last_name', 'staffid')
        return JsonResponse(list(enumerators), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching enumerators: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_communities_api(request):
    """API endpoint to get all communities"""
    try:
        communities = societyTbl.objects.all().values('id', 'society')
        return JsonResponse(list(communities), safe=False)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Error fetching communities: {str(e)}'
        }, status=500)
    




###################################################################################################################################

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Case, When, Value, IntegerField
from django.core.serializers.json import DjangoJSONEncoder
import json

@login_required
def map_overview_view(request):
    """Render the Map Overview page"""
    return render(request, 'portal/map_overview.html')

# views.py
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Case, When, Value, IntegerField, F, FloatField
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
import json
from decimal import Decimal
from datetime import datetime, timedelta
import math

@login_required
def map_overview_view(request):
    """Render the Map Overview page"""
    return render(request, 'core/map.html')

@login_required
@require_http_methods(["GET"])
def get_survey_locations_api(request):
    """API endpoint to get survey locations for mapping"""
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        enumerator_id = request.GET.get('enumerator', '')
        district_id = request.GET.get('district', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        risk_level = request.GET.get('risk_level', '')
        quality_filter = request.GET.get('quality', '')

        print(status_filter, enumerator_id, district_id, date_from, date_to, risk_level, quality_filter)
        
        # Build query filters
        filters = Q()
        
        # Status filter
        if status_filter:
            if status_filter == 'approved':
                filters &= Q(approval__status='approved')
            elif status_filter == 'rejected':
                filters &= Q(approval__status='rejected')
            elif status_filter == 'pending':
                filters &= Q(approval__status='pending')
            elif status_filter == 'requires_correction':
                filters &= Q(approval__status='requires_correction')
        
        # Enumerator filter
        if enumerator_id:
            filters &= Q(enumerator_id=enumerator_id)
        
        # District filter
        if district_id:
            communities_in_district = societyTbl.objects.filter(
                districtTbl_foreignkey_id=district_id
            ).values_list('id', flat=True)
            filters &= Q(farmer__society_name_id__in=list(communities_in_district))
        
        # Date range filter
        if date_from:
            filters &= Q(created_at__date__gte=date_from)
        if date_to:
            filters &= Q(created_at__date__lte=date_to)
        
        # Risk level filter
        if risk_level:
            filters &= Q(children__risk_assessment__risk_level=risk_level)
        
        # Quality filter
        if quality_filter:
            # Calculate quality score based on validation results
            if quality_filter == 'high':
                filters &= Q(validation_results__status='passed') & \
                         Q(validation_results__count__gte=8)  # At least 80% passed
            elif quality_filter == 'medium':
                filters &= Q(validation_results__status='passed') & \
                         Q(validation_results__count__gte=5) & \
                         Q(validation_results__count__lte=7)  # 50-70% passed
            elif quality_filter == 'low':
                filters &= Q(validation_results__status='passed') & \
                         Q(validation_results__count__lte=4)  # Less than 50% passed
        
        # Get household surveys with coordinates
        surveys = houseHoldTbl.objects.filter(filters).filter(
            Q(latitude__isnull=False) & Q(longitude__isnull=False) &
            ~Q(latitude='') & ~Q(longitude='')
        ).select_related(
            'enumerator__staffTbl_foreignkey',
            'farmer',
            'farmer__society_name',
            'farmer__society_name__districtTbl_foreignkey',
            'approval'
        ).prefetch_related(
            'children',
            'children__risk_assessment',
            'validation_results'
        ).distinct()
        
        # Prepare data for response
        data = []
        for survey in surveys:
            farmer = survey.farmer
            society = farmer.society_name if farmer else None
            district = society.districtTbl_foreignkey if society else None
            enumerator = survey.enumerator.staffTbl_foreignkey if survey.enumerator else None
            
            # Get risk levels from children
            risk_levels = []
            for child in survey.children.all():
                if hasattr(child, 'risk_assessment'):
                    risk_levels.append(child.risk_assessment.risk_level)
            
            # Determine overall risk level
            overall_risk = 'no_risk'
            if 'both_risk' in risk_levels:
                overall_risk = 'both_risk'
            elif 'heavy_risk' in risk_levels:
                overall_risk = 'heavy_risk'
            elif 'light_risk' in risk_levels:
                overall_risk = 'light_risk'
            
            # Get validation status
            validation_results = survey.validation_results.all()
            passed_count = validation_results.filter(status='passed').count()
            failed_count = validation_results.filter(status='failed').count()
            total_count = validation_results.count()
            
            data.append({
                'id': survey.id,
                'survey_id': f"SUR-{survey.id:04d}",
                'latitude': float(survey.latitude),
                'longitude': float(survey.longitude),
                'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'farmer_code': farmer.farmer_code if farmer else 'N/A',
                'community': society.society if society else 'N/A',
                'district': district.district if district else 'N/A',
                'enumerator': f"{enumerator.first_name} {enumerator.last_name}" if enumerator else 'N/A',
                'interview_date': survey.created_at.strftime('%Y-%m-%d'),
                'risk_level': overall_risk,
                'validation_status': {
                    'passed': passed_count,
                    'failed': failed_count,
                    'total': total_count
                },
                'approval_status': survey.approval.status if hasattr(survey, 'approval') else 'not_validated',
                'total_children': survey.children.count(),
                'total_adults': survey.total_adults,
                'gps_accuracy': survey.gps_point if survey.gps_point else 'N/A',
                'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # Get statistics for the map
        total_surveys = surveys.count()
        surveys_with_coords = houseHoldTbl.objects.filter(
            Q(latitude__isnull=False) & Q(longitude__isnull=False) &
            ~Q(latitude='') & ~Q(longitude='')
        ).count()
        
        # Risk level statistics
        risk_stats = {
            'no_risk': houseHoldTbl.objects.filter(
                children__risk_assessment__risk_level='no_risk'
            ).distinct().count(),
            'light_risk': houseHoldTbl.objects.filter(
                children__risk_assessment__risk_level='light_risk'
            ).distinct().count(),
            'heavy_risk': houseHoldTbl.objects.filter(
                children__risk_assessment__risk_level='heavy_risk'
            ).distinct().count(),
            'both_risk': houseHoldTbl.objects.filter(
                children__risk_assessment__risk_level='both_risk'
            ).distinct().count()
        }
        print(data)
        
        return JsonResponse({
            'success': True,
            'data': data,
            'statistics': {
                'total_surveys': total_surveys,
                'surveys_with_coords': surveys_with_coords,
                'coverage_percentage': (surveys_with_coords / houseHoldTbl.objects.count() * 100) if houseHoldTbl.objects.count() > 0 else 0,
                'risk_stats': risk_stats
            }
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        print(e)
        return JsonResponse({
            'success': False,
            'message': f'Error fetching survey locations: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_survey_details_api(request, survey_id):
    """API endpoint to get detailed survey information"""
    try:
        # Get the survey
        survey = houseHoldTbl.objects.filter(id=survey_id).first()
        
        if not survey:
            return JsonResponse({
                'success': False,
                'message': 'Survey not found'
            }, status=404)
        
        farmer = survey.farmer
        society = farmer.society_name if farmer else None
        district = society.districtTbl_foreignkey if society else None
        enumerator = survey.enumerator.staffTbl_foreignkey if survey.enumerator else None
        
        # Get risk levels from children
        risk_levels = []
        children_data = []
        
        for child in survey.children.all():
            child_risk = 'no_risk'
            if hasattr(child, 'risk_assessment'):
                child_risk = child.risk_assessment.risk_level
                risk_levels.append(child_risk)
            
            # Get tasks performed by child
            tasks_performed = []
            if hasattr(child, 'light_tasks'):
                tasks_performed.extend([task.task.name for task in child.light_tasks.all()])
            if hasattr(child, 'heavy_tasks'):
                tasks_performed.extend([task.task.name for task in child.heavy_tasks.all()])
            
            children_data.append({
                'first_name': child.child_first_name,
                'last_name': child.child_surname,
                'birth_year': child.child_year_birth,
                'gender': child.child_gender,
                'education_status': child.education_level if hasattr(child, 'education_level') else 'Unknown',
                'risk_level': child_risk,
                'tasks_performed': tasks_performed
            })
        
        # Determine overall risk level
        overall_risk = 'no_risk'
        if 'both_risk' in risk_levels:
            overall_risk = 'both_risk'
        elif 'heavy_risk' in risk_levels:
            overall_risk = 'heavy_risk'
        elif 'light_risk' in risk_levels:
            overall_risk = 'light_risk'
        
        # Get validation status and issues
        validation_results = survey.validation_results.all()
        passed_count = validation_results.filter(status='passed').count()
        failed_count = validation_results.filter(status='failed').count()
        total_count = validation_results.count()
        
        validation_issues = []
        for result in validation_results.filter(status='failed'):
            validation_issues.append({
                'rule_name': result.validation_rule.name if hasattr(result, 'validation_rule') else 'Unknown Rule',
                'severity': result.validation_rule.severity if hasattr(result, 'validation_rule') else 'medium',
                'description': result.error_details or 'Validation failed',
                'field_name': result.validation_rule.field_name if hasattr(result, 'validation_rule') else 'Unknown'
            })
        
        # Get community type
        community_type = survey.community_type if hasattr(survey, 'community_type') else 'Unknown'
        
        response_data = {
            'id': survey.id,
            'survey_id': f"SUR-{survey.id:04d}",
            'latitude': float(survey.latitude),
            'longitude': float(survey.longitude),
            'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
            'farmer_code': farmer.farmer_code if farmer else 'N/A',
            'community': society.society if society else 'N/A',
            'district': district.district if district else 'N/A',
            'enumerator': f"{enumerator.first_name} {enumerator.last_name}" if enumerator else 'N/A',
            'interview_date': survey.created_at.strftime('%Y-%m-%d'),
            'risk_level': overall_risk,
            'validation_status': {
                'passed': passed_count,
                'failed': failed_count,
                'total': total_count
            },
            'approval_status': survey.approval.status if hasattr(survey, 'approval') else 'not_validated',
            'total_children': survey.children.count(),
            'total_adults': survey.total_adults,
            'gps_accuracy': survey.gps_point if survey.gps_point else 'N/A',
            'community_type': community_type,
            'nationality': survey.nationality if hasattr(survey, 'nationality') else 'N/A',
            'country_origin': survey.country_origin if hasattr(survey, 'country_origin') else 'N/A',
            'children': children_data,
            'validation_issues': validation_issues,
            'created_at': survey.created_at.strftime('%Y-%m-%d %H:%M')
        }
        
        return JsonResponse({
            'success': True,
            'data': response_data
        }, encoder=DjangoJSONEncoder)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching survey details: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_enumerators_api(request):
    """API endpoint to get all enumerators"""
    try:
        enumerators = staffTbl.objects.filter(
            designation__name__icontains='enumerator'
        ).values('id', 'first_name', 'last_name', 'staffid')
        
        print(enumerators)
        return JsonResponse({
            'success': True,
            'data': list(enumerators)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching enumerators: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def get_districts_api(request):
    """API endpoint to get all districts"""
    try:
        districts = districtTbl.objects.all().values('id', 'district')
        print(districts)
        
        return JsonResponse({
            'success': True,
            'data': list(districts)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching districts: {str(e)}'
        }, status=500)
    


# @login_required
# @require_http_methods(["GET"])
# def get_enumerator_tracking_api(request, enumerator_id):
#     """API endpoint to get enumerator tracking data"""
#     try:
#         # Get enumerator
#         enumerator = staffTbl.objects.filter(id=enumerator_id).first()
#         if not enumerator:
#             return JsonResponse({
#                 'success': False,
#                 'message': 'Enumerator not found'
#             }, status=404)
        
#         # Get date range from request
#         date_from = request.GET.get('date_from')
#         date_to = request.GET.get('date_to')
        
#         # Build date filters
#         date_filters = Q()
#         if date_from:
#             date_filters &= Q(created_at__date__gte=date_from)
#         if date_to:
#             date_filters &= Q(created_at__date__lte=date_to)
        
#         # Get surveys conducted by this enumerator
#         surveys = houseHoldTbl.objects.filter(
#             enumerator__staffTbl_foreignkey=enumerator, date_filters).filter(Q(latitude__isnull=False) & Q(longitude__isnull=False) & ~Q(latitude='') & ~Q(longitude='')).order_by('created_at')
        
#         # Prepare tracking data
#         locations = []
#         survey_data = []
#         total_distance = 0
#         previous_location = None
        
#         for survey in surveys:
#             location = {
#                 'latitude': float(survey.latitude),
#                 'longitude': float(survey.longitude),
#                 'timestamp': survey.created_at.isoformat(),
#                 'survey_id': f"SUR-{survey.id:04d}"
#             }
#             locations.append(location)
            
#             # Calculate distance if we have a previous location
#             if previous_location:
#                 distance = calculate_distance(
#                     previous_location['latitude'], previous_location['longitude'],
#                     location['latitude'], location['longitude']
#                 )
#                 total_distance += distance
            
#             previous_location = location
            
#             # Add survey data
#             farmer = survey.farmer
#             survey_data.append({
#                 'survey_id': f"SUR-{survey.id:04d}",
#                 'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
#                 'interview_date': survey.created_at.strftime('%Y-%m-%d'),
#                 'approval_status': survey.approval.status if hasattr(survey, 'approval') else 'not_validated',
#                 'latitude': float(survey.latitude),
#                 'longitude': float(survey.longitude)
#             })
        
#         # If no date range provided, default to last 7 days
#         if not date_from:
#             date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
#         if not date_to:
#             date_to = datetime.now().strftime('%Y-%m-%d')
        
#         return JsonResponse({
#             'success': True,
#             'data': {
#                 'enumerator': {
#                     'id': enumerator.id,
#                     'name': f"{enumerator.first_name} {enumerator.last_name}",
#                     'staffid': enumerator.staffid
#                 },
#                 'date_from': date_from,
#                 'date_to': date_to,
#                 'locations': locations,
#                 'surveys': survey_data,
#                 'survey_count': len(surveys),
#                 'distance_km': round(total_distance, 2)
#             }
#         })
        
#     except Exception as e:
#         return JsonResponse({
#             'success': False,
#             'message': f'Error fetching enumerator tracking data: {str(e)}'
#         }, status=500)





@login_required
@require_http_methods(["GET"])
def get_enumerator_tracking_api(request, enumerator_id):
    """API endpoint to get enumerator tracking data"""
    try:
        # Get enumerator
        enumerator = staffTbl.objects.filter(id=enumerator_id).first()
        if not enumerator:
            return JsonResponse({
                'success': False,
                'message': 'Enumerator not found'
            }, status=404)
        
        # Get date range from request
        date_from = request.GET.get('date_from')
        date_to = request.GET.get('date_to')
        
        # Build date filters correctly
        date_filters = Q()
        if date_from:
            date_filters &= Q(created_at__date__gte=date_from)
        if date_to:
            date_filters &= Q(created_at__date__lte=date_to)
        
        # Get surveys conducted by this enumerator - FIXED QUERY
        # We need to go through districtStaffTbl to get the correct relationship
        surveys = houseHoldTbl.objects.filter(
            Q(enumerator__staffTbl_foreignkey_id=enumerator_id) & date_filters
        ).filter(
            Q(latitude__isnull=False) & 
            Q(longitude__isnull=False) & 
            ~Q(latitude='') & 
            ~Q(longitude='')
        ).order_by('created_at')
        
        # Prepare tracking data
        locations = []
        survey_data = []
        total_distance = 0
        previous_location = None
        
        for survey in surveys:
            try:
                location = {
                    'latitude': float(survey.latitude),
                    'longitude': float(survey.longitude),
                    'timestamp': survey.created_at.isoformat(),
                    'survey_id': f"SUR-{survey.id:04d}"
                }
                locations.append(location)
                
                # Calculate distance if we have a previous location
                if previous_location:
                    distance = calculate_distance(
                        previous_location['latitude'], previous_location['longitude'],
                        location['latitude'], location['longitude']
                    )
                    total_distance += distance
                
                previous_location = location
                
                # Add survey data
                farmer = survey.farmer
                survey_data.append({
                    'survey_id': f"SUR-{survey.id:04d}",
                    'farmer_name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                    'interview_date': survey.created_at.strftime('%Y-%m-%d'),
                    'approval_status': survey.approval.status if hasattr(survey, 'approval') else 'not_validated',
                    'latitude': float(survey.latitude),
                    'longitude': float(survey.longitude)
                })
            except (ValueError, TypeError):
                continue
        
        # If no date range provided, default to last 7 days
        if not date_from:
            date_from = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        if not date_to:
            date_to = datetime.now().strftime('%Y-%m-%d')
        
        return JsonResponse({
            'success': True,
            'data': {
                'enumerator': {
                    'id': enumerator.id,
                    'name': f"{enumerator.first_name} {enumerator.last_name}",
                    'staffid': enumerator.staffid
                },
                'date_from': date_from,
                'date_to': date_to,
                'locations': locations,
                'surveys': survey_data,
                'survey_count': len(surveys),
                'distance_km': round(total_distance, 2)
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error fetching enumerator tracking data: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_map_clusters_api(request):
    """API endpoint to get clustered data for map visualization"""
    try:
        # Get all surveys with coordinates
        surveys = houseHoldTbl.objects.filter(
            Q(latitude__isnull=False) & Q(longitude__isnull=False) &
            ~Q(latitude='') & ~Q(longitude='')
        )
        
        # Simple clustering by rounding coordinates
        clusters = []
        cluster_precision = 0.01  # Approximately 1km
        
        for survey in surveys:
            try:
                lat = float(survey.latitude)
                lon = float(survey.longitude)
                
                # Round coordinates to create clusters
                cluster_lat = round(lat / cluster_precision) * cluster_precision
                cluster_lon = round(lon / cluster_precision) * cluster_precision
                
                # Find or create cluster
                cluster = next((c for c in clusters if c['lat'] == cluster_lat and c['lon'] == cluster_lon), None)
                
                if not cluster:
                    cluster = {
                        'lat': cluster_lat,
                        'lon': cluster_lon,
                        'count': 0,
                        'risk_levels': {'no_risk': 0, 'light_risk': 0, 'heavy_risk': 0, 'both_risk': 0},
                        'surveys': []
                    }
                    clusters.append(cluster)
                
                cluster['count'] += 1
                
                # Add risk level information
                for child in survey.children.all():
                    if hasattr(child, 'risk_assessment'):
                        risk_level = child.risk_assessment.risk_level
                        if risk_level in cluster['risk_levels']:
                            cluster['risk_levels'][risk_level] += 1
                
                cluster['surveys'].append(survey.id)
                
            except (ValueError, TypeError):
                continue
        
        return JsonResponse({
            'success': True,
            'clusters': clusters,
            'cluster_precision': cluster_precision
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error generating map clusters: {str(e)}'
        }, status=500)

@login_required
@require_http_methods(["GET"])
def export_map_data_api(request):
    """API endpoint to export map data"""
    try:
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        enumerator_id = request.GET.get('enumerator', '')
        district_id = request.GET.get('district', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        risk_level = request.GET.get('risk_level', '')
        
        # Build query filters (same as get_survey_locations_api)
        filters = Q()
        
        if status_filter:
            if status_filter == 'approved':
                filters &= Q(approval__status='approved')
            elif status_filter == 'rejected':
                filters &= Q(approval__status='rejected')
            elif status_filter == 'pending':
                filters &= Q(approval__status='pending')
            elif status_filter == 'requires_correction':
                filters &= Q(approval__status='requires_correction')
        
        if enumerator_id:
            filters &= Q(enumerator_id=enumerator_id)
        
        if district_id:
            communities_in_district = societyTbl.objects.filter(
                districtTbl_foreignkey_id=district_id
            ).values_list('id', flat=True)
            filters &= Q(farmer__society_name_id__in=list(communities_in_district))
        
        if date_from:
            filters &= Q(created_at__date__gte=date_from)
        if date_to:
            filters &= Q(created_at__date__lte=date_to)
        
        if risk_level:
            filters &= Q(children__risk_assessment__risk_level=risk_level)
        
        # Get surveys with coordinates
        surveys = houseHoldTbl.objects.filter(filters).filter(
            Q(latitude__isnull=False) & Q(longitude__isnull=False) &
            ~Q(latitude='') & ~Q(longitude='')
        ).select_related(
            'enumerator__staffTbl_foreignkey',
            'farmer',
            'farmer__society_name',
            'farmer__society_name__districtTbl_foreignkey',
            'approval'
        ).prefetch_related(
            'children',
            'children__risk_assessment',
            'validation_results'
        ).distinct()
        
        # Prepare data for export
        export_data = []
        for survey in surveys:
            farmer = survey.farmer
            society = farmer.society_name if farmer else None
            district = society.districtTbl_foreignkey if society else None
            enumerator = survey.enumerator.staffTbl_foreignkey if survey.enumerator else None
            
            # Get risk levels from children
            risk_levels = []
            for child in survey.children.all():
                if hasattr(child, 'risk_assessment'):
                    risk_levels.append(child.risk_assessment.risk_level)
            
            # Determine overall risk level
            overall_risk = 'no_risk'
            if 'both_risk' in risk_levels:
                overall_risk = 'both_risk'
            elif 'heavy_risk' in risk_levels:
                overall_risk = 'heavy_risk'
            elif 'light_risk' in risk_levels:
                overall_risk = 'light_risk'
            
            # Get validation status
            validation_results = survey.validation_results.all()
            passed_count = validation_results.filter(status='passed').count()
            failed_count = validation_results.filter(status='failed').count()
            
            export_data.append({
                'Survey ID': f"SUR-{survey.id:04d}",
                'Latitude': float(survey.latitude),
                'Longitude': float(survey.longitude),
                'Farmer Name': f"{farmer.first_name} {farmer.last_name}" if farmer else 'N/A',
                'Farmer Code': farmer.farmer_code if farmer else 'N/A',
                'Community': society.society if society else 'N/A',
                'District': district.district if district else 'N/A',
                'Enumerator': f"{enumerator.first_name} {enumerator.last_name}" if enumerator else 'N/A',
                'Interview Date': survey.created_at.strftime('%Y-%m-%d'),
                'Risk Level': overall_risk,
                'Validation Passed': passed_count,
                'Validation Failed': failed_count,
                'Total Children': survey.children.count(),
                'Total Adults': survey.total_adults,
                'GPS Accuracy': survey.gps_point if survey.gps_point else 'N/A',
                'Approval Status': survey.approval.status if hasattr(survey, 'approval') else 'not_validated'
            })
        
        return JsonResponse({
            'success': True,
            'data': export_data,
            'filename': f'survey_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error exporting map data: {str(e)}'
        }, status=500)

# Utility functions
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


