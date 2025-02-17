from django.contrib import admin
from django.urls import path, include
from Nora import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', views.login, name='login'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('Nora.urls')),  #app Nora
]