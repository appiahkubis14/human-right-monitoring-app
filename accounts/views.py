import logging
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from accounts.models import CustomUser
from .forms import (
    LoginForm, 
    RegistrationForm, 
    PasswordResetForm, 
    SetPasswordForm,
    LockScreenForm
)

# Set up logging
logger = logging.getLogger(__name__)
class LoginView(View):
    template_name = 'auth/auth-login.html'
    form_class = LoginForm

    def get(self, request):
        logger.debug("LoginView GET request received")
        if request.user.is_authenticated:
            logger.info(f"User {request.user} already authenticated, redirecting")
            messages.info(request, "You're already logged in!")
            return redirect('dashboard')
        form = self.form_class()
        logger.debug("Rendering login form")
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        logger.debug("LoginView POST request received")
        # form = self.form_class(request.POST)
        # print(request.POST)
        data = request.POST
        print(f'data: {data}')
        
        if data:
            phone_number = data['phone_number']
            password = data['password']
            remember_me = data.get('remember_me', False)
            logger.debug(f"Attempting authentication for phone: {phone_number}")

            # print(phone_number, password, remember_me)
            
            user = authenticate(request, phone_number=phone_number, password=password)

            if user is not None:
                logger.info(f"User {user} authenticated successfully")
                login(request, user)
                
                if not remember_me:
                    logger.debug("Setting session to expire on browser close")
                    request.session.set_expiry(0)
                
                messages.success(request, f"Welcome back, {user.get_full_name() or user.phone_number}!")
                next_url = request.GET.get('next', reverse_lazy('dashboard'))
                logger.debug(f"Redirecting to: {next_url}")
                return redirect(next_url)
            else:
                logger.warning(f"Authentication failed for phone: {phone_number}")
                messages.error(request, "Invalid phone number or password. Please try again.")
       
        
        logger.debug("Re-rendering login form with errors")
        return render(request, self.template_name)
    


class RegistrationView(View):
    template_name = 'auth/auth-register.html'
    form_class = RegistrationForm

    def get(self, request):
        logger.debug("RegistrationView GET request received")
        if request.user.is_authenticated:
            logger.info(f"User {request.user} already authenticated, redirecting")
            messages.info(request, "You're already registered and logged in!")
            return redirect('login')
        form = self.form_class()
        logger.debug("Rendering registration form")
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        logger.debug("RegistrationView POST request received")
        form = self.form_class(request.POST)
        
        if form.is_valid():
            logger.debug("Form validation successful")
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            logger.info(f"New user created: {user}")
            
            # Authenticate and login the user
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password1']
            logger.debug(f"Attempting auto-login for new user: {phone_number}")
            
            user = authenticate(phone_number=phone_number, password=password)
            
            if user is not None:
                logger.info(f"Auto-login successful for new user: {user}")
                login(request, user)
                messages.success(request, "Registration successful! You're now logged in.")
                return redirect('dashboard')
            else:
                logger.error(f"Auto-login failed for new user: {phone_number}")
                messages.error(request, "Registration complete but automatic login failed. Please log in manually.")
                return redirect('login')
        else:
            logger.warning(f"Form validation failed with errors: {form.errors}")
            messages.warning(request, "Please correct the errors below.")
        
        logger.debug("Re-rendering registration form with errors")
        return render(request, self.template_name, {'form': form})

class LogoutView(View):
    print
    def get(self, request):
        logger.debug("LogoutView GET request received")
        if request.user.is_authenticated:
            logger.info(f"Logging out user: {request.user}")
            logout(request)
            messages.success(request, "You've been successfully logged out!")
            return redirect('login')
        else:
            logger.debug("Anonymous user attempted logout")
            messages.info(request, "You weren't logged in to begin with.")
        logger.debug("Redirecting to login page")
        return redirect('login')

class LockScreenView(View):
    template_name = 'auth/lock_screen.html'
    form_class = LockScreenForm

    @method_decorator(login_required)
    def get(self, request):
        logger.debug("LockScreenView GET request received")
        # Store current path for redirect after unlock
        next_url = request.GET.get('next', reverse_lazy('dashboard'))
        request.session['next'] = next_url
        logger.debug(f"Stored next URL in session: {next_url}")
        messages.info(request, "Please enter your password to unlock your session.")
        logger.debug(f"Rendering lock screen for user: {request.user}")
        return render(request, self.template_name, {'user': request.user})

    @method_decorator(login_required)
    def post(self, request):
        logger.debug("LockScreenView POST request received")
        form = self.form_class(request.POST)
        
        if form.is_valid():
            password = form.cleaned_data['password']
            logger.debug(f"Attempting unlock for user: {request.user}")
            
            user = authenticate(phone_number=request.user.phone_number, password=password)
            
            if user is not None:
                logger.info(f"Unlock successful for user: {user}")
                login(request, user)
                next_url = request.session.get('next', reverse_lazy('dashboard'))
                logger.debug(f"Redirecting to stored URL: {next_url}")
                messages.success(request, "Welcome back! Your session has been unlocked.")
                return redirect(next_url)
            else:
                logger.warning(f"Unlock failed for user: {request.user}")
                messages.error(request, "Invalid password. Please try again.")
        else:
            logger.warning(f"Lock screen form validation failed with errors: {form.errors}")
            messages.warning(request, "Please enter a valid password.")
        
        logger.debug("Re-rendering lock screen with errors")
        return render(request, self.template_name, {'form': form, 'user': request.user})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'core/auth/auth-recoverpw.html'
    form_class = PasswordResetForm
    email_template_name = 'auth/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        logger.debug("PasswordResetView form validation successful")
        email = form.cleaned_data['email']
        logger.info(f"Processing password reset for email: {email}")
        
        response = super().form_valid(form)
        messages.success(self.request, 
            "We've sent you an email with instructions to reset your password. "
            "If you don't receive it within a few minutes, check your spam folder."
        )
        logger.debug("Password reset email sent successfully")
        return response

    def form_invalid(self, form):
        logger.warning(f"PasswordResetView form validation failed with errors: {form.errors}")
        messages.error(self.request, 
            "We couldn't find an account with that email address. "
            "Please check the email and try again."
        )
        return super().form_invalid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'auth/password_reset_confirm.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        logger.debug("PasswordResetConfirmView form validation successful")
        user = form.save()
        logger.info(f"Password successfully reset for user: {user}")
        
        response = super().form_valid(form)
        messages.success(self.request, 
            "Your password has been successfully reset! "
            "You can now log in with your new password."
        )
        return response

    def form_invalid(self, form):
        logger.warning(f"PasswordResetConfirmView form validation failed with errors: {form.errors}")
        messages.error(self.request, 
            "Please correct the errors below. "
            "Make sure your passwords match and meet the requirements."
        )
        return super().form_invalid(form)

    def dispatch(self, *args, **kwargs):
        logger.debug("PasswordResetConfirmView dispatch started")
        # Check if the link is valid before showing the form
        response = super().dispatch(*args, **kwargs)
        
        if self.validlink:
            logger.debug("Password reset link is valid")
            return response
        else:
            logger.warning("Invalid or expired password reset link")
            messages.error(self.request, 
                "This password reset link is invalid or has expired. "
                "Please request a new password reset."
            )
            return redirect('password_reset')
        












#########################################################################################################
# api/views.py
import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)



@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_register(request):
    logger.debug("API registration request received")
    username = request.data.get('username')
    full_name = request.data.get('full_name')
    phone_number = request.data.get('phone_number')
    email = request.data.get('email')
    password = request.data.get('password')

    print(f'full_name: {full_name}')
    print(f'phone_number: {phone_number}')
    print(f'email: {email}')
    print(f'password: {password}')

    logger.debug(f"Attempting registration for phone: {phone_number} and email: {email} and full_name: {full_name} and password: {password}")

    logger.debug(f"Attempting registration for phone: {phone_number}")
    user = CustomUser.objects.create_user(
        username=username,
        full_name=full_name,
        phone_number=phone_number,
        email=email,
        password=password
    )
    logger.info(f"User {user} registered successfully via API")
    token, created = Token.objects.get_or_create(user=user)
    login(request, user)
    return Response({
        'token': token.key,
        'user_id': user.id,
        'phone_number': user.phone_number,
        'email': user.email,
        'full_name': user.get_full_name()
    })


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def api_login(request):
    logger.debug("API login request received")
    
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    
    if not phone_number or not password:
        logger.warning("Missing phone number or password in API login")
        return Response(
            {'error': 'Phone number and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    logger.debug(f"Attempting authentication for phone: {phone_number}")
    user = authenticate(request, phone_number=phone_number, password=password)
    
    if user is not None:
        logger.info(f"User {user} authenticated successfully via API")
        token, created = Token.objects.get_or_create(user=user)
        login(request, user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'phone_number': user.phone_number,
            'full_name': user.get_full_name()
        })
    else:
        logger.warning(f"Authentication failed for phone: {phone_number}")
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

@api_view(['POST'])
def api_logout(request):
    if request.user.is_authenticated:
        logger.info(f"Logging out user via API: {request.user}")
        # Delete the token
        Token.objects.filter(user=request.user).delete()
        logout(request)
        return Response({'success': 'Logged out successfully'})
    
    logger.debug("Anonymous user attempted API logout")
    return Response(
        {'error': 'Not logged in'},
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    logger.debug("CSRF token request received")
    return Response({'csrfToken': request.META.get('CSRF_COOKIE')})








def notifications(request):
    return render(request, 'accounts/notifications.html')


def profile_settings(request):
    return render(request, 'accounts/profile-settings.html')