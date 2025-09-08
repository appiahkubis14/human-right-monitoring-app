from django import forms
from django.contrib.auth.forms import (
    AuthenticationForm, 
    UserCreationForm, 
    PasswordResetForm, 
    SetPasswordForm
)
from django.core.exceptions import ValidationError
from accounts.models import CustomUser

class LoginForm(AuthenticationForm):
    phone_number = forms.CharField(
        label="Phone Number",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'required': 'required'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': 'required'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # print(phone_number, password, remember_me)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('username')  # Remove username field since we're using phone_number

class RegistrationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your phone number',
            'required': 'required'
        })
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': 'required'
        })
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password',
            'required': 'required'
        })
    )
    terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="I accept Terms and Conditions"
    )

    class Meta:
        model = CustomUser
        fields = ('phone_number', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            raise ValidationError("This phone number is already registered.")
        return phone_number

class PasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email',
            'required': 'required'
        })
    )

class SetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'required': 'required'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'required': 'required'
        })
    )

class LockScreenForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'required': 'required'
        })
    )