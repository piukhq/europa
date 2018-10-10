import hashlib
import mock
from config_service import views
from django.test import TestCase, Client
from rest_framework.response import Response


class TestViewFunctions(TestCase):
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
    @mock.patch('config_service.views.get_file_type')
    @mock.patch('config_service.views.create_hash')
    def test_prepare_data_fits_schema(self, mock_create_hash, mock_get_file_type,
                                      mock_upload_to_vault, mock_store_key_in_session):
        mock_create_hash.return_value = 'abc'
        mock_get_file_type.return_value = True
        mock_upload_to_vault.return_value = Response(status=201)

        response = self.client.get('/form_data/', self.data)

        self.assertTrue(mock_create_hash.called)
        self.assertTrue(mock_get_file_type.called)
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
        response = views.create_hash(
            credential_type=self.data['credential_type'],
            service_type=self.data['service_type'],
            merchant_id=self.data['merchant_id']
        )
        self.assertEqual(self.storage_key, response)

    @mock.patch('config_service.views.upload_to_vault')
    @mock.patch('config_service.views.get_file_type')
    @mock.patch('config_service.views.create_hash')
    def test_store_key_in_session_when_vault_status_is_201(self, mock_create_hash,
                                                           mock_get_file_type, mock_upload_to_vault):
        mock_create_hash.return_value = self.storage_key
        mock_upload_to_vault.return_value = Response(status=201)
        self.client.get('/form_data/', self.data)
        session = self.client.session

        self.assertEqual(session["storage_key"], self.storage_key)

    def test_get_file_type_is_not_type_dict(self):
        response = views.get_file_type(self.data['file'])
        self.assertEqual(response, False)

    def test_get_file_type_is_type_dict(self):
        response = views.get_file_type('{"test": "test"}')
        self.assertEqual(response, True)
