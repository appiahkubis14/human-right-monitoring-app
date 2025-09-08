from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='dashboard'),
    path('all-farmers/', farmer, name='all-farmers'),
    path('farmer-children/', farmer_children, name='add-farmer'),
    path('risk-assessment/', risk_assessment, name='farmer-identification'),
    path('communities/', community, name='communities'),

    path('notification/', notifications, name='notification'),
    path('profile-settings/', settings, name='profile-settings'),
 
]


# <div class="page-content">
#     <div class="page-container">
        
#     </div>
# </div>