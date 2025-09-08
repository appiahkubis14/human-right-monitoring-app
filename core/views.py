from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'core/index.html')


def farmer(request):
    return render(request, 'core/farmer-list.html')


def farmer_children(request):
    return render(request, 'core/farmer-children-list.html')


def risk_assessment(request):
    return render(request, 'core/risk-assessment-list.html')


def community(request):
    return render(request, 'core/community-list.html')



def notifications(request):
    return render(request, 'core/notifications.html')


def settings(request):
    return render(request, 'core/profile-settings.html')