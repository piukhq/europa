from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
from .models import SecurityCredential
from config_service.forms import SecurityCredentialForm
from config_service.models import Configuration, SecurityCredential, CustomUser, SecurityService

admin.site.register(CustomUser, UserAdmin)


class SecurityCredentialInline(NestedTabularInline):
    extra = 1
    model = SecurityCredential
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    readonly_fields = ('storage_key', 'upload_button')

    def upload_button(self, obj):
        return format_html(
            "<input id='upload_to_vault' class='button-primary select' type='submit' value='Upload to Vault' />"
        )

    upload_button.allow_tags = True

    class Media:
        js = ('show_fields.js', 'save_to_vault.js')


class SecurityServiceInline(NestedTabularInline):
    extra = 1
    model = SecurityService
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    inlines = [SecurityCredentialInline]


@admin.register(Configuration)
class ConfigurationAdmin(NestedModelAdmin):
    list_display = ('merchant_id', 'handler_type')
    inlines = (SecurityServiceInline,)

    # def save_formset(self, request, form, formset, change):
    #     # instances = formset.save(commit=False)
    #     file_string = form.data['securityservice_set-0-securitycredential_set-0-key_to_store']
    #     file = SecurityCredential(key_to_store=file_string)
    #     pass
    #
    # def save_model(self, request, obj, form, change):
    #     instances = form.save(commit=False)
    #     pass


@admin.register(SecurityCredential)
class SecurityCredentialAdmin(admin.ModelAdmin):
    form = SecurityCredentialForm
    list_display = ('type',)
    readonly_fields = ('storage_key',)


@admin.register(SecurityService)
class SecurityServiceAdmin(admin.ModelAdmin):
    list_display = ('type',)
