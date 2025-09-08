import json
from datetime import datetime

import requests
from django.core.exceptions import ValidationError
from django.core.files.storage import default_storage
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from .models import (
    Cover_tbl,
    FarmerChild,
    ConsentLocation_tbl,
    FarmerIdentification_OwnerIdentificationTbl,
    FarmerIdentification_Info_OnVisit_tbl,
    WorkersInTheFarmTbl,
    AdultInHouseholdTbl,
    ChildHouseholdDetailsTbl,
    AdultHouseholdMember,
    ChildrenInHouseholdTbl,
    ChildInHouseholdTbl,
    ChildEducationDetailsTbl,
    ChildRemediationTbl,
    HouseholdSensitizationTbl,
    EndOfCollection,
)


###########################################################################################
# COVER QUESTIONNAIRE VIEWS
###########################################################################################
@csrf_exempt
def cover_view(request, cover_id=None):
    """Handles CRUD operations for Cover_tbl model"""
    if request.method == "GET":
        if cover_id:
            cover = get_object_or_404(Cover_tbl, id=cover_id)
            data = {
                "id": cover.id,
                "enumerator_name": cover.enumerator_name,
                "enumerator_code": cover.enumerator_code,
                "farmer_code": cover.farmer_code,
                "society_code": cover.society_code,
                "farmer_surname": cover.farmer_surname,
                "farmer_first_name": cover.farmer_first_name,
                "country": cover.country,
                "region": cover.region,
                "district": cover.district,
                "risk_classification": cover.risk_classification,
                "client": cover.client,
                "num_farmer_children": cover.num_farmer_children
            }
            return JsonResponse(data, status=200)
        else:
            covers = Cover_tbl.objects.all().values()
            return JsonResponse(list(covers), safe=False, status=200)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            cover = Cover_tbl.objects.create(
                enumerator_name=data["enumerator_name"],
                enumerator_code=data.get("enumerator_code", ""),
                farmer_code=data["farmer_code"],
                society_code=data.get("society_code", ""),
                farmer_surname=data.get("farmer_surname", ""),
                farmer_first_name=data.get("farmer_first_name", ""),
                country=data.get("country", ""),
                region=data.get("region", ""),
                district=data.get("district", ""),
                risk_classification=data.get("risk_classification", ""),
                client=data.get("client", ""),
                num_farmer_children=data.get("num_farmer_children", 0),
            )
            return JsonResponse({"message": "Cover created", "id": cover.id}, status=201)
        except (KeyError, json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "PUT":
        if not cover_id:
            return JsonResponse({"error": "Cover ID is required for update"}, status=400)
        
        cover = get_object_or_404(Cover_tbl, id=cover_id)
        try:
            data = json.loads(request.body)
            for field, value in data.items():
                setattr(cover, field, value)
            cover.save()
            return JsonResponse({"message": "Cover updated successfully"}, status=200)
        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "DELETE":
        if not cover_id:
            return JsonResponse({"error": "Cover ID is required for deletion"}, status=400)

        cover = get_object_or_404(Cover_tbl, id=cover_id)
        cover.delete()
        return JsonResponse({"message": "Cover deleted successfully"}, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)


@csrf_exempt
def farmer_child_view(request, child_id=None):
    """Handles CRUD operations for FarmerChild model"""
    if request.method == "GET":
        if child_id:
            child = get_object_or_404(FarmerChild, id=child_id)
            data = {
                "id": child.id,
                "cover": child.cover.id,
                "name": child.name,
                "age": child.age,
                "gender": child.gender
            }
            return JsonResponse(data, status=200)
        else:
            children = FarmerChild.objects.all().values()
            return JsonResponse(list(children), safe=False, status=200)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            cover = get_object_or_404(Cover_tbl, id=data["cover"])
            child = FarmerChild.objects.create(
                cover=cover,
                name=data["name"],
                age=data["age"],
                gender=data["gender"]
            )
            return JsonResponse({"message": "Child created", "id": child.id}, status=201)
        except (KeyError, json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "PUT":
        if not child_id:
            return JsonResponse({"error": "Child ID is required for update"}, status=400)
        
        child = get_object_or_404(FarmerChild, id=child_id)
        try:
            data = json.loads(request.body)
            for field, value in data.items():
                setattr(child, field, value)
            child.save()
            return JsonResponse({"message": "Child updated successfully"}, status=200)
        except (json.JSONDecodeError, ValidationError) as e:
            return JsonResponse({"error": str(e)}, status=400)

    elif request.method == "DELETE":
        if not child_id:
            return JsonResponse({"error": "Child ID is required for deletion"}, status=400)

        child = get_object_or_404(FarmerChild, id=child_id)
        child.delete()
        return JsonResponse({"message": "Child deleted successfully"}, status=200)

    return JsonResponse({"error": "Method not allowed"}, status=405)



###########################################################################################
# CONSENT AND LOCATION MODEL
###########################################################################################

class ConsentLocationView(View):
    def get(self, request, consent_id=None):
        if consent_id:
            consent = get_object_or_404(ConsentLocation_tbl, id=consent_id)
            data = {
                "id": consent.id,
                "interview_start_time": consent.interview_start_time,
                "gps_point": consent.gps_point,
                "community_type": consent.community_type,
                "farmer_resides_in_community": consent.farmer_resides_in_community,
                "community_name": consent.community_name,
                "farmer_community": consent.farmer_community,
                "farmer_available": consent.farmer_available,
                "reason_unavailable": consent.reason_unavailable,
                "reason_unavailable_other": consent.reason_unavailable_other,
                "available_answer_by": consent.available_answer_by,
                "refusal_toa_participate_reason_survey": consent.refusal_toa_participate_reason_survey,
            }
            return JsonResponse(data)
        else:
            consents = ConsentLocation_tbl.objects.all().values()
            return JsonResponse(list(consents), safe=False)

    def post(self, request):
        try:
            data = request.POST
            cover = get_object_or_404(Cover_tbl, id=data.get("cover_id"))
            consent = ConsentLocation_tbl.objects.create(
                cover=cover,
                interview_start_time=parse_datetime(data.get("interview_start_time")),
                gps_point=data.get("gps_point"),
                community_type=data.get("community_type"),
                farmer_resides_in_community=data.get("farmer_resides_in_community"),
                community_name=data.get("community_name", ""),
                farmer_community=data.get("farmer_community", ""),
                farmer_available=data.get("farmer_available"),
                reason_unavailable=data.get("reason_unavailable", ""),
                reason_unavailable_other=data.get("reason_unavailable_other", ""),
                available_answer_by=data.get("available_answer_by", ""),
                refusal_toa_participate_reason_survey=data.get("refusal_toa_participate_reason_survey", ""),
            )
            return JsonResponse({"message": "Consent location created successfully", "id": consent.id})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, consent_id):
        try:
            consent = get_object_or_404(ConsentLocation_tbl, id=consent_id)
            data = request.POST
            consent.interview_start_time = parse_datetime(data.get("interview_start_time", consent.interview_start_time))
            consent.gps_point = data.get("gps_point", consent.gps_point)
            consent.community_type = data.get("community_type", consent.community_type)
            consent.farmer_resides_in_community = data.get("farmer_resides_in_community", consent.farmer_resides_in_community)
            consent.community_name = data.get("community_name", consent.community_name)
            consent.farmer_community = data.get("farmer_community", consent.farmer_community)
            consent.farmer_available = data.get("farmer_available", consent.farmer_available)
            consent.reason_unavailable = data.get("reason_unavailable", consent.reason_unavailable)
            consent.reason_unavailable_other = data.get("reason_unavailable_other", consent.reason_unavailable_other)
            consent.available_answer_by = data.get("available_answer_by", consent.available_answer_by)
            consent.refusal_toa_participate_reason_survey = data.get("refusal_toa_participate_reason_survey", consent.refusal_toa_participate_reason_survey)
            consent.save()
            return JsonResponse({"message": "Consent location updated successfully"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, consent_id):
        consent = get_object_or_404(ConsentLocation_tbl, id=consent_id)
        consent.delete()
        return JsonResponse({"message": "Consent location deleted successfully"})



#################################################################################
#FARMER IDENTIFICATION - INFORMATION ON THE VISIT
#################################################################################

@csrf_exempt
def farmer_identification_view(request, pk=None):
    if request.method == "GET":
        if pk:
            farmer_identification = get_object_or_404(FarmerIdentification_Info_OnVisit_tbl, pk=pk)
            data = {
                "id": farmer_identification.id,
                "is_name_correct": farmer_identification.is_name_correct,
                "exact_name": farmer_identification.exact_name,
                "nationality": farmer_identification.nationality,
                "country_origin": farmer_identification.country_origin,
                "country_origin_other": farmer_identification.country_origin_other,
                "is_owner": farmer_identification.is_owner,
                "owner_status_01": farmer_identification.owner_status_01,
                "owner_status_00": farmer_identification.owner_status_00,
            }
            return JsonResponse(data, status=200)
        else:
            farmers = FarmerIdentification_Info_OnVisit_tbl.objects.all().values()
            return JsonResponse(list(farmers), safe=False, status=200)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            farmer_identification = FarmerIdentification_Info_OnVisit_tbl.objects.create(
                is_name_correct=data.get("is_name_correct"),
                exact_name=data.get("exact_name", ""),
                nationality=data.get("nationality"),
                country_origin=data.get("country_origin", ""),
                country_origin_other=data.get("country_origin_other", ""),
                is_owner=data.get("is_owner"),
                owner_status_01=data.get("owner_status_01", ""),
                owner_status_00=data.get("owner_status_00", ""),
            )
            return JsonResponse({"message": "Farmer Identification record created successfully!", "id": farmer_identification.id}, status=201)
        except IntegrityError:
            return JsonResponse({"error": "Duplicate entry or database error"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    elif request.method == "PUT":
        if not pk:
            return JsonResponse({"error": "Missing ID for update"}, status=400)
        try:
            farmer_identification = get_object_or_404(FarmerIdentification_Info_OnVisit_tbl, pk=pk)
            data = json.loads(request.body)
            farmer_identification.is_name_correct = data.get("is_name_correct", farmer_identification.is_name_correct)
            farmer_identification.exact_name = data.get("exact_name", farmer_identification.exact_name)
            farmer_identification.nationality = data.get("nationality", farmer_identification.nationality)
            farmer_identification.country_origin = data.get("country_origin", farmer_identification.country_origin)
            farmer_identification.country_origin_other = data.get("country_origin_other", farmer_identification.country_origin_other)
            farmer_identification.is_owner = data.get("is_owner", farmer_identification.is_owner)
            farmer_identification.owner_status_01 = data.get("owner_status_01", farmer_identification.owner_status_01)
            farmer_identification.owner_status_00 = data.get("owner_status_00", farmer_identification.owner_status_00)
            farmer_identification.save()
            return JsonResponse({"message": "Farmer Identification record updated successfully!"}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    elif request.method == "DELETE":
        if not pk:
            return JsonResponse({"error": "Missing ID for deletion"}, status=400)
        farmer_identification = get_object_or_404(FarmerIdentification_Info_OnVisit_tbl, pk=pk)
        farmer_identification.delete()
        return JsonResponse({"message": "Farmer Identification record deleted successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


#################################################################################
#OWNER IDENTIFICATION
#################################################################################


@csrf_exempt
def owner_identification_view(request, pk=None):
    if request.method == "GET":
        if pk:
            owner_identification = get_object_or_404(FarmerIdentification_OwnerIdentificationTbl, pk=pk)
            data = {
                "id": owner_identification.id,
                "owner_identification": owner_identification.owner_identification.id if owner_identification.owner_identification else None,
                "name_owner": owner_identification.name_owner,
                "first_name_owner": owner_identification.first_name_owner,
                "nationality_owner": owner_identification.nationality_owner,
                "country_origin_owner": owner_identification.country_origin_owner,
                "country_origin_owner_other": owner_identification.country_origin_owner_other,
                "manager_work_length": owner_identification.manager_work_length,
            }
            return JsonResponse(data, status=200)
        else:
            owners = FarmerIdentification_OwnerIdentificationTbl.objects.all().values()
            return JsonResponse(list(owners), safe=False, status=200)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            owner_identification = FarmerIdentification_OwnerIdentificationTbl.objects.create(
                owner_identification=FarmerIdentification_Info_OnVisit_tbl.objects.get(id=data.get("owner_identification")) if data.get("owner_identification") else None,
                name_owner=data.get("name_owner", ""),
                first_name_owner=data.get("first_name_owner", ""),
                nationality_owner=data.get("nationality_owner"),
                country_origin_owner=data.get("country_origin_owner", ""),
                country_origin_owner_other=data.get("country_origin_owner_other", ""),
                manager_work_length=data.get("manager_work_length", 0),
            )
            return JsonResponse({"message": "Owner Identification record created successfully!", "id": owner_identification.id}, status=201)
        except FarmerIdentification_Info_OnVisit_tbl.DoesNotExist:
            return JsonResponse({"error": "Invalid owner_identification ID"}, status=400)
        except IntegrityError:
            return JsonResponse({"error": "Duplicate entry or database error"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    elif request.method == "PUT":
        if not pk:
            return JsonResponse({"error": "Missing ID for update"}, status=400)
        try:
            owner_identification = get_object_or_404(FarmerIdentification_OwnerIdentificationTbl, pk=pk)
            data = json.loads(request.body)
            if data.get("owner_identification"):
                owner_identification.owner_identification = FarmerIdentification_Info_OnVisit_tbl.objects.get(id=data.get("owner_identification"))
            owner_identification.name_owner = data.get("name_owner", owner_identification.name_owner)
            owner_identification.first_name_owner = data.get("first_name_owner", owner_identification.first_name_owner)
            owner_identification.nationality_owner = data.get("nationality_owner", owner_identification.nationality_owner)
            owner_identification.country_origin_owner = data.get("country_origin_owner", owner_identification.country_origin_owner)
            owner_identification.country_origin_owner_other = data.get("country_origin_owner_other", owner_identification.country_origin_owner_other)
            owner_identification.manager_work_length = data.get("manager_work_length", owner_identification.manager_work_length)
            owner_identification.save()
            return JsonResponse({"message": "Owner Identification record updated successfully!"}, status=200)
        except FarmerIdentification_Info_OnVisit_tbl.DoesNotExist:
            return JsonResponse({"error": "Invalid owner_identification ID"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    elif request.method == "DELETE":
        if not pk:
            return JsonResponse({"error": "Missing ID for deletion"}, status=400)
        owner_identification = get_object_or_404(FarmerIdentification_OwnerIdentificationTbl, pk=pk)
        owner_identification.delete()
        return JsonResponse({"message": "Owner Identification record deleted successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)

 ##################################################################################
    # WORKERS IN THE FARM
##################################################################################

@csrf_exempt
def workers_in_farm_view(request, pk=None):
    if request.method == "GET":
        if pk:
            worker = get_object_or_404(WorkersInTheFarmTbl, pk=pk)
            data = {
                "id": worker.id,
                "workers_in_farm": worker.workers_in_farm.id if worker.workers_in_farm else None,
                "recruited_workers": worker.recruited_workers,
                "worker_recruitment_type": worker.worker_recruitment_type,
                "worker_agreement_type": worker.worker_agreement_type,
                "worker_agreement_other": worker.worker_agreement_other,
                "tasks_clarified": worker.tasks_clarified,
                "additional_tasks": worker.additional_tasks,
                "refusal_action": worker.refusal_action,
                "refusal_action_other": worker.refusal_action_other,
                "salary_status": worker.salary_status,
                "recruit_1": worker.recruit_1,
                "recruit_2": worker.recruit_2,
                "recruit_3": worker.recruit_3,
                "conditions_1": worker.conditions_1,
                "conditions_2": worker.conditions_2,
                "conditions_3": worker.conditions_3,
                "conditions_4": worker.conditions_4,
                "conditions_5": worker.conditions_5,
                "leaving_1": worker.leaving_1,
                "leaving_2": worker.leaving_2,
                "consent_recruitment": worker.consent_recruitment,
            }
            return JsonResponse(data, status=200)
        else:
            workers = WorkersInTheFarmTbl.objects.all().values()
            return JsonResponse(list(workers), safe=False, status=200)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            worker = WorkersInTheFarmTbl.objects.create(
                workers_in_farm=FarmerIdentification_Info_OnVisit_tbl.objects.get(id=data.get("workers_in_farm")) if data.get("workers_in_farm") else None,
                recruited_workers=data.get("recruited_workers"),
                worker_recruitment_type=data.get("worker_recruitment_type"),
                worker_agreement_type=data.get("worker_agreement_type"),
                worker_agreement_other=data.get("worker_agreement_other", ""),
                tasks_clarified=data.get("tasks_clarified"),
                additional_tasks=data.get("additional_tasks"),
                refusal_action=data.get("refusal_action"),
                refusal_action_other=data.get("refusal_action_other", ""),
                salary_status=data.get("salary_status"),
                recruit_1=data.get("recruit_1"),
                recruit_2=data.get("recruit_2"),
                recruit_3=data.get("recruit_3"),
                conditions_1=data.get("conditions_1"),
                conditions_2=data.get("conditions_2"),
                conditions_3=data.get("conditions_3"),
                conditions_4=data.get("conditions_4"),
                conditions_5=data.get("conditions_5"),
                leaving_1=data.get("leaving_1"),
                leaving_2=data.get("leaving_2"),
                consent_recruitment=data.get("consent_recruitment"),
            )
            return JsonResponse({"message": "Worker record created successfully!", "id": worker.id}, status=201)
        except FarmerIdentification_Info_OnVisit_tbl.DoesNotExist:
            return JsonResponse({"error": "Invalid workers_in_farm ID"}, status=400)
        except IntegrityError:
            return JsonResponse({"error": "Duplicate entry or database error"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    elif request.method == "PUT":
        if not pk:
            return JsonResponse({"error": "Missing ID for update"}, status=400)
        try:
            worker = get_object_or_404(WorkersInTheFarmTbl, pk=pk)
            data = json.loads(request.body)
            if data.get("workers_in_farm"):
                worker.workers_in_farm = FarmerIdentification_Info_OnVisit_tbl.objects.get(id=data.get("workers_in_farm"))
            for field in data:
                if hasattr(worker, field):
                    setattr(worker, field, data[field])
            worker.save()
            return JsonResponse({"message": "Worker record updated successfully!"}, status=200)
        except FarmerIdentification_Info_OnVisit_tbl.DoesNotExist:
            return JsonResponse({"error": "Invalid workers_in_farm ID"}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

    elif request.method == "DELETE":
        if not pk:
            return JsonResponse({"error": "Missing ID for deletion"}, status=400)
        worker = get_object_or_404(WorkersInTheFarmTbl, pk=pk)
        worker.delete()
        return JsonResponse({"message": "Worker record deleted successfully!"}, status=200)

    return JsonResponse({"error": "Invalid request method"}, status=405)


#########################################################################################
    # ADULT OF THE RESPONDENTS HOUSEHOLD - INFORMATION ON THE ADULTS LIVING IN THE HOUSEHOLD
#########################################################################################

@csrf_exempt
def adult_in_household_view(request, id=None):
    if request.method == 'GET':
        if id:
            # Retrieve a single record
            adult = get_object_or_404(AdultInHouseholdTbl, id=id)
            data = {
                'id': adult.id,
                'consent_id': adult.consent.id if adult.consent else None,
                'total_adults': adult.total_adults,
            }
        else:
            # Retrieve all records
            adults = AdultInHouseholdTbl.objects.all().values('id', 'consent_id', 'total_adults')
            data = list(adults)
        return JsonResponse({'data': data}, status=200)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            consent_id = body.get('consent_id')
            total_adults = body.get('total_adults')

            if not consent_id or not total_adults:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            consent = get_object_or_404(ConsentLocation_tbl, id=consent_id)

            adult = AdultInHouseholdTbl.objects.create(
                consent=consent,
                total_adults=total_adults
            )

            return JsonResponse({'message': 'Record created successfully', 'id': adult.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'PUT':
        if not id:
            return JsonResponse({'error': 'ID is required for update'}, status=400)

        adult = get_object_or_404(AdultInHouseholdTbl, id=id)
        
        try:
            body = json.loads(request.body)
            consent_id = body.get('consent_id')
            total_adults = body.get('total_adults')

            if consent_id:
                adult.consent = get_object_or_404(ConsentLocation_tbl, id=consent_id)
            if total_adults:
                adult.total_adults = total_adults

            adult.save()

            return JsonResponse({'message': 'Record updated successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'DELETE':
        if not id:
            return JsonResponse({'error': 'ID is required for deletion'}, status=400)

        adult = get_object_or_404(AdultInHouseholdTbl, id=id)
        adult.delete()
        return JsonResponse({'message': 'Record deleted successfully'}, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



@csrf_exempt
def adult_household_member_view(request, id=None):
    if request.method == 'GET':
        if id:
            # Retrieve a single record
            member = get_object_or_404(AdultHouseholdMember, id=id)
            data = {
                'id': member.id,
                'household_id': member.household.id,
                'full_name': member.full_name,
                'relationship': member.relationship,
                'relationship_other': member.relationship_other,
                'gender': member.gender,
                'nationality': member.nationality,
                'country_origin': member.country_origin,
                'country_origin_other': member.country_origin_other,
                'year_birth': member.year_birth,
                'birth_certificate': member.birth_certificate,
                'main_work': member.main_work,
                'main_work_other': member.main_work_other,
            }
        else:
            # Retrieve all records
            members = AdultHouseholdMember.objects.all().values(
                'id', 'household_id', 'full_name', 'relationship', 'relationship_other',
                'gender', 'nationality', 'country_origin', 'country_origin_other',
                'year_birth', 'birth_certificate', 'main_work', 'main_work_other'
            )
            data = list(members)
        return JsonResponse({'data': data}, status=200)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            household_id = body.get('household_id')
            full_name = body.get('full_name')
            relationship = body.get('relationship')
            relationship_other = body.get('relationship_other', '')
            gender = body.get('gender')
            nationality = body.get('nationality')
            country_origin = body.get('country_origin', '')
            country_origin_other = body.get('country_origin_other', '')
            year_birth = body.get('year_birth')
            birth_certificate = body.get('birth_certificate')
            main_work = body.get('main_work')
            main_work_other = body.get('main_work_other', '')

            if not household_id or not full_name or not relationship or not gender or not nationality or not year_birth or not birth_certificate or not main_work:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            if year_birth < 1900 or year_birth > datetime.now().year:
                return JsonResponse({'error': 'Invalid year of birth'}, status=400)

            household = get_object_or_404(AdultInHouseholdTbl, id=household_id)

            member = AdultHouseholdMember.objects.create(
                household=household,
                full_name=full_name,
                relationship=relationship,
                relationship_other=relationship_other,
                gender=gender,
                nationality=nationality,
                country_origin=country_origin,
                country_origin_other=country_origin_other,
                year_birth=year_birth,
                birth_certificate=birth_certificate,
                main_work=main_work,
                main_work_other=main_work_other
            )

            return JsonResponse({'message': 'Record created successfully', 'id': member.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'PUT':
        if not id:
            return JsonResponse({'error': 'ID is required for update'}, status=400)

        member = get_object_or_404(AdultHouseholdMember, id=id)
        
        try:
            body = json.loads(request.body)
            household_id = body.get('household_id')
            full_name = body.get('full_name')
            relationship = body.get('relationship')
            relationship_other = body.get('relationship_other', '')
            gender = body.get('gender')
            nationality = body.get('nationality')
            country_origin = body.get('country_origin', '')
            country_origin_other = body.get('country_origin_other', '')
            year_birth = body.get('year_birth')
            birth_certificate = body.get('birth_certificate')
            main_work = body.get('main_work')
            main_work_other = body.get('main_work_other', '')

            if household_id:
                member.household = get_object_or_404(AdultInHouseholdTbl, id=household_id)
            if full_name:
                member.full_name = full_name
            if relationship:
                member.relationship = relationship
            if relationship_other:
                member.relationship_other = relationship_other
            if gender:
                member.gender = gender
            if nationality:
                member.nationality = nationality
            if country_origin:
                member.country_origin = country_origin
            if country_origin_other:
                member.country_origin_other = country_origin_other
            if year_birth:
                if year_birth < 1900 or year_birth > datetime.now().year:
                    return JsonResponse({'error': 'Invalid year of birth'}, status=400)
                member.year_birth = year_birth
            if birth_certificate:
                member.birth_certificate = birth_certificate
            if main_work:
                member.main_work = main_work
            if main_work_other:
                member.main_work_other = main_work_other

            member.save()

            return JsonResponse({'message': 'Record updated successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'DELETE':
        if not id:
            return JsonResponse({'error': 'ID is required for deletion'}, status=400)

        member = get_object_or_404(AdultHouseholdMember, id=id)
        member.delete()
        return JsonResponse({'message': 'Record deleted successfully'}, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



#################################################################################
# CHILDREN IN THE RESPONDENT'S HOUSEHOLD MODEL
#################################################################################

@csrf_exempt
def children_in_household_view(request, id=None):
    if request.method == 'GET':
        if id:
            # Retrieve a single record
            child_household = get_object_or_404(ChildrenInHouseholdTbl, id=id)
            data = {
                'id': child_household.id,
                'consent_id': child_household.consent.id if child_household.consent else None,
                'children_present': child_household.children_present,
                'num_children_5_to_17': child_household.num_children_5_to_17,
            }
        else:
            # Retrieve all records
            child_households = ChildrenInHouseholdTbl.objects.all().values(
                'id', 'consent_id', 'children_present', 'num_children_5_to_17'
            )
            data = list(child_households)
        return JsonResponse({'data': data}, status=200)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            consent_id = body.get('consent_id')
            children_present = body.get('children_present')
            num_children_5_to_17 = body.get('num_children_5_to_17')

            if children_present is None or num_children_5_to_17 is None:
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            if not (1 <= num_children_5_to_17 <= 19):
                return JsonResponse({'error': 'Number of children must be between 1 and 19'}, status=400)

            consent = get_object_or_404(ConsentLocation_tbl, id=consent_id) if consent_id else None

            child_household = ChildrenInHouseholdTbl.objects.create(
                consent=consent,
                children_present=children_present,
                num_children_5_to_17=num_children_5_to_17
            )

            return JsonResponse({'message': 'Record created successfully', 'id': child_household.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'PUT':
        if not id:
            return JsonResponse({'error': 'ID is required for update'}, status=400)

        child_household = get_object_or_404(ChildrenInHouseholdTbl, id=id)

        try:
            body = json.loads(request.body)
            consent_id = body.get('consent_id')
            children_present = body.get('children_present')
            num_children_5_to_17 = body.get('num_children_5_to_17')

            if consent_id:
                child_household.consent = get_object_or_404(ConsentLocation_tbl, id=consent_id)
            if children_present:
                child_household.children_present = children_present
            if num_children_5_to_17 is not None:
                if not (1 <= num_children_5_to_17 <= 19):
                    return JsonResponse({'error': 'Number of children must be between 1 and 19'}, status=400)
                child_household.num_children_5_to_17 = num_children_5_to_17

            child_household.save()

            return JsonResponse({'message': 'Record updated successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not id:
            return JsonResponse({'error': 'ID is required for deletion'}, status=400)

        child_household = get_object_or_404(ChildrenInHouseholdTbl, id=id)
        child_household.delete()
        return JsonResponse({'message': 'Record deleted successfully'}, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def child_in_household_view(request, id=None):
    if request.method == 'GET':
        if id:
            # Retrieve a single record
            child = get_object_or_404(ChildInHouseholdTbl, id=id)
            data = {
                'id': child.id,
                'household_id': child.household.id,
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
            }
        else:
            # Retrieve all records
            children = ChildInHouseholdTbl.objects.all().values(
                'id', 'household_id', 'child_declared_in_cover', 'child_identifier',
                'child_can_be_surveyed', 'child_unavailability_reason', 'child_not_avail',
                'who_answers_child_unavailable', 'who_answers_child_unavailable_other',
                'child_first_name', 'child_surname', 'child_gender', 'child_year_birth',
                'child_birth_certificate', 'child_birth_certificate_reason'
            )
            data = list(children)
        return JsonResponse({'data': data}, status=200)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            household_id = body.get('household_id')
            child_declared_in_cover = body.get('child_declared_in_cover')
            child_identifier = body.get('child_identifier')
            child_can_be_surveyed = body.get('child_can_be_surveyed')
            child_unavailability_reason = body.get('child_unavailability_reason', '')
            child_not_avail = body.get('child_not_avail', '')
            who_answers_child_unavailable = body.get('who_answers_child_unavailable', '')
            who_answers_child_unavailable_other = body.get('who_answers_child_unavailable_other', '')
            child_first_name = body.get('child_first_name')
            child_surname = body.get('child_surname')
            child_gender = body.get('child_gender')
            child_year_birth = body.get('child_year_birth')
            child_birth_certificate = body.get('child_birth_certificate')
            child_birth_certificate_reason = body.get('child_birth_certificate_reason', '')

            if not all([household_id, child_declared_in_cover, child_identifier, child_can_be_surveyed, 
                        child_first_name, child_surname, child_gender, child_year_birth, child_birth_certificate]):
                return JsonResponse({'error': 'Missing required fields'}, status=400)

            if not (1 <= child_identifier <= 19):
                return JsonResponse({'error': 'Child identifier must be between 1 and 19'}, status=400)

            if not (2007 <= child_year_birth <= 2020):
                return JsonResponse({'error': 'Year of birth must be between 2007 and 2020'}, status=400)

            household = get_object_or_404(ChildrenInHouseholdTbl, id=household_id)

            child = ChildInHouseholdTbl.objects.create(
                household=household,
                child_declared_in_cover=child_declared_in_cover,
                child_identifier=child_identifier,
                child_can_be_surveyed=child_can_be_surveyed,
                child_unavailability_reason=child_unavailability_reason,
                child_not_avail=child_not_avail,
                who_answers_child_unavailable=who_answers_child_unavailable,
                who_answers_child_unavailable_other=who_answers_child_unavailable_other,
                child_first_name=child_first_name,
                child_surname=child_surname,
                child_gender=child_gender,
                child_year_birth=child_year_birth,
                child_birth_certificate=child_birth_certificate,
                child_birth_certificate_reason=child_birth_certificate_reason
            )

            return JsonResponse({'message': 'Record created successfully', 'id': child.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'PUT':
        if not id:
            return JsonResponse({'error': 'ID is required for update'}, status=400)

        child = get_object_or_404(ChildInHouseholdTbl, id=id)

        try:
            body = json.loads(request.body)

            household_id = body.get('household_id')
            if household_id:
                child.household = get_object_or_404(ChildrenInHouseholdTbl, id=household_id)

            child.child_declared_in_cover = body.get('child_declared_in_cover', child.child_declared_in_cover)
            child.child_identifier = body.get('child_identifier', child.child_identifier)
            child.child_can_be_surveyed = body.get('child_can_be_surveyed', child.child_can_be_surveyed)
            child.child_unavailability_reason = body.get('child_unavailability_reason', child.child_unavailability_reason)
            child.child_not_avail = body.get('child_not_avail', child.child_not_avail)
            child.who_answers_child_unavailable = body.get('who_answers_child_unavailable', child.who_answers_child_unavailable)
            child.who_answers_child_unavailable_other = body.get('who_answers_child_unavailable_other', child.who_answers_child_unavailable_other)
            child.child_first_name = body.get('child_first_name', child.child_first_name)
            child.child_surname = body.get('child_surname', child.child_surname)
            child.child_gender = body.get('child_gender', child.child_gender)
            child.child_year_birth = body.get('child_year_birth', child.child_year_birth)
            child.child_birth_certificate = body.get('child_birth_certificate', child.child_birth_certificate)
            child.child_birth_certificate_reason = body.get('child_birth_certificate_reason', child.child_birth_certificate_reason)

            if not (1 <= child.child_identifier <= 19):
                return JsonResponse({'error': 'Child identifier must be between 1 and 19'}, status=400)

            if not (2007 <= child.child_year_birth <= 2020):
                return JsonResponse({'error': 'Year of birth must be between 2007 and 2020'}, status=400)

            child.save()
            return JsonResponse({'message': 'Record updated successfully'}, status=200)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        if not id:
            return JsonResponse({'error': 'ID is required for deletion'}, status=400)

        child = get_object_or_404(ChildInHouseholdTbl, id=id)
        child.delete()
        return JsonResponse({'message': 'Record deleted successfully'}, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



############################################
# ChildHouseholdDetails Model
############################################

@csrf_exempt
def child_household_details(request, id=None):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            child = ChildHouseholdDetailsTbl.objects.create(
                child_in_household_id=data.get("child_in_household"),
                child_born_in_community=data.get("child_born_in_community"),
                child_country_of_birth=data.get("child_country_of_birth", ""),
                child_country_of_birth_other=data.get("child_country_of_birth_other", ""),
                child_relationship_to_head=data.get("child_relationship_to_head"),
                child_relationship_to_head_other=data.get("child_relationship_to_head_other", ""),
                child_not_live_with_family_reason=data.get("child_not_live_with_family_reason", ""),
                child_not_live_with_family_reason_other=data.get("child_not_live_with_family_reason_other", ""),
                child_decision_maker=data.get("child_decision_maker"),
                child_decision_maker_other=data.get("child_decision_maker_other", ""),
                child_agree_with_decision=data.get("child_agree_with_decision"),
                child_seen_parents=data.get("child_seen_parents"),
                child_last_seen_parent=data.get("child_last_seen_parent"),
                child_living_duration=data.get("child_living_duration"),
                child_accompanied_by=data.get("child_accompanied_by"),
                child_accompanied_by_other=data.get("child_accompanied_by_other", ""),
            )
            return JsonResponse({"message": "Child household details created successfully", "id": child.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    elif request.method == "GET":
        if id:
            child = get_object_or_404(ChildHouseholdDetailsTbl, id=id)
            data = {
                "id": child.id,
                "child_in_household": child.child_in_household_id,
                "child_born_in_community": child.child_born_in_community,
                "child_country_of_birth": child.child_country_of_birth,
                "child_country_of_birth_other": child.child_country_of_birth_other,
                "child_relationship_to_head": child.child_relationship_to_head,
                "child_relationship_to_head_other": child.child_relationship_to_head_other,
                "child_not_live_with_family_reason": child.child_not_live_with_family_reason,
                "child_not_live_with_family_reason_other": child.child_not_live_with_family_reason_other,
                "child_decision_maker": child.child_decision_maker,
                "child_decision_maker_other": child.child_decision_maker_other,
                "child_agree_with_decision": child.child_agree_with_decision,
                "child_seen_parents": child.child_seen_parents,
                "child_last_seen_parent": child.child_last_seen_parent,
                "child_living_duration": child.child_living_duration,
                "child_accompanied_by": child.child_accompanied_by,
                "child_accompanied_by_other": child.child_accompanied_by_other,
            }
            return JsonResponse(data, status=200)
        
        else:
            children = ChildHouseholdDetailsTbl.objects.all().values()
            return JsonResponse(list(children), safe=False, status=200)
    
    elif request.method == "PUT":
        child = get_object_or_404(ChildHouseholdDetailsTbl, id=id)
        try:
            data = json.loads(request.body)
            for field, value in data.items():
                setattr(child, field, value)
            child.save()
            return JsonResponse({"message": "Child household details updated successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    elif request.method == "DELETE":
        child = get_object_or_404(ChildHouseholdDetailsTbl, id=id)
        child.delete()
        return JsonResponse({"message": "Child household details deleted successfully"}, status=200)
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


############################################
# ChildEducationDetails Model   
############################################


class ChildEducationDetailsView(View):
    def get(self, request, *args, **kwargs):
        """Retrieve all records or a specific record if an ID is provided."""
        child_id = kwargs.get('id')
        if child_id:
            child = get_object_or_404(ChildEducationDetailsTbl, id=child_id)
            return JsonResponse(self.serialize_child(child), safe=False)
        
        children = ChildEducationDetailsTbl.objects.all()
        children_data = [self.serialize_child(child) for child in children]
        return JsonResponse(children_data, safe=False)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """Create a new record."""
        try:
            data = json.loads(request.body)
            child = ChildEducationDetailsTbl.objects.create(**data)
            return JsonResponse({'message': 'Child record created', 'id': child.id}, status=201)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        """Update an existing record."""
        child_id = kwargs.get('id')
        if not child_id:
            return JsonResponse({'error': 'ID is required for update'}, status=400)
        
        child = get_object_or_404(ChildEducationDetailsTbl, id=child_id)
        try:
            data = json.loads(request.body)
            for key, value in data.items():
                setattr(child, key, value)
            child.save()
            return JsonResponse({'message': 'Child record updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    @csrf_exempt
    def delete(self, request, *args, **kwargs):
        """Delete a record."""
        child_id = kwargs.get('id')
        if not child_id:
            return JsonResponse({'error': 'ID is required for deletion'}, status=400)
        
        child = get_object_or_404(ChildEducationDetailsTbl, id=child_id)
        child.delete()
        return JsonResponse({'message': 'Child record deleted'}, status=204)

    def serialize_child(self, child):
        """Helper function to serialize the child object."""
        return {
            'id': child.id,
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

            # Light Work Fields
            'total_hours_light_work_school': child.total_hours_light_work_school,
            'total_hours_light_work_non_school': child.total_hours_light_work_non_school,
            'under_supervision': child.under_supervision,
            'performed_tasks_12months': child.performed_tasks_12months,
            'remuneration_received_12months': child.remuneration_received_12months,
            'light_duty_duration_school_12': child.light_duty_duration_school_12,
            'light_duty_duration_non_school_12': child.light_duty_duration_non_school_12,
            'task_location_12': child.task_location_12,
            'task_location_other_12': child.task_location_other_12,
            'total_hours_light_work_school_12': child.total_hours_light_work_school_12,
            'total_hours_light_work_non_school_12': child.total_hours_light_work_non_school_12,
            'under_supervision_12': child.under_supervision_12,
            'tasks_done_in_7days': child.tasks_done_in_7days,

            # Heavy Work Fields
            'salary_received': child.salary_received,
            'task_location': child.task_location,
            'task_location_other': child.task_location_other,
            'longest_time_school_day': child.longest_time_school_day,
            'longest_time_non_school_day': child.longest_time_non_school_day,
            'total_hours_school_days': child.total_hours_school_days,
            'total_hours_non_school_days': child.total_hours_non_school_days,
            'under_supervision': child.under_supervision,
            'heavy_tasks_12months': child.heavy_tasks_12months,
            'salary_received_12': child.salary_received_12,
            'task_location_12': child.task_location_12,
            'task_location_other_12': child.task_location_other_12,
            'child_work_who': child.child_work_who,
            'child_work_who_other': child.child_work_who_other,
            'child_work_why': child.child_work_why,
            'child_work_why_other': child.child_work_why_other,

            # Health & Safety Fields
            'agrochemicals_applied': child.agrochemicals_applied,
            'child_on_farm_during_agro': child.child_on_farm_during_agro,
            'suffered_injury': child.suffered_injury,
            'wound_cause': child.wound_cause,
            'wound_cause_other': child.wound_cause_other,
            'wound_time': child.wound_time,
            'child_often_pains': child.child_often_pains,
            'help_child_health': child.help_child_health,
            'help_child_health_other': child.help_child_health_other,
            'child_photo': child.child_photo.url if child.child_photo else None,  # Handle image field properly
        }

####################################################################################################
# Child Remediation Assessment
####################################################################################################

@method_decorator(csrf_exempt, name='dispatch')
class ChildRemediationView(View):
    
    def get(self, request, remediation_id=None):
        if remediation_id:
            remediation = get_object_or_404(ChildRemediationTbl, id=remediation_id)
            data = {
                "id": remediation.id,
                "consent": remediation.consent.id if remediation.consent else None,
                "school_fees_owed": remediation.school_fees_owed,
                "parent_remediation": remediation.parent_remediation,
                "parent_remediation_other": remediation.parent_remediation_other,
                "community_remediation": remediation.community_remediation,
                "community_remediation_other": remediation.community_remediation_other,
            }
            return JsonResponse(data, status=200)
        
        all_remediations = ChildRemediationTbl.objects.all().values()
        return JsonResponse(list(all_remediations), safe=False, status=200)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            remediation = ChildRemediationTbl.objects.create(
                consent_id=data.get("consent"),
                school_fees_owed=data.get("school_fees_owed"),
                parent_remediation=data.get("parent_remediation"),
                parent_remediation_other=data.get("parent_remediation_other"),
                community_remediation=data.get("community_remediation"),
                community_remediation_other=data.get("community_remediation_other"),
            )
            return JsonResponse({"message": "Remediation record created successfully", "id": remediation.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    def put(self, request, remediation_id):
        remediation = get_object_or_404(ChildRemediationTbl, id=remediation_id)
        try:
            data = json.loads(request.body)
            remediation.consent_id = data.get("consent", remediation.consent_id)
            remediation.school_fees_owed = data.get("school_fees_owed", remediation.school_fees_owed)
            remediation.parent_remediation = data.get("parent_remediation", remediation.parent_remediation)
            remediation.parent_remediation_other = data.get("parent_remediation_other", remediation.parent_remediation_other)
            remediation.community_remediation = data.get("community_remediation", remediation.community_remediation)
            remediation.community_remediation_other = data.get("community_remediation_other", remediation.community_remediation_other)
            remediation.save()
            return JsonResponse({"message": "Remediation record updated successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    
    def delete(self, request, remediation_id):
        remediation = get_object_or_404(ChildRemediationTbl, id=remediation_id)
        remediation.delete()
        return JsonResponse({"message": "Remediation record deleted successfully"}, status=200)


####################################################################################################
# Household Sensitization Assessment
####################################################################################################

class HouseholdSensitizationView(View):
    def get(self, request, sensitization_id=None):
        if sensitization_id:
            sensitization = get_object_or_404(HouseholdSensitizationTbl, pk=sensitization_id)
            data = {
                "id": sensitization.id,
                "consent": sensitization.consent.id if sensitization.consent else None,
                "sensitized_good_parenting": sensitization.sensitized_good_parenting,
                "sensitized_child_protection": sensitization.sensitized_child_protection,
                "sensitized_safe_labour": sensitization.sensitized_safe_labour,
                "number_of_female_adults": sensitization.number_of_female_adults,
                "number_of_male_adults": sensitization.number_of_male_adults,
                "picture_of_respondent": sensitization.picture_of_respondent,
                "picture_sensitization": sensitization.picture_sensitization.url if sensitization.picture_sensitization else None,
                "feedback_observations": sensitization.feedback_observations,
            }
            return JsonResponse(data, status=200)
        
        sensitizations = HouseholdSensitizationTbl.objects.all().values()
        return JsonResponse(list(sensitizations), safe=False, status=200)

    def post(self, request):
        try:
            data = json.loads(request.body)
            sensitization = HouseholdSensitizationTbl.objects.create(
                consent_id=data.get("consent"),
                sensitized_good_parenting=data.get("sensitized_good_parenting"),
                sensitized_child_protection=data.get("sensitized_child_protection"),
                sensitized_safe_labour=data.get("sensitized_safe_labour"),
                number_of_female_adults=data.get("number_of_female_adults"),
                number_of_male_adults=data.get("number_of_male_adults"),
                picture_of_respondent=data.get("picture_of_respondent"),
                feedback_observations=data.get("feedback_observations"),
            )
            return JsonResponse({"message": "Sensitization record created successfully", "id": sensitization.id}, status=201)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def put(self, request, sensitization_id):
        sensitization = get_object_or_404(HouseholdSensitizationTbl, pk=sensitization_id)
        try:
            data = json.loads(request.body)
            sensitization.sensitized_good_parenting = data.get("sensitized_good_parenting", sensitization.sensitized_good_parenting)
            sensitization.sensitized_child_protection = data.get("sensitized_child_protection", sensitization.sensitized_child_protection)
            sensitization.sensitized_safe_labour = data.get("sensitized_safe_labour", sensitization.sensitized_safe_labour)
            sensitization.number_of_female_adults = data.get("number_of_female_adults", sensitization.number_of_female_adults)
            sensitization.number_of_male_adults = data.get("number_of_male_adults", sensitization.number_of_male_adults)
            sensitization.picture_of_respondent = data.get("picture_of_respondent", sensitization.picture_of_respondent)
            sensitization.feedback_observations = data.get("feedback_observations", sensitization.feedback_observations)
            sensitization.save()
            return JsonResponse({"message": "Sensitization record updated successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, sensitization_id):
        sensitization = get_object_or_404(HouseholdSensitizationTbl, pk=sensitization_id)
        sensitization.delete()
        return JsonResponse({"message": "Sensitization record deleted successfully"}, status=204)


####################################################################################################
# End of Collection
####################################################################################################

@method_decorator(csrf_exempt, name='dispatch')
class EndOfCollectionView(View):
    
    def get(self, request, id=None):
        if id:
            record = get_object_or_404(EndOfCollection, id=id)
            data = {
                'id': record.id,
                'sensitization': record.sensitization.id if record.sensitization else None,
                'feedback_enum': record.feedback_enum,
                'picture_of_respondent': record.picture_of_respondent.url if record.picture_of_respondent else None,
                'signature_producer': record.signature_producer.url if record.signature_producer else None,
                'end_gps': record.end_gps,
                'end_time': record.end_time,
            }
            return JsonResponse(data, status=200)
        else:
            records = EndOfCollection.objects.all().values()
            return JsonResponse(list(records), safe=False, status=200)
    
    def post(self, request):
        data = request.POST
        file_data = request.FILES
        
        record = EndOfCollection.objects.create(
            sensitization_id=data.get('sensitization'),
            feedback_enum=data.get('feedback_enum'),
            end_gps=data.get('end_gps'),
            end_time=data.get('end_time'),
            picture_of_respondent=file_data.get('picture_of_respondent'),
            signature_producer=file_data.get('signature_producer'),
        )
        return JsonResponse({'message': 'Record created', 'id': record.id}, status=201)
    
    def put(self, request, id):
        record = get_object_or_404(EndOfCollection, id=id)
        data = json.loads(request.body)
        
        record.feedback_enum = data.get('feedback_enum', record.feedback_enum)
        record.end_gps = data.get('end_gps', record.end_gps)
        record.end_time = data.get('end_time', record.end_time)
        record.sensitization_id = data.get('sensitization', record.sensitization_id)
        record.save()
        
        return JsonResponse({'message': 'Record updated'}, status=200)
    
    def delete(self, request, id):
        record = get_object_or_404(EndOfCollection, id=id)
        
        if record.picture_of_respondent:
            default_storage.delete(record.picture_of_respondent.path)
        if record.signature_producer:
            default_storage.delete(record.signature_producer.path)
        
        record.delete()
        return JsonResponse({'message': 'Record deleted'}, status=204)
