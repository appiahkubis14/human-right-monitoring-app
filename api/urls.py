from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import *

schema_view = get_schema_view(
    openapi.Info(
        title="HRM API Documentation",
        default_version="v1",
        description="HRM app API documentation for Afarinick Company Ltd",
        terms_of_service="https://www.api.com/terms/",
        contact=openapi.Contact(email="contact@afarinick.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

app_name = "api"

urlpatterns = [
    # Authentication endpoints
    path('v1/auth/login/', StaffLoginAPIView.as_view(), name='staff-login'),
    path('v1/auth/change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    
    # Staff endpoints
    path('v1/staff/', StaffAPIView.as_view(), name='staff-list'),
    path('v1/staff/<int:staff_id>/', StaffDetailAPIView.as_view(), name='staff-detail'),
    
    # Farmer endpoints
    path('v1/farmers/', FarmerAPIView.as_view(), name='farmer-list'),
    path('v1/farmers/<int:farmer_id>/', FarmerDetailAPIView.as_view(), name='farmer-detail'),
    
    # PCI endpoints
    path('v1/pci/', PCIAPIView.as_view(), name='pci-list'),
    path('v1/pci/<int:pci_id>/', PCIDetailAPIView.as_view(), name='pci-detail'),
    
    # Household endpoints
    path('v1/households/', HouseholdAPIView.as_view(), name='household-list'),
    path('v1/households/<int:household_id>/', HouseholdDetailAPIView.as_view(), name='household-detail'),
    
    # Adult Household Member endpoints
    path('v1/adult-members/', AdultHouseholdMemberAPIView.as_view(), name='adult-member-list'),
    path('v1/adult-members/<int:member_id>/', AdultHouseholdMemberDetailAPIView.as_view(), name='adult-member-detail'),

    # Child endpoints
    path('v1/children/', ChildInHouseholdAPIView.as_view(), name='child-list'),

    # Light Task URLs
    path('v1/light-tasks/', LightTaskAPIView.as_view(), name='light-task-list'),
    path('v1/light-tasks/<int:task_id>/', LightTaskDetailAPIView.as_view(), name='light-task-detail'),

    # Heavy Task URLs
    path('v1/heavy-tasks/', HeavyTaskAPIView.as_view(), name='heavy-task-list'),
    path('v1/heavy-tasks/<int:task_id>/', HeavyTaskDetailAPIView.as_view(), name='heavy-task-detail'),

    # Child Light Task URLs
    path('v1/child-light-tasks/', ChildLightTaskAPIView.as_view(), name='child-light-task-list'),

    # Child Heavy Task URLs
    path('v1/child-heavy-tasks/', ChildHeavyTaskAPIView.as_view(), name='child-heavy-task-list'),

    # Child Light Task 12 Months URLs
    path('v1/child-light-tasks-12months/', ChildLightTask12MonthsAPIView.as_view(), name='child-light-task-12months-list'),

    # Child Heavy Task 12 Months URLs
    path('v1/child-heavy-tasks-12months/', ChildHeavyTask12MonthsAPIView.as_view(), name='child-heavy-task-12months-list'),
        
    # Region/District/Society endpoints
    path('v1/regions/', RegionAPIView.as_view(), name='region-list'),
    path('v1/districts/', DistrictAPIView.as_view(), name='district-list'),
    path('v1/societies/', SocietyAPIView.as_view(), name='society-list'),
    
    # Deadline endpoints
    path('v1/deadlines/', DeadlineAssignmentAPIView.as_view(), name='deadline-list'),
    
    # Query endpoints
    path('v1/queries/', QueryAPIView.as_view(), name='query-list'),
    
    # Risk Assessment endpoints
    path('v1/risk-assessments/', RiskAssessmentAPIView.as_view(), name='risk-assessment-list'),
    
    # Utility endpoints
    path('v1/health/', HealthCheckAPIView.as_view(), name='health-check'),
    
    # Documentation
    path('v1/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('v1/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('v1/swagger.json/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]