import hashlib

from django.db import models
from django.contrib.auth.models import AbstractUser


def read_file_contents(value):
    contents = value.read()
    return contents


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
    key_to_store = models.FileField(validators=[read_file_contents], blank=True)
    storage_key = models.TextField(blank=True)
    security_service = models.ForeignKey('SecurityService', on_delete=models.CASCADE)

    def __str__(self):
        return '{}'.format(self.type)

    def save(self, *args, **kwargs):
        hashed_storage_key = hashlib.sha256(
            "{}.{}.{}".format(
                self.type, self.security_service.type, self.security_service.configuration.merchant_id
            ).encode()
        )
        self.storage_key = hashed_storage_key.hexdigest()
        super().save(*args, **kwargs)


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
