from rest_framework.response import Response
from sentry_sdk import capture_exception
import ast
import hashlib

from config_service.vault_connector import connect_to_vault


def create_hash(credential_type, service_type, merchant_id):
    hashed_storage_key = hashlib.sha256(
        "{}.{}.{}".format(
            credential_type, service_type, merchant_id).encode()
    )
    return hashed_storage_key.hexdigest()


def store_key_in_session(request, vault_response, storage_key):
    if vault_response.status_code != 201:
        request.session['storage_key'] = vault_response.data
    else:
        request.session['storage_key'] = storage_key


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
        return Response(status=201, data='Saved to vault')

    except Exception as e:
        capture_exception(e)
        return Response(status=503, data='Service unavailable')
