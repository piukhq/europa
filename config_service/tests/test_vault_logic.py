import hashlib
import mock
from config_service import vault_logic
from django.test import TestCase, Client
from rest_framework.response import Response


class TestVaultFunctions(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            'merchant_id': 'test',
            'service_type': 'test_service',
            'credential_type': 'test_credential',
            'file': 'test_file'
        }
        hashed_storage_key = hashlib.sha256(
            "{}.{}.{}".format(
                self.data['credential_type'],
                self.data['service_type'],
                self.data['merchant_id']
            ).encode())
        self.storage_key = hashed_storage_key.hexdigest()

    # If data fits with schema the mocked methods will be called and the response will return 200
    @mock.patch('config_service.views.store_key_in_session')
    @mock.patch('config_service.views.upload_to_vault')
    @mock.patch('config_service.views.format_key')
    @mock.patch('config_service.views.create_hash')
    def test_prepare_data_fits_schema(self, mock_create_hash, mock_format_key,
                                      mock_upload_to_vault, mock_store_key_in_session):
        mock_create_hash.return_value = 'abc'
        mock_format_key.return_value = True
        mock_upload_to_vault.return_value = Response(status=201)

        response = self.client.get('/form_data/', self.data)

        self.assertTrue(mock_create_hash.called)
        self.assertTrue(mock_format_key.called)
        self.assertTrue(mock_upload_to_vault.called)
        self.assertTrue(mock_store_key_in_session.called)
        self.assertEqual(response.status_code, 200)

    def test_prepare_data_does_not_fit_schema(self):
        response = self.client.get('/form_data/', {
            'merchant_id': 'test',
            'service_type': 'test_service',
        })

        error_message = response._container[0].decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(error_message, '{"error_message": "required key not provided"}')

    def test_correct_hash_is_created(self):
        response = vault_logic.create_hash(
            credential_type=self.data['credential_type'],
            service_type=self.data['service_type'],
            merchant_id=self.data['merchant_id']
        )
        self.assertEqual(self.storage_key, response)

    @mock.patch('config_service.views.upload_to_vault')
    @mock.patch('config_service.views.format_key')
    @mock.patch('config_service.views.create_hash')
    def test_store_key_in_session_when_vault_status_is_201(self, mock_create_hash,
                                                           mock_format_key, mock_upload_to_vault):
        mock_create_hash.return_value = self.storage_key
        mock_upload_to_vault.return_value = Response(status=201)
        self.client.get('/form_data/', self.data)
        session = self.client.session

        self.assertEqual(session["storage_key"], self.storage_key)

    def test_get_file_type_is_not_type_dict(self):
        response = vault_logic.format_key(self.data['file'])
        self.assertEqual(response, {"value": "test_file"})

    def test_get_file_type_is_type_dict(self):
        response = vault_logic.format_key('{"test": "test"}')
        self.assertEqual(response, {'test': 'test'})

    @mock.patch('config_service.vault_logic.connect_to_vault')
    def test_upload_to_vault(self, mock_connect_to_vault):
        response = vault_logic.upload_to_vault('test_key', self.storage_key)
        self.assertTrue(mock_connect_to_vault.called)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data, 'Saved to vault')

    def test_upload_to_vault_no_connection(self):
        response = vault_logic.upload_to_vault('test_key', self.storage_key)
        self.assertEqual(response.data, 'Service unavailable')
        self.assertEqual(response.status_code, 503)

    def test_upload_to_vault_compound_key_no_connection(self):
        response = vault_logic.upload_to_vault('{test: test}', self.storage_key)
        self.assertEqual(response.data, 'Service unavailable')
        self.assertEqual(response.status_code, 503)
