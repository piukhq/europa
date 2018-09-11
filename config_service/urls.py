from django.urls import path

from config_service import views

urlpatterns = [
    path('configuration', views.ConfigurationDetail.as_view(), name='configuration'),
    ]
