from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.item_list, name='item_list'),
    # Note: Add, edit, and delete URLs removed as per user request to consolidate to one HTML template
]
