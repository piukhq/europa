from datetime import datetime

from azure.core.exceptions import AzureError, ResourceNotFoundError, ServiceRequestError
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from sentry_sdk import capture_exception

import europa.settings as settings
from config_service.credential_types import COMPOUND_KEY


def store_key_in_session(request, vault_response, storage_key):
    if vault_response:
        request.session["storage_key"] = storage_key
    else:
        request.session["storage_key"] = "Service unavailable"


def format_key(key_to_store, credential_type):
    if credential_type == COMPOUND_KEY:
        return key_to_store
    else:
        return {"value": key_to_store}


def upload_to_vault(key_to_store, storage_key):
    client = connect_to_vault()
    try:  # Save to vault. storage_key is the secret name
        years = 50
        date_now = datetime.utcnow()
        try:
            expiry_date = date_now.replace(year=date_now.year + years)
        except ValueError:
            expiry_date = date_now.replace(year=date_now.year + years, day=28)
        client.set_secret(storage_key, key_to_store, expires_on=expiry_date)
        return True

    except (ServiceRequestError, AzureError) as e:
        capture_exception(e)
        return False
    except Exception as e:
        capture_exception(e)
        return False


def get_secret(self, secret_name: str):
    client = connect_to_vault()

    try:
        return client.get_secret(secret_name).value
    except ResourceNotFoundError:
        return None


def delete_secret(secret_name: str):
    client = connect_to_vault()

    try:
        poller = client.begin_delete_secret(secret_name)
        deleted_secret = poller.result()
        poller.wait()
        return deleted_secret
    except ResourceNotFoundError:
        return None


def connect_to_vault():
    if settings.KEYVAULT_URI is None:
        raise Exception("Vault Error: settings.KEYVAULT_URI not set")

    kv_credential = DefaultAzureCredential()

    return SecretClient(vault_url=settings.KEYVAULT_URI, credential=kv_credential)
