from django.contrib import messages
from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework.response import Response
from sentry_sdk import capture_exception

from config_service.vault_logic import delete_secret
from config_service.null_storage import NullStorage
from config_service.credential_types import BINK_PRIVATE_KEY, BINK_PUBLIC_KEY, MERCHANT_PUBLIC_KEY, COMPOUND_KEY

exposed_request = None


class CustomUser(AbstractUser):
    first_login = models.BooleanField(default=True)


class Configuration(models.Model):
    UPDATE_HANDLER = 0
    JOIN_HANDLER = 1
    VALIDATE_HANDLER = 2
    TRANSACTION_MATCHING = 3
    CHECK_MEMBERSHIP_HANDLER = 4
    TRANSACTION_HISTORY_HANDLER = 5

    HANDLER_TYPE_CHOICES = (
        (UPDATE_HANDLER, "Update"),
        (JOIN_HANDLER, "Join"),
        (VALIDATE_HANDLER, "Validate"),
        (TRANSACTION_MATCHING, "Transaction Matching"),
        (CHECK_MEMBERSHIP_HANDLER, "Check Membership"),
        (TRANSACTION_HISTORY_HANDLER, "Transaction History"),
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
        (CRITICAL_LOG_LEVEL, "Critical"),
    )

    merchant_id = models.CharField(verbose_name="Merchant Slug", max_length=64)
    merchant_url = models.CharField(max_length=256)
    handler_type = models.IntegerField(choices=HANDLER_TYPE_CHOICES)
    integration_service = models.IntegerField(choices=INTEGRATION_CHOICES)
    callback_url = models.CharField(max_length=256, blank=True, null=True)
    retry_limit = models.IntegerField(default=0)
    log_level = models.IntegerField(choices=LOG_LEVEL_CHOICES, default=DEBUG_LOG_LEVEL)
    country = models.CharField(max_length=128, default="GB")

    class Meta:
        unique_together = ("merchant_id", "handler_type")


class SecurityCredential(models.Model):
    SECURITY_CRED_TYPE_CHOICES = (
        (BINK_PRIVATE_KEY, "Bink private key"),
        (BINK_PUBLIC_KEY, "Bink public key"),
        (MERCHANT_PUBLIC_KEY, "Merchant public key"),
        (COMPOUND_KEY, "Compound key"),
    )

    type = models.CharField(max_length=32, choices=SECURITY_CRED_TYPE_CHOICES)
    key_to_store = models.FileField(blank=True, storage=NullStorage())
    storage_key = models.TextField(blank=True)
    security_service = models.ForeignKey("SecurityService", on_delete=models.CASCADE)

    def __str__(self):
        return "{}".format(self.type)

    def delete(self, *args, **kwargs):
        if isinstance(self.storage_key, str):
            try:
                # storage_key is the secret name
                deleted_secret = delete_secret(self.storage_key)
                messages.set_level(exposed_request, messages.INFO)
                messages.info(exposed_request, f"Secret deleted: {deleted_secret.name}")
            except Exception as e:
                capture_exception(e)
                messages.set_level(exposed_request, messages.ERROR)
                messages.error(exposed_request, "Unable to delete the secret.")
                return Response(status=503, data="Resource not found")

        super(SecurityCredential, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.storage_key = self.get_storage_key(exposed_request)
        error_message = "File not saved, please check a file is selected and all fields are populated"

        if self.storage_key == "Service unavailable":
            messages.set_level(exposed_request, messages.ERROR)
            messages.error(exposed_request, "Can not connect to the vault! The file has not been saved.")

        elif not self.storage_key:
            messages.set_level(exposed_request, messages.ERROR)
            messages.error(exposed_request, error_message)
            self.storage_key = error_message

        super().save(*args, **kwargs)

    @staticmethod
    def get_storage_key(request):
        return request.session.get("storage_key")


class SecurityService(models.Model):
    RSA_SECURITY = 0
    OPEN_AUTH_SECURITY = 1
    OAUTH_SECURITY = 2
    PGP_SECURITY = 3

    SECURITY_TYPE_CHOICES = (
        (RSA_SECURITY, "RSA"),
        (OPEN_AUTH_SECURITY, "Open Auth (No Authentication)"),
        (OAUTH_SECURITY, "OAuth"),
        (PGP_SECURITY, "PGP"),
    )

    INBOUND_REQUEST = "INBOUND"
    OUTBOUND_REQUEST = "OUTBOUND"

    REQUEST_TYPE_CHOICES = ((INBOUND_REQUEST, "Inbound"), (OUTBOUND_REQUEST, "Outbound"))

    request_type = models.CharField(max_length=16, choices=REQUEST_TYPE_CHOICES)
    type = models.IntegerField(choices=SECURITY_TYPE_CHOICES)
    configuration = models.ForeignKey(Configuration, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("request_type", "configuration")

    def __str__(self):
        return "{} {}".format(self.type, self.request_type)
