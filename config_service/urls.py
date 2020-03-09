from django.urls import path

from config_service import views

urlpatterns = [
    path("configuration", views.ConfigurationDetail.as_view(), name="configuration"),
    path("form_data/", views.prepare_data, name="prepare_data"),
]
