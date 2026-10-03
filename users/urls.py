from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('create-admin/', views.create_admin),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('detect/', views.detect_animal, name='detect'),
    path('api/detect/', views.detect_api, name='detect_api'),
    path('history/', views.history, name='history'),
    path('test-email/', views.test_email, name='test_email'),
    
]
