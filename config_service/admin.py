from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db import models
from django.forms import Textarea

from config_service.models import Configuration, SecurityCredential, CustomUser

admin.site.register(CustomUser, UserAdmin)


class SecurityCredentialInline(admin.TabularInline):
    extra = 1
    model = SecurityCredential
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 1, 'cols': 40})},
    }
    readonly_fields = ('storage_key',)


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    list_display = ('merchant_id', 'handler_type')
    inlines = (SecurityCredentialInline,)


@admin.register(SecurityCredential)
class SecurityCredentialAdmin(admin.ModelAdmin):
    list_display = ('type',)
    readonly_fields = ('storage_key',)
