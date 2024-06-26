import hashlib
import json

import mock
from django.test import TestCase
from django.urls import reverse

from config_service.models import Configuration, SecurityCredential, SecurityService, get_changed_fields


class TestConfigService(TestCase):
    def setUp(self):
        self.data = {
            "log_level": Configuration.DEBUG_LOG_LEVEL,
            "merchant_id": "fake-merchant",
            "merchant_url": "www.fake-url.fake",
            "handler_type": Configuration.UPDATE_HANDLER,
            "retry_limit": 2,
        }

        self.config = Configuration.objects.create(**self.data)

        self.inbound_service = SecurityService.objects.create(
            request_type=SecurityService.INBOUND_REQUEST,
            type=SecurityService.RSA_SECURITY,
            configuration=self.config,
        )

        self.outbound_service = SecurityService.objects.create(
            request_type=SecurityService.OUTBOUND_REQUEST,
            type=SecurityService.RSA_SECURITY,
            configuration=self.config,
        )

        self.inbound_security_creds = {
            "type": "public_key",
            "security_service": self.inbound_service,
        }
        self.outbound_security_creds = {
            "type": "public_key",
            "security_service": self.outbound_service,
        }

        hashed_inbound_storage_key = hashlib.sha256(
            "{}.{}.{}".format(
                self.inbound_security_creds["type"],
                self.inbound_service.type,
                self.inbound_service.configuration.merchant_id,
            ).encode()
        )
        inbound_storage_key = hashed_inbound_storage_key.hexdigest()

        patcher = mock.patch("config_service.models.SecurityCredential.get_storage_key")
        self.mock_get_storage_key = patcher.start()
        self.mock_get_storage_key._mock_return_value = inbound_storage_key

        SecurityCredential.objects.create(**self.inbound_security_creds)
        SecurityCredential.objects.create(**self.outbound_security_creds)

    def test_retrieve_config_view(self):
        hashed_inbound_storage_key = hashlib.sha256(
            "{}.{}.{}".format(
                self.inbound_security_creds["type"],
                self.inbound_service.type,
                self.inbound_service.configuration.merchant_id,
            ).encode()
        )

        inbound_storage_key = hashed_inbound_storage_key.hexdigest()

        expected_resp = {
            "id": self.config.id,
            "merchant_id": "fake-merchant",
            "merchant_url": "www.fake-url.fake",
            "handler_type": 0,
            "callback_url": None,
            "retry_limit": 2,
            "log_level": 0,
            "country": "GB",
            "security_credentials": {
                "inbound": {
                    "service": self.inbound_service.type,
                    "credentials": [
                        {
                            "credential_type": self.inbound_security_creds["type"],
                            "storage_key": inbound_storage_key,
                        }
                    ],
                },
                "outbound": {
                    "service": 0,
                    "credentials": [
                        {
                            "credential_type": self.inbound_security_creds["type"],
                            "storage_key": inbound_storage_key,
                        }
                    ],
                },
            },
        }

        resp = self.client.get(
            reverse("configuration"),
            {"merchant_id": "fake-merchant", "handler_type": 0},
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode("utf8")), expected_resp)

    def test_incorrect_handler_returns_error_response(self):
        resp = self.client.get(
            reverse("configuration"),
            {"merchant_id": "fake-merchant", "handler_type": 123},
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            json.loads(resp.content.decode("utf8"))["message"],
            "configuration for fake-merchant using the given handler does not exist.",
        )

    def test_missing_config_returns_error_response(self):
        resp = self.client.get(
            reverse("configuration"),
            {"merchant_id": "fake-merchant", "handler_type": 2},
        )

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(
            json.loads(resp.content.decode("utf8"))["message"],
            "configuration for fake-merchant using the given handler does not exist.",
        )

    @mock.patch("config_service.models.get_changed_fields")
    @mock.patch("config_service.models.teams_notify")
    def test_config_change_post_to_teams_called(self, teams_mock, fields_mock):
        fields_mock.return_value = "test, test, test"
        Configuration(
            id=999,
            merchant_id="test",
            merchant_url="http://test",
            handler_type=0,
            retry_limit=0,
            log_level=0,
            country="GB",
        ).save()
        config_service = Configuration.objects.filter(id=999).first()
        config_service.merchant_id = "test str"
        config_service.save()
        teams_mock.assert_called()

    @mock.patch("config_service.models.get_changed_fields")
    @mock.patch("config_service.models.teams_notify")
    def test_config_change_post_to_teams_not_called_if_brand_new_instance(self, teams_mock, fields_mock):
        fields_mock.return_value = "test, test, test"
        Configuration(
            merchant_id="test",
            merchant_url="http://test",
            handler_type=0,
            retry_limit=0,
            log_level=0,
            country="GB",
        ).save()
        teams_mock.assert_not_called()

    def test_get_changed_fields(self):
        Configuration(
            merchant_id="test",
            merchant_url="http://test",
            handler_type=0,
            retry_limit=0,
            log_level=0,
            country="GB",
        ).save()

        instance = Configuration.objects.filter(merchant_id="test").first()
        instance.merchant_url = "http://nottest"
        assert (
            get_changed_fields(instance, Configuration) == 'merchant_url changed from "http://test" to "http://nottest"'
        )
