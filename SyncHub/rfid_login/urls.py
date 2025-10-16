from django.urls import path
from django.urls import path
from . import views

app_name = 'rfid_login'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('time_log/', views.time_log_view, name='time_log'),
    path('officers/', views.officer_list, name='officer_list'),
    path('officers/add/', views.officer_add, name='officer_add'),
    path('officers/<int:pk>/edit/', views.officer_edit, name='officer_edit'),
    path('officers/<int:pk>/delete/', views.officer_delete, name='officer_delete'),
]
