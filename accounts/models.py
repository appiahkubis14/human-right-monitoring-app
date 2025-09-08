from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Extended user model with additional fields for all user types.
    """
    class UserType(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        STAFF = 'STAFF', _('Staff')

    email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.ADMIN)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Additional common fields for all users
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_('The groups this user belongs to. A user will get all permissions granted to each of their groups.'),
        related_name="customuser_set",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="customuser",
    )
    
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']
    
    def __str__(self):
        return f"{self.email or self.phone_number} ({self.get_user_type_display()})"