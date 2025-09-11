from django.urls import path


from . import views

urlpatterns = [

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
    path('review_responses/', views.review_responses, name='create_response_api'),
    path('api/responses/', views.response_list_api, name='response_list_api'),
    path('api/responses/<int:response_id>/', views.response_detail_api, name='response_detail_api'),
    path('api/queries/<int:query_id>/mark-resolved/', views.mark_query_resolved_api, name='mark_query_resolved_api'),
    path('api/queries/<int:query_id>/request-clarification/', views.request_clarification_api, name='request_clarification_api'),


]