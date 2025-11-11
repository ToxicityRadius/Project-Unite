from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('about/', views.about_us, name='about_us'),
    path('purpose/', views.purpose_page, name='purpose'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('logged-in-superadmins/', views.logged_in_superadmins_view, name='logged_in_superadmins'),
    path('admin/', admin.site.urls),
    path('inventory/', include('inventory.urls')),
    path('rfid_login/', include('rfid_login.urls')),


    # Password reset
    path('accounts/password_reset/', views.password_reset_validate_email, name='password_reset'),
    path('accounts/', include('django.contrib.auth.urls')),

    path('api/signup', views.signup_api, name='api_signup'),
    path('api/login', views.login_api, name='api_login'),
    path('api/auth-status', views.auth_status_api, name='auth_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
