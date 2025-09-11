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
        
        # Prepare education data
        education_data = {
            'is_enrolled': child.child_educated == 1,
            'school_name': child.child_school_name,
            'school_type': child.school_type,
            'grade': child.child_grade,
            'school_attendance': child.child_school_7days,
            'basic_needs': child.basic_need_available.split(',') if child.basic_need_available else [],
            'assessment': {
                'calculation': child.calculation_response,
                'reading': child.reading_response,
                'writing': child.writing_response
            }
        }
        
        # Prepare work data
        work_data = {
            'house_work': child.work_in_house == 'yes',
            'cocoa_work': child.work_on_cocoa == 'yes',
            'work_frequency': child.work_frequency,
            'tasks_performed': child.performed_tasks.split(',') if child.performed_tasks else [],
            'supervision': child.under_supervision if hasattr(child, 'under_supervision') else 'no'
        }
        
        # Prepare health data
        health_data = {
            'injuries': child.suffered_injury == 'yes',
            'injury_cause': child.wound_cause,
            'injury_time': child.wound_time,
            'frequent_pains': child.child_often_pains == 'yes',
            'health_help': child.help_child_health.split(',') if child.help_child_health else []
        }
        
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
            'birth_certificate_reason': child.child_birth_certificate_reason,
            
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
            'health': health_data,
            
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