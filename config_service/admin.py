from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html
from nested_admin.nested import NestedModelAdmin, NestedTabularInline

from config_service.models import Configuration, CustomUser, SecurityCredential, SecurityService

admin.site.register(CustomUser, UserAdmin)


class SecurityCredentialForm(forms.ModelForm):
    class Meta:
        model = SecurityCredential
        fields = "__all__"

    key_to_store = forms.FileField()


class SecurityCredentialInline(NestedTabularInline):
    extra = 1
    model = SecurityCredential
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 40})},
    }
    readonly_fields = ("storage_key", "upload_button")

    def upload_button(self, obj):
        return format_html("<input type='button' class='button-primary upload_to_vault' value='Upload to Vault' />")

    upload_button.allow_tags = True

    class Media:
        js = ("save_to_vault.js", "show_fields.js")


class SecurityServiceInline(NestedTabularInline):
    extra = 1
    model = SecurityService
    formfield_overrides = {
        models.TextField: {"widget": Textarea(attrs={"rows": 1, "cols": 40})},
    }
    inlines = [SecurityCredentialInline]


@admin.register(Configuration)
class ConfigurationAdmin(NestedModelAdmin):
    list_filter = ("merchant_id", "handler_type")
    list_display = ("merchant_id", "handler_type")
    inlines = (SecurityServiceInline,)


@admin.register(SecurityCredential)
class SecurityCredentialAdmin(admin.ModelAdmin):
    form = SecurityCredentialForm
    list_display = ("type",)
    readonly_fields = ("storage_key",)


@admin.register(SecurityService)
class SecurityServiceAdmin(admin.ModelAdmin):
    list_display = ("type",)
