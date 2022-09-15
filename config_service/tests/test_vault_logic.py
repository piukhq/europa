import hashlib

import mock
from django.test import Client, TestCase
from django.test.client import RequestFactory

from config_service import vault_logic
from config_service.credential_types import COMPOUND_KEY
from config_service.models import Configuration


class TestVaultFunctions(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            "csrfmiddlewaretoken": "test_token",
            "merchant_id": "test",
            "service_type": "test_service",
            "handler_type": Configuration.JOIN_HANDLER,
            "credential_type": "test_credential",
            "file": "test_file",
        }
        hashed_storage_key = hashlib.sha256(
            "{}.{}.{}.{}".format(
                self.data["credential_type"],
                self.data["service_type"],
                self.data["handler_type"],
                self.data["merchant_id"],
            ).encode()
        )
        self.storage_key = hashed_storage_key.hexdigest()

    # If data fits with schema the mocked methods will be called and the response will return 200
    @mock.patch("config_service.views.store_key_in_session")
    @mock.patch("config_service.views.upload_to_vault")
    @mock.patch("config_service.views.format_key")
    def test_prepare_data_fits_schema(
        self, mock_format_key, mock_upload_to_vault, mock_store_key_in_session
    ):
        mock_format_key.return_value = {"test": "test"}
        mock_upload_to_vault.return_value = True

        response = self.client.post("/config_service/form_data/", self.data)

        self.assertTrue(mock_format_key.called)
        self.assertTrue(mock_upload_to_vault.called)
        self.assertTrue(mock_store_key_in_session.called)
        self.assertEqual(response.status_code, 200)

    def test_prepare_data_does_not_fit_schema(self):
        response = self.client.get(
            "/config_service/form_data/",
            {"merchant_id": "test", "service_type": "test_service"},
        )

        error_message = response._container[0].decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            error_message, '{"error_message": "required key not provided"}'
        )

    def test_store_in_session_returns_unavailable(self):
        req = RequestFactory()
        req.session = self.client.session
        vault_logic.store_key_in_session(req, None, "key1")
        self.assertEqual(req.session["storage_key"], "Service unavailable")

    @mock.patch("config_service.views.upload_to_vault")
    def test_store_key_in_session_when_vault_status_is_201(self, mock_upload_to_vault):
        mock_upload_to_vault.return_value = True
        self.client.post("/config_service/form_data/", self.data)
        session = self.client.session

        self.assertEqual(
            session["storage_key"], "test-test-service-test-credential-join"
        )

    def test_get_file_type_is_not_type_dict(self):
        response = vault_logic.format_key(self.data["file"], "oauth")
        self.assertEqual(response, {"value": "test_file"})

    def test_get_file_type_is_type_dict(self):
        response = vault_logic.format_key({"test": "test"}, COMPOUND_KEY)
        self.assertEqual(response, {"test": "test"})

    @mock.patch("config_service.vault_logic.connect_to_vault")
    def test_upload_to_vault(self, mock_connect_to_vault):
        response = vault_logic.upload_to_vault("test_key", self.storage_key)
        self.assertTrue(mock_connect_to_vault.called)
        self.assertEqual(response, True)

    @mock.patch("config_service.vault_logic.connect_to_vault")
    def test_upload_to_vault_no_connection(self, mock_connect_to_vault):
        mock_connect_to_vault.return_value = None
        response = vault_logic.upload_to_vault("test_key", self.storage_key)
        self.assertEqual(response, False)

    @mock.patch("config_service.vault_logic.connect_to_vault")
    def test_upload_to_vault_compound_key_no_connection(self, mock_connect_to_vault):
        mock_connect_to_vault.return_value = None
        response = vault_logic.upload_to_vault("{test: test}", self.storage_key)
        self.assertEqual(response, False)
