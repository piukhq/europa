import hashlib
import json

from django.test import TestCase
from django.urls import reverse

from config_service.models import Configuration, SecurityCredential
from europa.settings import SERVICE_API_KEY


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
        config = Configuration.objects.create(**self.data)
        SecurityCredential.objects.create(**self.security_creds, configuration=config)

    def test_retrieve_config_view(self):
        hashed_storage_key = hashlib.sha256("{}.{}".format(self.security_creds['type'],
                                                           self.data['merchant_id']).encode())
        storage_key = hashed_storage_key.hexdigest()
        expected_resp = {
            'id': 1,
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

        headers = {'HTTP_AUTHORIZATION': 'Token ' + SERVICE_API_KEY}

        resp = self.client.get(reverse('configuration'),
                               {'merchant_id': 'fake-merchant', 'handler_type': 0},
                               **headers)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.content.decode('utf8')), expected_resp)

    def test_incorrect_handler_returns_error_response(self):
        headers = {'HTTP_AUTHORIZATION': 'Token ' + SERVICE_API_KEY}
        resp = self.client.get(reverse('configuration'),
                               {'merchant_id': 'fake-merchant', 'handler_type': 123},
                               **headers)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content.decode('utf8'))['message'],
                         'configuration for fake-merchant using the given handler does not exist.')

    def test_missing_config_returns_error_response(self):
        headers = {'HTTP_AUTHORIZATION': 'Token ' + SERVICE_API_KEY}
        resp = self.client.get(reverse('configuration'),
                               {'merchant_id': 'fake-merchant', 'handler_type': 2},
                               **headers)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(json.loads(resp.content.decode('utf8'))['message'],
                         'configuration for fake-merchant using the given handler does not exist.')
