from rest_framework import serializers

from config_service.models import Configuration


class ConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Configuration
        fields = "__all__"
