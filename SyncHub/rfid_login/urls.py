from django.urls import path
from . import views

app_name = 'rfid_login'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('time_log/', views.time_log_view, name='time_log'),
]
