import hashlib
import json

from django.test import TestCase
from django.urls import reverse

from config_service.models import Configuration, SecurityCredential


class TestConfigService(TestCase):
    def setUp(self):
        self.data = {
            'log_level': Configuration.DEBUG_LOG_LEVEL,
            'merchant_id': 'fake-merchant',
            'merchant_url': 'www.fake-url.fake',
            'security_service': Configuration.RSA_SECURITY,
            'handler_type': Configuration.UPDATE_HANDLER,
            'integration_service': Configuration.SYNC_INTEGRATION,
            'retry_limit': 2,
        }
        self.security_creds = {'type': 'public_key'}
        self.config = Configuration.objects.create(**self.data)
        SecurityCredential.objects.create(**self.security_creds, configuration=self.config)

    def test_retrieve_config_view(self):
        hashed_storage_key = hashlib.sha256("{}.{}".format(self.security_creds['type'],
                                                           self.data['merchant_id']).encode())
        storage_key = hashed_storage_key.hexdigest()
        expected_resp = {
            'id': self.config.id,
            'merchant_id': 'fake-merchant',
            'merchant_url': 'www.fake-url.fake',
            'handler_type': 0,
            'integration_service': 0,
            'callback_url': None,
            'security_service': 0,
            'retry_limit': 2,
            'log_level': 0,
            'country': 'GB',
            'security_credentials': [{'type': 'public_key', 'storage_key': storage_key}]
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
