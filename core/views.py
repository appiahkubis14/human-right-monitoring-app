from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def index(request):
    return render(request, 'core/index.html')

# @login_required
# def farmer(request):
#     return render(request, 'core/farmer-list.html')

@login_required
def farmer_children(request):
    return render(request, 'core/farmer-children-list.html')

@login_required
def risk_assessment(request):
    return render(request, 'core/risk-assessment-list.html')

@login_required
def community(request):
    return render(request, 'core/community-list.html')



