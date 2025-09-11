from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin
from .models import *

# Resource classes for import/export
class RegionTblResource(resources.ModelResource):
    class Meta:
        model = regionTbl
        fields = ('id', 'region', 'created_date', 'delete_field')

class DistrictTblResource(resources.ModelResource):
    class Meta:
        model = districtTbl
        fields = ('id', 'regionTbl_foreignkey', 'district', 'district_code', 'created_date', 'delete_field')

class StaffTblResource(resources.ModelResource):
    class Meta:
        model = staffTbl
        fields = ('id', 'user', 'first_name', 'last_name', 'gender', 'contact', 'designation', 
                 'email_address', 'uid', 'fbase_code', 'district', 'staffid', 'cmpassword', 
                 'created_date', 'delete_field')

class SocietyTblResource(resources.ModelResource):
    class Meta:
        model = societyTbl
        fields = ('id', 'districtTbl_foreignkey', 'society', 'society_code', 
                 'society_pre_code', 'new_society_pre_code', 'created_date', 'delete_field')

class FarmerTblResource(resources.ModelResource):
    class Meta:
        model = farmerTbl
        fields = ('id', 'first_name', 'last_name', 'farmer_code', 'society_name', 
                 'national_id_no', 'contact', 'id_type', 'id_expiry_date', 
                 'no_of_cocoa_farms', 'no_of_certified_crop', 
                 'total_cocoa_bags_harvested_previous_year', 
                 'total_cocoa_bags_sold_group_previous_year', 
                 'current_year_yeild_estimate', 'staffTbl_foreignkey', 'uuid', 
                 'farmer_photo', 'cal_no_mapped_farms', 'mapped_status', 
                 'new_farmer_code', 'created_date', 'delete_field')

class DistrictStaffTblResource(resources.ModelResource):
    class Meta:
        model = districtStaffTbl
        fields = ('id', 'staffTbl_foreignkey', 'districtTbl_foreignkey', 
                 'created_date', 'delete_field')

class PciTblResource(resources.ModelResource):
    class Meta:
        model = pciTbl
        fields = ('id', 'enumerator', 'society', 'access_to_protected_water', 
                 'hire_adult_labourers', 'awareness_raising_session', 
                 'women_leaders', 'pre_school', 'primary_school', 'separate_toilets', 
                 'provide_food', 'scholarships', 'corporal_punishment', 'total_index', 
                 'status', 'created_at', 'updated_at', 'created_date', 'delete_field')

class SchhoolTblResource(resources.ModelResource):
    class Meta:
        model = schhoolTbl
        fields = ('id', 'name', 'pci', 'separate_toilet', 'food_provided', 
                 'corporal_punishment', 'created_date', 'delete_field')

class HouseHoldTblResource(resources.ModelResource):
    class Meta:
        model = houseHoldTbl
        fields = ('id', 'enumerator', 'farmer', 'interview_start_time', 'gps_point', 
                 'community_type', 'farmer_resides_in_community', 
                 'farmer_residing_community', 'farmer_available', 'reason_unavailable', 
                 'reason_unavailable_other', 'available_answer_by', 
                 'refusal_toa_participate_reason_survey', 'total_adults', 
                 'is_name_correct', 'exact_name', 'nationality', 'country_origin', 
                 'country_origin_other', 'is_owner', 'owner_status_01', 'owner_status_00', 
                 'children_present', 'num_children_5_to_17', 'feedback_enum', 
                 'picture_of_respondent', 'signature_producer', 'end_gps', 'end_time', 
                 'sensitized_good_parenting', 'sensitized_child_protection', 
                 'sensitized_safe_labour', 'number_of_female_adults', 
                 'number_of_male_adults', 'picture_sensitization', 'feedback_observations', 
                 'school_fees_owed', 'parent_remediation', 'parent_remediation_other', 
                 'community_remediation', 'community_remediation_other', 'name_owner', 
                 'first_name_owner', 'nationality_owner', 'country_origin_owner', 
                 'country_origin_owner_other', 'manager_work_length', 'recruited_workers', 
                 'worker_recruitment_type', 'worker_agreement_type', 'worker_agreement_other', 
                 'tasks_clarified', 'additional_tasks', 'refusal_action', 
                 'refusal_action_other', 'salary_status', 'recruit_1', 'recruit_2', 
                 'recruit_3', 'conditions_1', 'conditions_2', 'conditions_3', 
                 'conditions_4', 'conditions_5', 'leaving_1', 'leaving_2', 
                 'consent_recruitment', 'created_at', 'updated_at', 'created_date', 'delete_field')

class AdultHouseholdMemberResource(resources.ModelResource):
    class Meta:
        model = AdultHouseholdMember
        fields = ('id', 'houseHold', 'full_name', 'relationship', 'relationship_other', 
                 'gender', 'nationality', 'country_origin', 'country_origin_other', 
                 'year_birth', 'birth_certificate', 'main_work', 'main_work_other', 
                 'created_at', 'updated_at', 'created_date', 'delete_field')

class ChildInHouseholdTblResource(resources.ModelResource):
    class Meta:
        model = ChildInHouseholdTbl
        fields = ('id', 'houseHold', 'child_declared_in_cover', 'child_identifier', 
                 'child_can_be_surveyed', 'child_unavailability_reason', 
                 'child_not_avail', 'who_answers_child_unavailable', 
                 'who_answers_child_unavailable_other', 'child_first_name', 
                 'child_surname', 'child_gender', 'child_year_birth', 
                 'child_birth_certificate', 'child_birth_certificate_reason', 
                 'child_born_in_community', 'child_country_of_birth', 
                 'child_country_of_birth_other', 'child_relationship_to_head', 
                 'child_relationship_to_head_other', 'child_not_live_with_family_reason', 
                 'child_not_live_with_family_reason_other', 'child_decision_maker', 
                 'child_decision_maker_other', 'child_agree_with_decision', 
                 'child_seen_parents', 'child_last_seen_parent', 'child_living_duration', 
                 'child_accompanied_by', 'child_accompanied_by_other', 
                 'child_father_location', 'child_father_country', 
                 'child_father_country_other', 'child_mother_location', 
                 'child_mother_country', 'child_mother_country_other', 
                 'child_educated', 'child_school_name', 'school_type', 'child_grade', 
                 'sch_going_times', 'basic_need_available', 'child_schl2', 
                 'child_schl_left_age', 'calculation_response', 'reading_response', 
                 'writing_response', 'education_level', 'child_schl_left_why', 
                 'child_schl_left_why_other', 'child_why_no_school', 
                 'child_why_no_school_other', 'child_school_7days', 
                 'child_school_absence_reason', 'child_school_absence_reason_other', 
                 'missed_school', 'missed_school_reason', 'missed_school_reason_other', 
                 'work_in_house', 'work_on_cocoa', 'work_frequency', 'observed_work', 
                 'performed_tasks', 'created_at', 'updated_at', 'created_date', 'delete_field')

class LightTaskTblResource(resources.ModelResource):
    class Meta:
        model = lightTaskTbl
        fields = ('id', 'name', 'created_date', 'delete_field')

class HeavyTaskTblResource(resources.ModelResource):
    class Meta:
        model = heavyTaskTbl
        fields = ('id', 'name', 'created_date', 'delete_field')

class ChildLightTaskTblResource(resources.ModelResource):
    class Meta:
        model = childLightTaskTbl
        fields = ('id', 'task', 'child', 'remuneration_received_12months', 
                 'light_duty_duration_school_12', 'light_duty_duration_non_school_12', 
                 'task_location_12', 'task_location_other_12', 
                 'total_hours_light_work_school_12', 'total_hours_light_work_non_school_12', 
                 'under_supervision_12', 'tasks_done_in_7days', 'created_at', 
                 'updated_at', 'created_date', 'delete_field')

class ChildHeavyTaskTblResource(resources.ModelResource):
    class Meta:
        model = childHeavyTaskTbl
        fields = ('id', 'task', 'child', 'salary_received', 'task_location', 
                 'task_location_other', 'longest_time_school_day', 
                 'longest_time_non_school_day', 'total_hours_school_days', 
                 'total_hours_non_school_days', 'under_supervision', 
                 'heavy_tasks_12months', 'salary_received_12', 'task_location_12', 
                 'task_location_other_12', 'longest_time_school_day', 
                 'longest_time_non_school_day', 'total_hours_school_days', 
                 'total_hours_non_school_days', 'under_supervision', 'child_work_who', 
                 'child_work_who_other', 'child_work_why', 'child_work_why_other', 
                 'agrochemicals_applied', 'child_on_farm_during_agro', 'suffered_injury', 
                 'wound_cause', 'wound_cause_other', 'wound_time', 'child_often_pains', 
                 'help_child_health', 'help_child_health_other', 'child_photo', 
                 'created_at', 'updated_at', 'created_date', 'delete_field')

class ChildLightTask12MonthsTblResource(resources.ModelResource):
    class Meta:
        model = childLightTask12MonthsTbl
        fields = ('id', 'child', 'task', 'remuneration_received', 
                 'light_duty_duration_school', 'light_duty_duration_non_school', 
                 'task_location', 'task_location_other', 'total_hours_light_work_school', 
                 'total_hours_light_work_non_school', 'under_supervision', 
                 'performed_tasks_12months', 'created_at', 'updated_at', 
                 'created_date', 'delete_field')

class ChildHeavyTask12MonthsTblResource(resources.ModelResource):
    class Meta:
        model = childHeavyTask12MonthsTbl
        fields = ('id', 'child', 'task', 'salary_received', 'task_location', 
                 'task_location_other', 'longest_time_school_day', 
                 'longest_time_non_school_day', 'total_hours_school_days', 
                 'total_hours_non_school_days', 'under_supervision', 
                 'heavy_tasks_12months', 'salary_received_12', 'task_location_12', 
                 'task_location_other_12', 'longest_time_school_day', 
                 'longest_time_non_school_day', 'total_hours_school_days', 
                 'total_hours_non_school_days', 'under_supervision', 'child_work_who', 
                 'child_work_who_other', 'child_work_why', 'child_work_why_other', 
                 'agrochemicals_applied', 'child_on_farm_during_agro', 'suffered_injury', 
                 'wound_cause', 'wound_cause_other', 'wound_time', 'child_often_pains', 
                 'help_child_health', 'help_child_health_other', 'child_photo', 
                 'created_at', 'updated_at', 'created_date', 'delete_field')

# Admin classes
@admin.register(regionTbl)
class RegionTblAdmin(ImportExportModelAdmin):
    resource_class = RegionTblResource
    list_display = ('region', 'created_date')
    list_filter = ('created_date',)
    search_fields = ('region',)

@admin.register(districtTbl)
class DistrictTblAdmin(ImportExportModelAdmin):
    resource_class = DistrictTblResource
    list_display = ('district', 'district_code', 'regionTbl_foreignkey')
    list_filter = ('regionTbl_foreignkey',)
    search_fields = ('district', 'district_code')

@admin.register(staffTbl)
class StaffTblAdmin(ImportExportModelAdmin):
    resource_class = StaffTblResource
    list_display = ('first_name', 'last_name', 'designation', 'contact')
    list_filter = ('designation', 'gender')
    search_fields = ('first_name', 'last_name', 'contact')

@admin.register(societyTbl)
class SocietyTblAdmin(ImportExportModelAdmin):
    resource_class = SocietyTblResource
    list_display = ('society', 'society_code', 'districtTbl_foreignkey')
    list_filter = ('districtTbl_foreignkey',)
    search_fields = ('society', 'society_code')

@admin.register(farmerTbl)
class FarmerTblAdmin(ImportExportModelAdmin):
    resource_class = FarmerTblResource
    list_display = ('first_name', 'last_name', 'farmer_code', 'society_name')
    list_filter = ('society_name',)
    search_fields = ('first_name', 'last_name', 'farmer_code', 'contact')

@admin.register(districtStaffTbl)
class DistrictStaffTblAdmin(ImportExportModelAdmin):
    resource_class = DistrictStaffTblResource
    list_display = ('staffTbl_foreignkey', 'districtTbl_foreignkey')
    list_filter = ('districtTbl_foreignkey',)

@admin.register(pciTbl)
class PciTblAdmin(ImportExportModelAdmin):
    resource_class = PciTblResource
    list_display = ('society', 'total_index', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('society__society',)

@admin.register(schhoolTbl)
class SchhoolTblAdmin(ImportExportModelAdmin):
    resource_class = SchhoolTblResource
    list_display = ('name', 'pci')
    list_filter = ('pci',)
    search_fields = ('name',)

@admin.register(houseHoldTbl)
class HouseHoldTblAdmin(ImportExportModelAdmin):
    resource_class = HouseHoldTblResource
    list_display = ('farmer', 'community_type', 'interview_start_time')
    list_filter = ('community_type', 'interview_start_time')
    search_fields = ('farmer__first_name', 'farmer__last_name')

@admin.register(AdultHouseholdMember)
class AdultHouseholdMemberAdmin(ImportExportModelAdmin):
    resource_class = AdultHouseholdMemberResource
    list_display = ('full_name', 'houseHold', 'relationship', 'gender')
    list_filter = ('relationship', 'gender')
    search_fields = ('full_name',)

@admin.register(ChildInHouseholdTbl)
class ChildInHouseholdTblAdmin(ImportExportModelAdmin):
    resource_class = ChildInHouseholdTblResource
    list_display = ('child_first_name', 'child_surname', 'houseHold', 'child_gender')
    list_filter = ('child_gender', 'child_educated')
    search_fields = ('child_first_name', 'child_surname')

@admin.register(lightTaskTbl)
class LightTaskTblAdmin(ImportExportModelAdmin):
    resource_class = LightTaskTblResource
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(heavyTaskTbl)
class HeavyTaskTblAdmin(ImportExportModelAdmin):
    resource_class = HeavyTaskTblResource
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(childLightTaskTbl)
class ChildLightTaskTblAdmin(ImportExportModelAdmin):
    resource_class = ChildLightTaskTblResource
    list_display = ('child', 'task')
    list_filter = ('task',)

@admin.register(childHeavyTaskTbl)
class ChildHeavyTaskTblAdmin(ImportExportModelAdmin):
    resource_class = ChildHeavyTaskTblResource
    list_display = ('child', 'task')
    list_filter = ('task',)

@admin.register(childLightTask12MonthsTbl)
class ChildLightTask12MonthsTblAdmin(ImportExportModelAdmin):
    resource_class = ChildLightTask12MonthsTblResource
    list_display = ('child', 'task')
    list_filter = ('task',)

@admin.register(childHeavyTask12MonthsTbl)
class ChildHeavyTask12MonthsTblAdmin(ImportExportModelAdmin):
    resource_class = ChildHeavyTask12MonthsTblResource
    list_display = ('child', 'task')
    list_filter = ('task',)









# admin.py
from django.contrib import admin
from .models import PriorityLevel, DeadlineType, DeadlineAssignment

@admin.register(PriorityLevel)
class PriorityLevelAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'description']
    search_fields = ['name']

@admin.register(DeadlineType)
class DeadlineTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(DeadlineAssignment)
class DeadlineAssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'assigned_to', 'deadline_type', 'priority_level', 'start_date', 'end_date', 'status']
    list_filter = ['status', 'priority_level', 'deadline_type', 'staff_type', 'start_date']
    search_fields = ['title', 'assigned_to__first_name', 'assigned_to__last_name']
    readonly_fields = ['status', 'completion_date']
    date_hierarchy = 'start_date'