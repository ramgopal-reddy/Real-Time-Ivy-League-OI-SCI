from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from .models import Student

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        domain = request.POST.get('domain')
        sub_domain = request.POST.get('sub_domain', '')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
        
        user = User.objects.create_user(username=username, password=password, email=email)
        student = Student.objects.create(user=user, domain=domain, sub_domain=sub_domain)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    
    return render(request, 'login.html')

@login_required
def dashboard(request):
    try:
        student = request.user.student
        # Get opportunities from backend API
        response = requests.get('https://real-time-ivy-league-oi-sci.onrender.com/opportunities')
        if response.status_code == 200:
            all_opportunities = response.json()
            # Filter opportunities based on student's domain
            matched_opportunities = []
            for opp in all_opportunities:
                if (student.domain.lower() in opp.get('domain', '').lower() or 
                    student.domain.lower() in opp.get('sub_domain', '').lower() or
                    student.domain.lower() in opp.get('title', '').lower()):
                    matched_opportunities.append(opp)
            
            context = {
                'student': student,
                'opportunities': matched_opportunities[:5],  # Show latest 5
                'total_opportunities': len(matched_opportunities)
            }
        else:
            context = {
                'student': student,
                'opportunities': [],
                'total_opportunities': 0
            }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')
    
    return render(request, 'dashboard.html', context)

@login_required
def all_opportunities_unfiltered(request):
    try:
        student = request.user.student
        # Get all opportunities from backend API without filtering
        response = requests.get('https://real-time-ivy-league-oi-sci.onrender.com/opportunities')
        if response.status_code == 200:
            all_opportunities = response.json()
            
            context = {
                'student': student,
                'opportunities': all_opportunities,
                'total_count': len(all_opportunities)
            }
        else:
            context = {
                'student': student,
                'opportunities': [],
                'total_count': 0
            }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')
    
    return render(request, 'all_opportunities.html', context)

@login_required
def all_opportunities(request):
    try:
        student = request.user.student
        # Get opportunities from backend API
        response = requests.get('https://real-time-ivy-league-oi-sci.onrender.com/opportunities')
        if response.status_code == 200:
            all_opportunities = response.json()
            # Filter opportunities based on student's domain
            matched_opportunities = []
            for opp in all_opportunities:
                if (student.domain.lower() in opp.get('domain', '').lower() or 
                    student.domain.lower() in opp.get('sub_domain', '').lower() or
                    student.domain.lower() in opp.get('title', '').lower()):
                    matched_opportunities.append(opp)
            
            context = {
                'student': student,
                'opportunities': matched_opportunities
            }
        else:
            context = {
                'student': student,
                'opportunities': []
            }
    except Student.DoesNotExist:
        messages.error(request, 'Student profile not found')
        return redirect('login')
    
    return render(request, 'opportunities.html', context)
