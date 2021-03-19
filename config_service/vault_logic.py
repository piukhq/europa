import ast
import hashlib
import json

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.core.exceptions import ServiceRequestError, ResourceNotFoundError, AzureError
from sentry_sdk import capture_exception

import europa.settings as settings


def create_hash(credential_type, service_type, handler_type, merchant_id):
    hashed_storage_key = hashlib.sha256(
        "{}.{}.{}.{}".format(credential_type, service_type, handler_type, merchant_id).encode()
    )
    return hashed_storage_key.hexdigest()


def store_key_in_session(request, vault_response, storage_key):
    if vault_response:
        request.session["storage_key"] = storage_key
    else:
        request.session["storage_key"] = "Service unavailable"


def format_key(key_to_store):
    try:  # if key_to_store is a dict we know we have a compound key
        isinstance(ast.literal_eval(key_to_store), dict)
        return ast.literal_eval(key_to_store)
    except (SyntaxError, ValueError):
        return {"value": key_to_store}


def upload_to_vault(key_to_store, storage_key):
    client = connect_to_vault()

    try:  # Save to vault
        client.set_secret(storage_key, key_to_store)
        return True

    except (ServiceRequestError, AzureError) as e:
        capture_exception(e)
        return False
    except Exception as e:
        capture_exception(e)
        return False


def get_secret(self, secret_name: str, original_name: str):
    client = connect_to_vault()

    try:
        return json.loads(client.get_secret(secret_name).value)
    except ResourceNotFoundError:
        return None


def connect_to_vault():
    if settings.KEYVAULT_URI is None:
        raise Exception("Vault Error: settings.KEYVAULT_URI not set")

    kv_credential = DefaultAzureCredential()

    return SecretClient(vault_url=settings.KEYVAULT_URI, credential=kv_credential)
