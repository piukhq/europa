import ast
import hashlib

import hvac
from rest_framework.response import Response
from sentry_sdk import capture_exception

import europa.settings as settings


def create_hash(credential_type, service_type, merchant_id):
    hashed_storage_key = hashlib.sha256(
        "{}.{}.{}".format(
            credential_type, service_type, merchant_id).encode()
    )
    return hashed_storage_key.hexdigest()


def store_key_in_session(request, vault_response, storage_key):
    if vault_response:
        request.session['storage_key'] = storage_key
    else:
        request.session['storage_key'] = 'Service unavailable'


def format_key(key_to_store):
    try:  # if key_to_store is a dict we know we have a compound key
        isinstance(ast.literal_eval(key_to_store), dict)
        return ast.literal_eval(key_to_store)
    except (SyntaxError, ValueError):
        return {'value': key_to_store}


def upload_to_vault(key_to_store, storage_key):
    client = connect_to_vault()

    try:  # Save to vault
        client.write('secret/data/{}'.format(storage_key), data=key_to_store)
        return True

    except Exception as e:
        capture_exception(e)
        return False


def connect_to_vault():
    client = hvac.Client(url=settings.VAULT_URL, token=settings.VAULT_TOKEN)
    return client
