from .vault_connector import connect_to_vault
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.response import Response
from sentry_sdk import capture_exception


exposed_request = None


class CustomUser(AbstractUser):
    first_login = models.BooleanField(default=True)


class Configuration(models.Model):
    UPDATE_HANDLER = 0
    JOIN_HANDLER = 1
    VALIDATE_HANDLER = 2
    TRANSACTION_MATCHING = 3

    HANDLER_TYPE_CHOICES = (
        (UPDATE_HANDLER, "Update"),
        (JOIN_HANDLER, "Join"),
        (VALIDATE_HANDLER, "Validate"),
        (TRANSACTION_MATCHING, "Transaction Matching"),
    )

    SYNC_INTEGRATION = 0
    ASYNC_INTEGRATION = 1

    INTEGRATION_CHOICES = (
        (SYNC_INTEGRATION, "Sync"),
        (ASYNC_INTEGRATION, "Async"),
    )

    DEBUG_LOG_LEVEL = 0
    INFO_LOG_LEVEL = 1
    WARNING_LOG_LEVEL = 2
    ERROR_LOG_LEVEL = 3
    CRITICAL_LOG_LEVEL = 4

    LOG_LEVEL_CHOICES = (
        (DEBUG_LOG_LEVEL, "Debug"),
        (INFO_LOG_LEVEL, "Info"),
        (WARNING_LOG_LEVEL, "Warning"),
        (ERROR_LOG_LEVEL, "Error"),
        (CRITICAL_LOG_LEVEL, "Critical")
    )

    merchant_id = models.CharField(max_length=64)
    merchant_url = models.CharField(max_length=256)
    handler_type = models.IntegerField(choices=HANDLER_TYPE_CHOICES)
    integration_service = models.IntegerField(choices=INTEGRATION_CHOICES)
    callback_url = models.CharField(max_length=256, blank=True, null=True)
    retry_limit = models.IntegerField(default=0)
    log_level = models.IntegerField(choices=LOG_LEVEL_CHOICES, default=DEBUG_LOG_LEVEL)
    country = models.CharField(max_length=128, default='GB')

    class Meta:
        unique_together = ('merchant_id', 'handler_type')


class SecurityCredential(models.Model):
    BINK_PRIVATE_KEY = "bink_private_key"
    BINK_PUBLIC_KEY = "bink_public_key"
    MERCHANT_PUBLIC_KEY = "merchant_public_key"
    COMPOUND_KEY = "compound_key"

    SECURITY_CRED_TYPE_CHOICES = (
        (BINK_PRIVATE_KEY, "Bink private key"),
        (BINK_PUBLIC_KEY, "Bink public key"),
        (MERCHANT_PUBLIC_KEY, "Merchant public key"),
        (COMPOUND_KEY, "Compound key")
    )

    type = models.CharField(max_length=32, choices=SECURITY_CRED_TYPE_CHOICES)
    key_to_store = models.FileField(upload_to='media/', blank=True)
    storage_key = models.TextField(blank=True)
    security_service = models.ForeignKey('SecurityService', on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.type)

    def delete(self, *args, **kwargs):

        try:
            client = connect_to_vault()

        except Exception as e:
            capture_exception(e)
            return Response(status=503, data='Service unavailable')

        if isinstance(self.storage_key, str):
            client.delete('secret/data/{}'.format(self.storage_key.split(' ', 1)[0]))

        super(SecurityCredential, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        key = self.get_storage_key(exposed_request)
        self.storage_key = key
        super().save(*args, **kwargs)

    @staticmethod
    def get_storage_key(request):
        return request.session.get('storage_key')


class SecurityService(models.Model):
    RSA_SECURITY = 0
    OPEN_AUTH_SECURITY = 1
    OAUTH_SECURITY = 2

    SECURITY_TYPE_CHOICES = (
        (RSA_SECURITY, "RSA"),
        (OPEN_AUTH_SECURITY, "Open Auth (No Authentication)"),
        (OAUTH_SECURITY, "OAuth"),
    )

    INBOUND_REQUEST = "INBOUND"
    OUTBOUND_REQUEST = "OUTBOUND"

    REQUEST_TYPE_CHOICES = (
        (INBOUND_REQUEST, "Inbound"),
        (OUTBOUND_REQUEST, "Outbound")
    )

    request_type = models.CharField(max_length=16, choices=REQUEST_TYPE_CHOICES)
    type = models.IntegerField(choices=SECURITY_TYPE_CHOICES)
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('request_type', 'configuration')

    def __str__(self):
        return '{} {}'.format(self.type, self.request_type)
