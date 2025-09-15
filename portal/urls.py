from django.urls import path


from . import views

urlpatterns = [

    path('dashboard/', views.child_labor_dashboard, name='dashboard'),

    path('staff-management/', views.StaffManagementView.as_view(), name='staff_management'),
    path('staff-data/', views.get_staff_data, name='get_staff_data'),
    path('details/', views.get_staff_details, name='get_staff_details'),
    path('staff-create/', views.create_staff, name='create_staff'),
    path('staff-update/<int:staff_id>/', views.update_staff, name='update_staff'),
    path('staff-delete/<int:staff_id>/', views.delete_staff, name='delete_staff'),
    path('designation-options/', views.get_designation_options, name='get_designation_options'),

    ##################################################################################################
    path('assignments-overview/', views.AssignmentsOverviewView.as_view(), name='assignments_overview'),
    path('assignments-data/', views.get_assignments_data, name='get_assignments_data'),
    path('assignment-details/', views.get_assignment_details, name='get_assignment_details'),
    path('assignment-create/', views.create_assignment, name='create_assignment'),
    path('assignment-update/<int:assignment_id>/', views.update_assignment, name='update_assignment'),
    path('assignment-delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('staff-options/', views.get_staff_options, name='get_staff_options'),
    path('district-options/', views.get_district_options, name='get_district_options'),

    ####################################################################################################

    path('priorities-deadlines-assignments/', views.DeadlinesView.as_view(), name='deadlines_priorities'),
    path('priorities-deadlines-data/', views.get_deadlines_data, name='get_deadlines_data'),
    path('priorities-deadlines-details/', views.get_deadline_details, name='get_deadline_details'),
    path('priorities-deadlines-create/', views.create_deadline, name='create_deadline'),
    path('priorities-deadlines-update/<int:deadline_id>/', views.update_deadline, name='update_deadline'),
    path('priorities-deadlines-delete/<int:deadline_id>/', views.delete_deadline, name='delete_deadline'),
    path('options/', views.get_options_data, name='get_deadline_options'),



    #######################################################################################################

    path('farmers-management/', views.FarmersView.as_view(), name='farmers_management'),
    path('farmers-data/', views.get_farmers_data, name='get_farmers_data'),
    path('farmers-details/', views.get_farmer_details, name='get_farmer_details'),
    path('farmers-create/', views.create_farmer, name='create_farmer'),
    path('farmers-update/<int:farmer_id>/', views.update_farmer, name='update_farmer'),
    path('farmers-delete/<int:farmer_id>/', views.delete_farmer, name='delete_farmer'),
    path('farmer-options/', views.get_farmer_options_data, name='get_farmer_options'),


    #########################################################################################################

    path('societies/', views.societies_list, name='societies_list'),
    path('societies/data/', views.get_societies_data, name='get_societies_data'),
    path('societies/options/', views.get_society_options, name='get_society_options'),
    path('societies/create/', views.create_society, name='create_society'),
    path('societies/details/', views.get_society_details, name='get_society_details'),
    path('societies/update/<int:society_id>/', views.update_society, name='update_society'),
    path('societies/delete/<int:society_id>/', views.delete_society, name='delete_society'),


    ##########################################################################################################

    path('send-query/', views.send_query, name='send_query'),
    path('review-responses/', views.review_responses, name='review_responses'),
    path('flag-issues/', views.flag_issues, name='flag_issues'),
    path('escalate-cases/', views.escalate_cases, name='escalate_cases'),
    
    # API endpoints
    path('api/queries/', views.query_list_api, name='query_list_api'),
    path('api/queries/create/', views.create_query_api, name='create_query_api'),
    path('api/queries/<int:query_id>/', views.query_detail_api, name='query_detail_api'),
    path('api/queries/<int:query_id>/respond/', views.respond_to_query_api, name='respond_to_query_api'),
    path('api/queries/<int:query_id>/flag/', views.flag_query_api, name='flag_query_api'),
    path('api/queries/<int:query_id>/escalate/', views.escalate_query_api, name='escalate_query_api'),
    path('api/staff/enumerators/', views.get_enumerators_api, name='get_enumerators_api'),
    path('api/staff/supervisors/', views.get_supervisors_api, name='get_supervisors_api'),
    path('api/categories/', views.get_categories_api, name='get_categories_api'),
    path('api/households/', views.get_households_api, name='get_households_api'),
    path('api/farmers/', views.get_farmers_api, name='get_farmers_api'),
    path('api/children/', views.get_children_api, name='get_children_api'),


    #############################################################################################################
    path('review-responses/', views.review_responses, name='create_response_api'),
    path('api/responses/', views.response_list_api, name='response_list_api'),
    path('api/responses/<int:response_id>/', views.response_detail_api, name='response_detail_api'),
    path('api/queries/<int:query_id>/mark-resolved/', views.mark_query_resolved_api, name='mark_query_resolved_api'),
    path('api/queries/<int:query_id>/request-clarification/', views.request_clarification_api, name='request_clarification_api'),


    ##############################################################################################################

    path('community-pci/', views.community_pci_view, name='community_pci'),
    
    # API endpoints
    path('api/pci/', views.pci_list_api, name='pci_list_api'),
    path('api/pci/create/', views.create_pci_api, name='create_pci_api'),
    path('api/pci/<int:pci_id>/', views.pci_detail_api, name='pci_detail_api'),
    path('api/pci/<int:pci_id>/delete/', views.delete_pci_api, name='delete_pci_api'),
    
    # Filter data endpoints
    path('api/districts/', views.get_districts_api, name='get_districts_api'),
    path('api/communities/', views.get_communities_api, name='get_communities_api'),
    path('api/enumerators/', views.get_enumerators_api, name='get_enumerators_api'),

    ########################################################################################################

    path('farmer-children/', views.farmer_children_view, name='farmer_children'),
    
    # API endpoints
    path('api/farmer-children/', views.farmer_children_list_api, name='farmer_children_list_api'),
    path('api/farmer-children/create/', views.create_farmer_child_api, name='create_farmer_child_api'),
    path('api/farmer-children/<int:child_id>/', views.farmer_child_detail_api, name='farmer_child_detail_api'),
    path('api/farmer-children/<int:child_id>/delete/', views.delete_farmer_child_api, name='delete_farmer_child_api'),
    
    # Filter data endpoints
    path('api/farmers/', views.get_farmers_api, name='get_farmers_api'),
    path('api/communities/', views.get_communities_api, name='get_communities_api'),
    path('api/districts/', views.get_districts_api, name='get_districts_api'),


    ########################################################################################################
    path('risk-assessment/', views.risk_assessment_view, name='risk_assessment'),
    path('api/risk-assessment/', views.risk_assessment_list_api, name='risk_assessment_list_api'),
    path('api/risk-assessment/<int:assessment_id>/', views.risk_assessment_detail_api, name='risk_assessment_detail_api'),
    path('api/risk-assessment/reassess-all/', views.reassess_all_risks_api, name='reassess_all_risks_api'),
    path('api/risk-assessment/reassess-child/<int:child_id>/', views.reassess_child_risk_api, name='reassess_child_risk_api'),


    ########################################################################################################

    # Adult Members pages
    path('adult-members/', views.adult_members_view, name='adult_members'),
    
    # API endpoints
    path('api/adult-members/', views.adult_members_list_api, name='adult_members_list_api'),
    path('api/adult-members/create/', views.create_adult_member_api, name='create_adult_member_api'),
    path('api/adult-members/<int:member_id>/', views.adult_member_detail_api, name='adult_member_detail_api'),
    path('api/adult-members/<int:member_id>/update/', views.update_adult_member_api, name='update_adult_member_api'),
    path('api/adult-members/<int:member_id>/delete/', views.delete_adult_member_api, name='delete_adult_member_api'),
    
    # Filter data endpoints
    path('api/households/', views.get_households_api, name='get_households_api'),
    path('api/farmers/', views.get_farmers_api, name='get_farmers_api'),


    ########################################################################################################

    path('child-members/', views.ChildMembersView.as_view(), name='child_members'),
    path('child-members/data/', views.get_child_members_data, name='get_child_members_data'),
    path('child-members/details/', views.get_child_member_details, name='get_child_member_details'),
    path('child-members/create/', views.create_child_member, name='create_child_member'),
    path('child-members/update/<int:child_id>/', views.update_child_member, name='update_child_member'),
    path('child-members/delete/<int:child_id>/', views.delete_child_member, name='delete_child_member'),
    path('child-members/options/', views.get_child_options_data, name='get_child_options'),


    ############################################################################################################

    path('light-tasks/', views.light_tasks_list, name='light_tasks_list'),
    path('light-tasks/data/', views.get_light_tasks_data, name='get_light_tasks_data'),
    path('light-tasks/create/', views.create_light_task, name='create_light_task'),
    path('light-tasks/<int:task_id>/details/', views.get_light_task_details, name='get_light_task_details'),
    path('light-tasks/<int:task_id>/update/', views.update_light_task, name='update_light_task'),
    path('light-tasks/<int:task_id>/delete/', views.delete_light_task, name='delete_light_task'),

    ###############################################################################################################

     # Heavy Tasks URLs
    path('heavy-tasks/', views.heavy_tasks_list, name='heavy_tasks_list'),
    path('heavy-tasks/data/', views.get_heavy_tasks_data, name='get_heavy_tasks_data'),
    path('heavy-tasks/create/', views.create_heavy_task, name='create_heavy_task'),
    path('heavy-tasks/<int:task_id>/details/', views.get_heavy_task_details, name='get_heavy_task_details'),
    path('heavy-tasks/<int:task_id>/update/', views.update_heavy_task, name='update_heavy_task'),
    path('heavy-tasks/<int:task_id>/delete/', views.delete_heavy_task, name='delete_heavy_task'),
    
    # Child Heavy Tasks URLs
    path('child-heavy-tasks/data/', views.get_child_heavy_tasks_data, name='get_child_heavy_tasks_data'),
    path('child-heavy-tasks/data/child/<int:child_id>/', views.get_child_heavy_tasks_data, name='get_child_heavy_tasks_data_for_child'),


    #################################################################################################################

    # path('quality/validate-data/', views.validate_data_list, name='quality'),
    # path('quality/validate-data/', views.validate_data_list, name='validate_data_list'),
    # path('quality/validate-data/data/', views.get_validation_data, name='get_validation_data'),
    # path('quality/validate-data/stats/', views.get_validation_stats, name='get_validation_stats'),
    # path('quality/validate-data/household/<int:household_id>/', views.get_household_details, name='get_household_details'),
    # path('quality/validate-data/household/<int:household_id>/validate/', views.validate_household, name='validate_household'),

    ##################################################################################################################################

    path('quality/audit-checks/', views.AuditChecksView.as_view(), name='audit_checks'),
    path('quality/audit-checks/data/', views.get_audit_checks_data, name='get_audit_checks_data'),
    path('quality/audit-checks/details/', views.get_audit_check_details, name='get_audit_check_details'),
    path('quality/audit-checks/create/', views.create_audit_check, name='create_audit_check'),
    path('quality/audit-checks/update/<int:audit_id>/', views.update_audit_check, name='update_audit_check'),
    path('quality/audit-checks/delete/<int:audit_id>/', views.delete_audit_check, name='delete_audit_check'),
    path('quality/audit-checks/options/', views.get_audit_options_data, name='get_audit_options'),




    ###################################################################################################################################

     # Quality Control pages
    path('quality/validate-data/', views.validate_data_view, name='validate_data'),
    path('quality/approve-surveys/', views.approve_surveys_view, name='approve_surveys'),
    path('quality/audit-checks/', views.audit_checks_view, name='audit_checks'),
    path('quality/spot-checks/', views.spot_checks_view, name='spot_checks'),
    
    # API endpoints
    path('api/quality/household-surveys/', views.household_surveys_list_api, name='household_surveys_list_api'),
    path('api/quality/household-surveys/<int:survey_id>/validate/', views.validate_household_survey_api, name='validate_household_survey_api'),
    path('api/quality/household-surveys/<int:survey_id>/reject/', views.reject_household_survey_api, name='reject_household_survey_api'),
    path('api/quality/household-surveys/<int:survey_id>/details/', views.household_survey_detail_api, name='household_survey_detail_api'),
    path('api/quality/validation-rules/', views.get_validation_rules_api, name='get_validation_rules_api'),
    
    # Filter endpoints
    path('api/quality/enumerators/', views.get_enumerators_api, name='get_enumerators_api'),
    path('api/quality/communities/', views.get_communities_api, name='get_communities_api'),


    #################################################################################################################################################

    # Map Overview URLs
   path('map-overview/', views.map_overview_view, name='map_overview'),
    path('api/survey-locations/', views.get_survey_locations_api, name='survey_locations_api'),
    path('api/survey-details/<int:survey_id>/', views.get_survey_details_api, name='survey_details_api'),
    path('api/enumerators/', views.get_enumerators_api, name='get_enumerators_api'),
    path('api/districts/', views.get_districts_api, name='get_districts_api'),
    path('api/enumerator-tracking/<int:enumerator_id>/', views.get_enumerator_tracking_api, name='enumerator_tracking_api'),
    path('api/map-clusters/', views.get_map_clusters_api, name='map_clusters_api'),
    path('api/export-map-data/', views.export_map_data_api, name='export_map_data_api'),
]