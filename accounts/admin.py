from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Fields to display in the list view
    list_display = [
        'username', 
        'email', 
        'phone_number', 
        'full_name',
        'user_type', 
        'is_verified', 
        'is_active', 
        'date_joined'
    ]
    
    # Fields to filter by in the sidebar
    list_filter = [
        'user_type', 
        'is_verified', 
        'is_active', 
        'is_staff', 
        'date_joined'
    ]
    
    # Fields to search by
    search_fields = [
        'username', 
        'email', 
        'phone_number', 
        'full_name'
    ]
    
    # Ordering
    ordering = ['-date_joined']
    
    # Fieldsets for the add/edit form
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {
            'fields': (
                'full_name', 
                'email', 
                'phone_number',
                'profile_picture'
            )
        }),
        (_('Address Information'), {
            'fields': (
                'address',
                'city',
                'state',
                'country',
                'postal_code'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'user_type',
                'is_verified',
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    # Fieldsets for the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'phone_number',
                'full_name',
                'password1',
                'password2',
                'user_type',
                'is_verified',
                'is_active',
                'is_staff'
            )}
        ),
    )
    
    # Read-only fields
    readonly_fields = ['date_joined', 'last_updated', 'last_login']