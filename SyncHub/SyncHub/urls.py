from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', views.login_page, name='login'),
    path('signup/', views.signup_page, name='signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls')),
    path('rfid_login/', include('rfid_login.urls')),

    # API endpoints for auth used by frontend JS
    path('api/signup', views.signup_api, name='api_signup'),
    path('api/login', views.login_page, name='api_login'),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
