from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import Textarea
from django.utils.html import format_html
from nested_admin.nested import NestedModelAdmin, NestedTabularInline
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
        return format_html("<input class='button-primary' type='submit' value='Upload to Vault' />")

    upload_button.allow_tags = True


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


@admin.register(SecurityCredential)
class SecurityCredentialAdmin(admin.ModelAdmin):
    list_display = ('type',)
    readonly_fields = ('storage_key',)


@admin.register(SecurityService)
class SecurityServiceAdmin(admin.ModelAdmin):
    list_display = ('type',)
