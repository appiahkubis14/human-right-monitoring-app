from django.urls import path
from .views import (
    adult_household_member_view,
    adult_in_household_view,
    ChildEducationDetailsView,
    ChildRemediationView,
    child_in_household_view,
    children_in_household_view,
    ConsentLocationView,
    cover_view,
    EndOfCollectionView,
    farmer_child_view,
    farmer_identification_view,
    HouseholdSensitizationView,
    owner_identification_view,
    workers_in_farm_view,
)

urlpatterns = [
    # Cover endpoints:
    path('cover/', cover_view, name='cover-list'),  # GET: List all covers; POST: Create a new cover.
    path('cover/<int:cover_id>/', cover_view, name='cover-detail'),  # GET: Retrieve, PUT: Update, DELETE: Delete a specific cover.

    # Farmer Child endpoints:
    path('child/', farmer_child_view, name='child-list'),  # GET: List all children; POST: Create a new child.
    path('child/<int:child_id>/', farmer_child_view, name='child-detail'),  # GET: Retrieve, PUT: Update, DELETE: Delete a specific child.
    
    path('consent-location/', ConsentLocationView.as_view(), name='consent-location-list'),
    path('consent-location/<int:consent_id>/', ConsentLocationView.as_view(), name='consent-location-detail'),
    
     # List all farmer identification records or create a new one
    path('farmer-identification/', farmer_identification_view, name='farmer-identification-list'),
    # Retrieve, update, or delete a specific farmer identification record
    path('farmer-identification/<int:pk>/', farmer_identification_view, name='farmer-identification-detail'),
    
     # List all owner identification records or create a new one
    path('owner-identification/', owner_identification_view, name='owner-identification-list'),
    # Retrieve, update, or delete a specific owner identification record by its pk
    path('owner-identification/<int:pk>/', owner_identification_view, name='owner-identification-detail'),
    
    # List all worker records or create a new one
    path('workers-in-farm/', workers_in_farm_view, name='workers-in-farm-list'),
    # Retrieve, update, or delete a specific worker record by its pk
    path('workers-in-farm/<int:pk>/', workers_in_farm_view, name='workers-in-farm-detail'),
    
     # Endpoints for AdultInHouseholdTbl
    path('adult-in-household/', adult_in_household_view, name='adult-in-household-list'),
    path('adult-in-household/<int:id>/', adult_in_household_view, name='adult-in-household-detail'),

    # Endpoints for AdultHouseholdMember
    path('adult-household-member/', adult_household_member_view, name='adult-household-member-list'),
    path('adult-household-member/<int:id>/', adult_household_member_view, name='adult-household-member-detail'),
    
     # Endpoints for ChildrenInHouseholdTbl (overall children record)
    path('children-in-household/', children_in_household_view, name='children-in-household-list'),
    path('children-in-household/<int:id>/', children_in_household_view, name='children-in-household-detail'),
    
    # Endpoints for ChildInHouseholdTbl (individual child record)
    path('child-in-household/', child_in_household_view, name='child-in-household-list'),
    path('child-in-household/<int:id>/', child_in_household_view, name='child-in-household-detail'),
    
    # URL for listing all records or creating a new record
    path('child-education-details/', ChildEducationDetailsView.as_view(), name='child_education_details_list'),
    # URL for retrieving, updating, or deleting a specific record
    path('child-education-details/<int:id>/', ChildEducationDetailsView.as_view(), name='child_education_details_detail'),
    
     # Child Remediation endpoints
    path('child-remediation/', ChildRemediationView.as_view(), name='child_remediation_list'),
    path('child-remediation/<int:remediation_id>/', ChildRemediationView.as_view(), name='child_remediation_detail'),

    # Household Sensitization endpoints
    path('household-sensitization/', HouseholdSensitizationView.as_view(), name='household_sensitization_list'),
    path('household-sensitization/<int:sensitization_id>/', HouseholdSensitizationView.as_view(), name='household_sensitization_detail'),

    # End of Collection endpoints
    path('end-of-collection/', EndOfCollectionView.as_view(), name='end_of_collection_list'),
    path('end-of-collection/<int:id>/', EndOfCollectionView.as_view(), name='end_of_collection_detail'),
]
