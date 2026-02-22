from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('opportunities/', views.all_opportunities, name='all_opportunities'),
    path('all-opportunities/', views.all_opportunities_unfiltered, name='all_opportunities_unfiltered'),
]
