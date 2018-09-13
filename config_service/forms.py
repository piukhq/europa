from django import forms

from config_service.models import SecurityCredential


class SecurityCredentialForm(forms.ModelForm):
    class Meta:
        model = SecurityCredential
        fields = '__all__'

    key_to_store = forms.FileField()

