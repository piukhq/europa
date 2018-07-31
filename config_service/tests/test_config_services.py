import hashlib
import json

from django.test import TestCase
from django.urls import reverse

from config_service.models import Configuration, SecurityCredential, SecurityService


class TestConfigService(TestCase):
    def setUp(self):
        self.data = {
            'log_level': Configuration.DEBUG_LOG_LEVEL,
            'merchant_id': 'fake-merchant',
            'merchant_url': 'www.fake-url.fake',
            'handler_type': Configuration.UPDATE_HANDLER,
            'integration_service': Configuration.SYNC_INTEGRATION,
            'retry_limit': 2,
        }

        self.config = Configuration.objects.create(**self.data)

        self.inbound_service = SecurityService.objects.create(request_type=SecurityService.INBOUND_REQUEST,
                                                              type=SecurityService.RSA_SECURITY,
                                                              configuration=self.config)

        self.outbound_service = SecurityService.objects.create(request_type=SecurityService.OUTBOUND_REQUEST,
                                                               type=SecurityService.RSA_SECURITY,
                                                               configuration=self.config)

        self.inbound_security_creds = {'type': 'public_key', 'security_service': self.inbound_service}
        self.outbound_security_creds = {'type': 'public_key', 'security_service': self.outbound_service}

        SecurityCredential.objects.create(**self.inbound_security_creds)
        SecurityCredential.objects.create(**self.outbound_security_creds)

    def test_retrieve_config_view(self):
        hashed_inbound_storage_key = hashlib.sha256(
            "{}.{}.{}".format(
                self.inbound_security_creds['type'],
                self.inbound_service.type,
                self.inbound_service.configuration.merchant_id
            ).encode()
        )

        inbound_storage_key = hashed_inbound_storage_key.hexdigest()

        hashed_outbound_storage_key = hashlib.sha256(
            "{}.{}.{}".format(
                self.inbound_security_creds['type'],
                self.inbound_service.type,
                self.inbound_service.configuration.merchant_id
            ).encode()
        )

        outbound_storage_key = hashed_outbound_storage_key.hexdigest()
        expected_resp = {
            'id': self.config.id,
            'merchant_id': 'fake-merchant',
            'merchant_url': 'www.fake-url.fake',
            'handler_type': 0,
            'integration_service': 0,
            'callback_url': None,
            'retry_limit': 2,
            'log_level': 0,
            'country': 'GB',
            'security_credentials': {'inbound': [{'service': self.inbound_service.type,
                                                  'credential_type': self.inbound_security_creds['type'],
                                                  'storage_key': inbound_storage_key}],
                                     'outbound': [{'service': self.outbound_service.type,
                                                   'credential_type': self.outbound_security_creds['type'],
                                                   'storage_key': outbound_storage_key}]}
        }

        resp = self.client.get(reverse('configuration'),
                               {'merchant_id': 'fake-merchant', 'handler_type': 0})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode('utf8')), expected_resp)

    def test_incorrect_handler_returns_error_response(self):
        resp = self.client.get(reverse('configuration'),
                               {'merchant_id': 'fake-merchant', 'handler_type': 123})

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content.decode('utf8'))['message'],
                         'configuration for fake-merchant using the given handler does not exist.')

    def test_missing_config_returns_error_response(self):
        resp = self.client.get(reverse('configuration'),
                               {'merchant_id': 'fake-merchant', 'handler_type': 2})

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content.decode('utf8'))['message'],
                         'configuration for fake-merchant using the given handler does not exist.')
